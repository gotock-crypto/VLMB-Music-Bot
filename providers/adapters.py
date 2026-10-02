"""Named adapters for the current provider implementations."""
from __future__ import annotations
from typing import Any, Callable
from .base import CallableProviderAdapter

class YandexProviderAdapter(CallableProviderAdapter):
    def __init__(self, manager: Any):
        super().__init__("yandex", search=manager.search_tracks, download=manager.download_track_bytes)

class VKProviderAdapter(CallableProviderAdapter):
    def __init__(self, search: Callable[..., Any], download: Callable[..., Any] | None = None):
        super().__init__("vk", search=search, download=download)

class YouTubeProviderAdapter(CallableProviderAdapter):
    def __init__(self, manager: Any):
        super().__init__("youtube", search=manager.search_tracks, download=manager.download_track_bytes)
