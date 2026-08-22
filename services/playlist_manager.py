"""Playlist/album extraction through yt-dlp without downloading media during discovery."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

try:
    import yt_dlp
except Exception:  # pragma: no cover
    yt_dlp = None


class PlaylistManager:
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max(1, int(max_workers)))

    @staticmethod
    def _extract_sync(url: str, limit: int) -> List[Dict[str, Any]]:
        if yt_dlp is None:
            raise RuntimeError("yt-dlp недоступен")
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": False,
            "playlistend": max(1, int(limit)),
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info.get("entries") if isinstance(info, dict) else None
        if entries is None:
            entries = [info] if isinstance(info, dict) else []
        rows: List[Dict[str, Any]] = []
        for entry in entries:
            if not entry:
                continue
            vid = entry.get("id")
            webpage = entry.get("webpage_url") or (f"https://www.youtube.com/watch?v={vid}" if vid else "")
            if not webpage:
                continue
            title = str(entry.get("title") or "Unknown track").strip()
            artist = str(entry.get("artist") or entry.get("uploader") or entry.get("channel") or "YouTube").strip()
            rows.append({
                "artist": artist,
                "title": title,
                "source": "yt",
                "youtube_id": vid,
                "webpage_url": webpage,
                "url": webpage,
                "duration": int(entry.get("duration") or 0),
            })
        return rows

    async def extract(self, url: str, limit: int = 100) -> List[Dict[str, Any]]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._extract_sync, url, limit)

    async def close(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)
