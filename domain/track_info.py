"""Domain track model and canonical identity helpers.

This module contains no Telegram, database, or provider infrastructure.
The legacy core can import these symbols as a compatibility layer while the
4.0 architecture migration proceeds incrementally.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional


def _source_code(value: Any) -> str:
    source = str(value or "vk").strip().lower()
    if source in ("yandex", "yandex_music"):
        return "ym"
    if source in ("youtube", "youtube_music"):
        return "yt"
    return source


@dataclass
class TrackInfo:
    """Information about a track from any source.

    The dict-like methods intentionally preserve the legacy core contract so
    call sites can migrate without changing runtime behavior.
    """

    idx: int
    track_id: Any
    title: str
    artist: str
    album: str
    duration_sec: int
    source: str = "vk"
    vk_url: Optional[str] = None
    ym_download_info: Optional[Any] = None
    vk_key: Optional[str] = None
    youtube_id: Optional[str] = None
    youtube_url: Optional[str] = None
    audio_ext: Optional[str] = None
    track_obj: Optional[Any] = None
    uid: Optional[str] = None
    bitrate_kbps: Optional[int] = None

    def _compute_uid(self) -> str:
        """Return the stable UID used by routing, favorites and history."""
        try:
            if self.source == "ym" and self.track_id:
                return f"ym:{self.track_id}"
            if self.source == "vk":
                if self.vk_key:
                    return f"vk:{self.vk_key}"
                if self.track_id:
                    return f"vkid:{self.track_id}"
            if self.source == "yt":
                youtube_id = self.youtube_id or self.track_id
                if youtube_id:
                    return f"yt:{youtube_id}"
        except Exception:
            pass
        raw = f"{self.source}|{self.artist}|{self.title}|{self.duration_sec}|{self.vk_url or ''}"
        return "h:" + hashlib.md5(raw.encode("utf-8", errors="ignore")).hexdigest()

    def ensure_uid(self) -> str:
        if not self.uid:
            self.uid = self._compute_uid()
        return self.uid

    def get(self, key: str, default: Any = None) -> Any:
        if key == "url":
            value = self.youtube_url if self.source == "yt" else self.vk_url
            return value if value is not None else default
        mapping = {
            "idx": "idx",
            "track_id": "track_id",
            "title": "title",
            "artist": "artist",
            "album": "album",
            "duration": "duration_sec",
            "duration_sec": "duration_sec",
            "source": "source",
            "vk_url": "vk_url",
            "vk_key": "vk_key",
            "youtube_id": "youtube_id",
            "youtube_url": "youtube_url",
            "audio_ext": "audio_ext",
            "uid": "uid",
            "bitrate_kbps": "bitrate_kbps",
        }
        attr = mapping.get(key)
        if attr is None:
            return default
        value = getattr(self, attr, default)
        if key == "uid":
            return self.ensure_uid()
        return value if value is not None else default

    def __getitem__(self, key: str) -> Any:
        value = self.get(key, None)
        if value is None:
            raise KeyError(key)
        return value

    def to_dict(self) -> Dict[str, Any]:
        uid = self.ensure_uid()
        return {
            "idx": self.idx,
            "track_id": str(self.track_id),
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration_sec": self.duration_sec,
            "source": self.source,
            "vk_url": self.vk_url,
            "vk_key": self.vk_key,
            "youtube_id": self.youtube_id,
            "youtube_url": self.youtube_url,
            "audio_ext": self.audio_ext,
            "uid": uid,
            "bitrate_kbps": self.bitrate_kbps,
            "duration": self.duration_sec,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrackInfo":
        track = cls(
            idx=data["idx"],
            track_id=data["track_id"],
            title=data["title"],
            artist=data["artist"],
            album=data.get("album", ""),
            duration_sec=data["duration_sec"],
            source=data.get("source", "vk"),
            vk_url=data.get("vk_url"),
            vk_key=data.get("vk_key"),
            youtube_id=data.get("youtube_id"),
            youtube_url=data.get("youtube_url") or (data.get("url") if data.get("source") == "yt" else None),
            audio_ext=data.get("audio_ext"),
            uid=data.get("uid"),
            bitrate_kbps=data.get("bitrate_kbps"),
        )
        track.ensure_uid()
        return track


def track_uid_from_any(track: Any) -> str:
    """Return the canonical UID for a TrackInfo or compatible mapping."""
    if track is None:
        return ""
    if isinstance(track, TrackInfo):
        return track.ensure_uid()
    try:
        uid = track.get("uid")
        if uid:
            return str(uid)
    except Exception:
        pass
    try:
        src = _source_code(track.get("source") or "vk")
        if src == "ym" and track.get("track_id"):
            return f"ym:{track.get('track_id')}"
        if src == "vk" and track.get("vk_key"):
            return f"vk:{track.get('vk_key')}"
        if src == "yt":
            youtube_id = track.get("youtube_id") or track.get("track_id")
            if youtube_id:
                return f"yt:{youtube_id}"
    except Exception:
        pass
    try:
        raw = f"{track.get('source', '')}|{track.get('artist', '')}|{track.get('title', '')}|{track.get('duration', 0)}|{track.get('url', '')}"
    except Exception:
        raw = str(track)
    return "h:" + hashlib.md5(str(raw).encode("utf-8", errors="ignore")).hexdigest()
