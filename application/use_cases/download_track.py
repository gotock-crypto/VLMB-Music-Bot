"""Application use case for provider-independent track downloads."""
from __future__ import annotations

from time import monotonic
from typing import Any, Iterable

from providers.base import MusicProviderAdapter
from services.provider_health import ProviderHealth
from services.provider_router import ProviderFailure, ProviderRouter


class DownloadTrack:
    """Download a track through the provider boundary with failover."""

    def __init__(
        self,
        adapters: Iterable[MusicProviderAdapter],
        *,
        router: ProviderRouter | None = None,
        health: ProviderHealth | None = None,
    ) -> None:
        self._adapters = tuple(adapters)
        self._router = router or ProviderRouter()
        self._health = health

    async def execute(self, track: Any, **kwargs: Any) -> Any:
        if track is None:
            raise ValueError("track is required")

        failures: list[ProviderFailure] = []
        for adapter in self._adapters:
            started = monotonic()
            try:
                result = await self._router.call(
                    adapter.name,
                    "download",
                    lambda adapter=adapter: adapter.download(track, **kwargs),
                )
                if self._health is not None:
                    self._health.record_success(
                        adapter.name, "download", (monotonic() - started) * 1000, 1
                    )
                return result
            except ProviderFailure as exc:
                failures.append(exc)
                if self._health is not None:
                    self._health.record_failure(
                        adapter.name, "download", (monotonic() - started) * 1000, exc
                    )
            except Exception as exc:
                failure = ProviderFailure(adapter.name, "download", "failed", str(exc))
                failures.append(failure)
                if self._health is not None:
                    self._health.record_failure(
                        adapter.name, "download", (monotonic() - started) * 1000, failure
                    )

        summary = "; ".join(f"{item.provider}:{item.kind}" for item in failures)
        raise ProviderFailure("download", "download", "all_failed", summary) from (failures[-1] if failures else None)
