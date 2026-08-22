"""Unified provider adapter contract."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Iterable, Optional
from domain.models import DownloadResult, Track

class MusicProviderAdapter(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def download(self, track: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "available": True}

class CallableProviderAdapter(MusicProviderAdapter):
    """Adapter for existing manager methods during the migration period."""
    def __init__(self, name: str, *, search: Optional[Callable[..., Awaitable[Any]]] = None,
                 download: Optional[Callable[..., Awaitable[Any]]] = None,
                 health: Optional[Callable[..., Awaitable[dict[str, Any]]]] = None):
        self.name = name
        self._search = search
        self._download = download
        self._health = health

    async def search(self, query: str, **kwargs: Any) -> Any:
        if self._search is None:
            raise NotImplementedError(f"{self.name}.search adapter is not configured")
        return await self._search(query, **kwargs)

    async def download(self, track: Any, **kwargs: Any) -> Any:
        if self._download is None:
            raise NotImplementedError(f"{self.name}.download adapter is not configured")
        return await self._download(track, **kwargs)

    async def health(self) -> dict[str, Any]:
        if self._health is not None:
            return await self._health()
        return await super().health()
