"""Controlled retry classification and exponential backoff for VLMB operations."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

# Only transient failures are retryable. User/input/authorization/invalid-result
# failures must surface immediately instead of consuming worker capacity.
RETRYABLE_KINDS = frozenset({"timeout", "rate_limit", "unavailable", "failed", "temporary"})
NON_RETRYABLE_KINDS = frozenset({"unauthorized", "no_result", "invalid", "user_input", "circuit_open"})


def is_retryable(exc: BaseException) -> bool:
    """Return whether an exception represents a transient failure."""
    kind = str(getattr(exc, "kind", "") or "").casefold()
    if kind in NON_RETRYABLE_KINDS:
        return False
    if kind in RETRYABLE_KINDS:
        return True

    text = str(exc or "").casefold()
    name = type(exc).__name__.casefold()
    if isinstance(exc, asyncio.TimeoutError) or "timeout" in text or "timed out" in text:
        return True
    if "429" in text or "rate limit" in text or "too many requests" in text:
        return True
    if any(token in text for token in ("connection reset", "connection refused", "temporarily unavailable", "temporary failure", "network error")):
        return True
    if name in {"connectionerror", "timeouterror", "oserror"}:
        return True
    return False


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
) -> T:
    """Run an async operation with bounded retries and exponential backoff."""
    attempts = max(1, int(max_attempts))
    delay = max(0.0, float(base_delay))
    ceiling = max(delay, float(max_delay))

    for attempt in range(1, attempts + 1):
        try:
            return await operation()
        except Exception as exc:
            if attempt >= attempts or not is_retryable(exc):
                raise
            await asyncio.sleep(min(ceiling, delay * (2 ** (attempt - 1))))

    raise RuntimeError("retry policy exhausted unexpectedly")
