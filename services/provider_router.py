"""Provider routing, error classification and circuit-breaker failover for VLMB."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional


class ProviderFailure(RuntimeError):
    def __init__(self, provider: str, operation: str, kind: str, message: str = ""):
        self.provider = provider
        self.operation = operation
        self.kind = kind
        super().__init__(message or f"{provider} {operation}: {kind}")


def classify_error(exc: BaseException) -> str:
    text = str(exc or "").casefold()
    name = type(exc).__name__.casefold()
    if isinstance(exc, asyncio.TimeoutError) or "timeout" in text or "timed out" in text:
        return "timeout"
    if "429" in text or "rate limit" in text or "too many requests" in text:
        return "rate_limit"
    if any(x in text for x in ("403", "401", "unauthorized", "forbidden", "token")):
        return "unauthorized"
    if any(x in text for x in ("404", "not found", "no result", "empty result")):
        return "no_result"
    if any(x in text for x in ("invalid", "bad request", "malformed")):
        return "invalid"
    if "connection" in text or "network" in text or "clienterror" in name:
        return "unavailable"
    return "failed"


@dataclass
class Circuit:
    failures: int = 0
    opened_until: float = 0.0
    last_error: str = ""
    last_kind: str = ""
    successes: int = 0

    def open(self, cooldown: float, kind: str, error: str) -> None:
        self.failures += 1
        self.last_kind = kind
        self.last_error = error[:240]
        self.opened_until = time.monotonic() + max(0.0, cooldown)

    def reset(self) -> None:
        self.failures = 0
        self.opened_until = 0.0
        self.last_error = ""
        self.last_kind = ""
        self.successes += 1

    @property
    def available(self) -> bool:
        return time.monotonic() >= self.opened_until


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    weight: int = 0


class ProviderRouter:
    """Small, dependency-free router that can wrap existing provider managers."""

    def __init__(self, *, cooldown_seconds: float = 30.0, failure_threshold: int = 2):
        self.cooldown_seconds = float(cooldown_seconds)
        self.failure_threshold = max(1, int(failure_threshold))
        self.circuits: Dict[str, Circuit] = {}
        self.last_route: Dict[str, str] = {}

    def _circuit(self, provider: str) -> Circuit:
        return self.circuits.setdefault(provider, Circuit())

    def status(self) -> Dict[str, Dict[str, Any]]:
        now = time.monotonic()
        return {
            name: {
                "available": c.available,
                "failures": c.failures,
                "successes": c.successes,
                "cooldown_remaining_s": max(0.0, c.opened_until - now),
                "last_kind": c.last_kind,
                "last_error": c.last_error,
            }
            for name, c in self.circuits.items()
        }

    async def call(self, provider: str, operation: str, fn: Callable[[], Awaitable[Any]]) -> Any:
        circuit = self._circuit(provider)
        if not circuit.available:
            if hasattr(fn, "close"):
                try:
                    fn.close()
                except Exception:
                    pass
            raise ProviderFailure(provider, operation, "circuit_open", circuit.last_error)
        try:
            result = await fn()
            if result is None or result == [] or result == {}:
                raise ProviderFailure(provider, operation, "no_result", "empty provider result")
            circuit.reset()
            self.last_route[operation] = provider
            return result
        except ProviderFailure:
            raise
        except Exception as exc:
            kind = classify_error(exc)
            circuit.last_kind = kind
            circuit.last_error = str(exc)[:240]
            if kind in {"timeout", "rate_limit", "unavailable", "failed"}:
                circuit.failures += 1
                if circuit.failures >= self.failure_threshold:
                    circuit.open(self.cooldown_seconds, kind, str(exc))
            raise ProviderFailure(provider, operation, kind, str(exc)) from exc

    async def failover(
        self,
        operation: str,
        candidates: Iterable[tuple[str, Callable[[], Awaitable[Any]]]],
        *,
        allow_empty: bool = False,
    ) -> Any:
        errors: List[ProviderFailure] = []
        for provider, fn in candidates:
            try:
                result = await self.call(provider, operation, fn)
                if allow_empty or result not in (None, [], {}):
                    return result
            except ProviderFailure as exc:
                errors.append(exc)
                continue
        if errors:
            summary = "; ".join(f"{e.provider}:{e.kind}" for e in errors)
            raise ProviderFailure("router", operation, "all_failed", summary) from errors[-1]
        return []

# ---- VLMB 4.0 adapter boundary -------------------------------------------------
# These helpers let new application code depend on the provider contract without
# forcing a flag-day rewrite of the existing call(provider, operation, fn) API.
async def _adapter_call(router: ProviderRouter, adapter, operation: str, fn):
    return await router.call(adapter.name, operation, fn)

async def adapter_failover(router: ProviderRouter, operation: str, adapters, invoke):
    """Run the same failover policy against MusicProviderAdapter instances.

    `invoke(adapter)` must return an awaitable. Keeping invocation outside the
    router makes the router independent of Telegram/provider implementations.
    """
    return await router.failover(
        operation,
        ((adapter.name, lambda adapter=adapter: invoke(adapter)) for adapter in adapters),
    )
