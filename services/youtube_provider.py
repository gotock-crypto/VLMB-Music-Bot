"""YouTube/yt-dlp provider isolated from Telegram handlers.

The public YoutubeMusicManager interface matches the previous monolith.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yt_dlp  # type: ignore
    YT_DLP_AVAILABLE = True
except ImportError:
    yt_dlp = None  # type: ignore
    YT_DLP_AVAILABLE = False

import config

logger = logging.getLogger(__name__)


def _normalize_user_query(query: str) -> str:
    return re.sub(r"\s+", " ", (query or "").strip())


class _YTDLPLogger:
    @staticmethod
    def _clean(message: str) -> str:
        return re.sub(r"https?://\S+", "<url>", str(message or ""))

    def debug(self, message: str) -> None:
        if message and not str(message).startswith("[debug]"):
            logger.debug("yt-dlp: %s", self._clean(message))

    def info(self, message: str) -> None:
        logger.debug("yt-dlp: %s", self._clean(message))

    def warning(self, message: str) -> None:
        logger.warning("yt-dlp: %s", self._clean(message))

    def error(self, message: str) -> None:
        logger.error("yt-dlp: %s", self._clean(message))


class YoutubeMusicManager:
    """Bounded async wrapper around the synchronous yt-dlp API."""

    _YOUTUBE_URL_RE = re.compile(
        r"^(?:https?://)?(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)/",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        self._initialized = False
        self.executor: Optional[ThreadPoolExecutor] = None
        concurrency = max(1, min(int(getattr(config, "YOUTUBE_CONCURRENCY", 2) or 2), 8))
        self._semaphore = asyncio.Semaphore(concurrency)

    async def initialize(self) -> bool:
        if self._initialized and self.executor is not None:
            return True
        if not YT_DLP_AVAILABLE or yt_dlp is None:
            logger.warning('YouTube недоступен: установите pip install -U "yt-dlp[default]"')
            self._initialized = False
            return False
        workers = max(1, min(int(getattr(config, "YOUTUBE_CONCURRENCY", 2) or 2), 8))
        self.executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="youtube_")
        self._initialized = True
        logger.info("✅ YouTube/yt-dlp источник инициализирован")
        return True

    def _common_options(self) -> Dict[str, Any]:
        retries = max(0, min(int(getattr(config, "YOUTUBE_DOWNLOAD_RETRIES", 3) or 3), 10))
        options: Dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "logger": _YTDLPLogger(),
            "socket_timeout": float(getattr(config, "YOUTUBE_SEARCH_TIMEOUT", 15) or 15),
            "retries": retries,
            "fragment_retries": retries,
            "extractor_retries": max(0, min(int(getattr(config, "YOUTUBE_SEARCH_RETRIES", 2) or 2), 10)),
        }
        runtime = str(getattr(config, "YOUTUBE_JS_RUNTIME", "deno") or "deno").strip().lower()
        if runtime:
            runtime_path = shutil.which(runtime)
            if runtime_path:
                options["js_runtimes"] = {runtime: {"path": runtime_path}}
            else:
                logger.warning("YouTube JS runtime %s not found in PATH", runtime)

        clients = str(getattr(config, "YOUTUBE_PLAYER_CLIENTS", "tv,web_safari") or "tv,web_safari").strip()
        if clients:
            options["extractor_args"] = {"youtube": {"player_client": [x.strip() for x in clients.split(",") if x.strip()]}}

        cookie_file = str(getattr(config, "YOUTUBE_COOKIE_FILE", "") or "").strip()
        if cookie_file:
            if os.path.isfile(cookie_file):
                options["cookiefile"] = cookie_file
            else:
                logger.warning("YouTube cookie file not found: %s", cookie_file)
        return options

    @staticmethod
    def _artist_and_title(entry: Dict[str, Any]) -> Tuple[str, str]:
        raw_title = str(entry.get("track") or entry.get("title") or "Неизвестный трек").strip()
        artist = str(entry.get("artist") or entry.get("creator") or entry.get("uploader") or entry.get("channel") or "YouTube").strip()
        title = raw_title
        if not entry.get("track"):
            for separator in (" - ", " — ", " – "):
                if separator in raw_title:
                    left, right = raw_title.split(separator, 1)
                    if left.strip() and right.strip():
                        artist, title = left.strip(), right.strip()
                    break
        return artist or "YouTube", title or "Неизвестный трек"

    @staticmethod
    def _entry_to_track(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(entry, dict):
            return None
        video_id = str(entry.get("id") or "").strip()
        webpage_url = str(entry.get("webpage_url") or "").strip()
        if not webpage_url and video_id:
            webpage_url = f"https://www.youtube.com/watch?v={video_id}"
        if not webpage_url:
            raw_url = str(entry.get("url") or "").strip()
            if raw_url.startswith(("http://", "https://")):
                webpage_url = raw_url
        if not webpage_url:
            return None
        artist, title = YoutubeMusicManager._artist_and_title(entry)
        try:
            duration = max(0, int(float(entry.get("duration") or 0)))
        except (TypeError, ValueError):
            duration = 0
        return {"url": webpage_url, "youtube_url": webpage_url, "youtube_id": video_id or None,
                "track_id": video_id or webpage_url, "artist": artist, "title": title,
                "duration": duration, "source": "yt", "vk_key": None, "audio_ext": None}

    def _search_sync(self, query: str, limit: int) -> List[Dict[str, Any]]:
        if yt_dlp is None:
            return []
        options = self._common_options()
        options.update({"skip_download": True, "noplaylist": True, "extract_flat": "in_playlist", "playlistend": limit})
        target = query if self._YOUTUBE_URL_RE.match(query.strip()) else f"ytsearch{limit}:{query}"
        with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore[attr-defined]
            info = ydl.extract_info(target, download=False)
        if not info:
            return []
        entries = info.get("entries") if isinstance(info, dict) else None
        if entries is None:
            entries = [info]
        results: List[Dict[str, Any]] = []
        for entry in entries or []:
            track = self._entry_to_track(entry)
            if track is not None:
                results.append(track)
            if len(results) >= limit:
                break
        return results

    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self._initialized or not self.executor:
            return []
        query_clean = _normalize_user_query(query)
        if not query_clean:
            return []
        max_limit = max(1, int(getattr(config, "YOUTUBE_MAX_SEARCH_RESULTS", 40) or 40))
        requested = max(1, min(int(limit or 10), max_limit))
        timeout = max(3.0, float(getattr(config, "YOUTUBE_SEARCH_TIMEOUT", 15) or 15))
        loop = asyncio.get_running_loop()
        async with self._semaphore:
            try:
                task = loop.run_in_executor(self.executor, self._search_sync, query_clean, requested)
                return await asyncio.wait_for(task, timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning("YouTube search timeout (%.1fs) for %r", timeout, query_clean)
                return []
            except Exception as exc:
                logger.warning("YouTube search failed for %r: %s", query_clean, exc)
                return []

    @staticmethod
    def _resolve_ffmpeg_location() -> Optional[str]:
        configured = str(getattr(config, "YOUTUBE_FFMPEG_LOCATION", "") or "").strip()
        if configured:
            if os.path.exists(configured) or shutil.which(configured):
                return configured
            logger.warning("Configured ffmpeg location is unavailable: %s", configured)
            return None
        return shutil.which("ffmpeg")

    def _download_sync(self, track: Dict[str, Any]) -> Tuple[bytes, str]:
        temp_dir = tempfile.mkdtemp(prefix="youtube_audio_")
        try:
            return self._download_sync_in_dir(track, temp_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _download_sync_in_dir(self, track: Dict[str, Any], temp_dir: str) -> Tuple[bytes, str]:
        if yt_dlp is None:
            raise RuntimeError("yt-dlp не установлен")
        target = str(track.get("youtube_url") or track.get("url") or "").strip()
        video_id = str(track.get("youtube_id") or track.get("track_id") or "").strip()
        if not target and video_id:
            target = f"https://www.youtube.com/watch?v={video_id}"
        if not target:
            raise RuntimeError("YouTube URL недоступен")
        options = self._common_options()
        options.update({
            "format": str(getattr(config, "YOUTUBE_AUDIO_FORMAT", "bestaudio[ext=m4a]/bestaudio/best") or "bestaudio[ext=m4a]/bestaudio/best"),
            "outtmpl": os.path.join(temp_dir, "%(id)s.%(ext)s"), "noplaylist": True, "nopart": True,
            "overwrites": True, "max_filesize": int(getattr(config, "MAX_FILE_SIZE", 50 * 1024 * 1024) or 50 * 1024 * 1024),
            "socket_timeout": float(getattr(config, "YOUTUBE_DOWNLOAD_TIMEOUT", 180) or 180),
        })
        codec = str(getattr(config, "YOUTUBE_AUDIO_CODEC", "mp3") or "").strip().lower()
        ffmpeg_location = self._resolve_ffmpeg_location()
        if codec and ffmpeg_location:
            options["ffmpeg_location"] = ffmpeg_location
            options["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": codec,
                                          "preferredquality": str(getattr(config, "YOUTUBE_AUDIO_QUALITY", "192") or "192")}]
        with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore[attr-defined]
            info = ydl.extract_info(target, download=True)
            prepared = ydl.prepare_filename(info) if isinstance(info, dict) else ""
        candidates: List[Path] = []
        if prepared:
            candidates.append(Path(prepared))
            if codec and ffmpeg_location:
                candidates.append(Path(prepared).with_suffix(f".{codec}"))
        if isinstance(info, dict):
            for item in info.get("requested_downloads") or []:
                if isinstance(item, dict):
                    filepath = item.get("filepath") or item.get("filename")
                    if filepath:
                        candidates.append(Path(str(filepath)))
        candidates.extend(sorted(Path(temp_dir).glob("*"), key=lambda item: item.stat().st_mtime if item.exists() else 0, reverse=True))
        chosen: Optional[Path] = None
        for candidate in candidates:
            try:
                if candidate.is_file() and candidate.suffix.lower() not in (".part", ".ytdl", ".json"):
                    chosen = candidate
                    break
            except OSError:
                continue
        if chosen is None:
            raise RuntimeError("yt-dlp не создал аудиофайл")
        max_size = int(getattr(config, "MAX_FILE_SIZE", 50 * 1024 * 1024) or 50 * 1024 * 1024)
        size = chosen.stat().st_size
        if size <= 0:
            raise RuntimeError("YouTube вернул пустой аудиофайл")
        if size > max_size:
            raise RuntimeError(f"YouTube аудиофайл слишком большой: {size} байт")
        extension = chosen.suffix.lower().lstrip(".") or (codec if codec else "m4a")
        if not ffmpeg_location and extension not in ("mp3", "m4a", "mp4"):
            raise RuntimeError(f"YouTube вернул формат .{extension}; установите ffmpeg для конвертации в MP3")
        return chosen.read_bytes(), extension

    async def download_track_bytes(self, track: Dict[str, Any]) -> Tuple[bytes, str]:
        if not self._initialized or not self.executor:
            raise RuntimeError("YouTube источник не инициализирован")
        timeout = max(10.0, float(getattr(config, "YOUTUBE_DOWNLOAD_TIMEOUT", 180) or 180))
        loop = asyncio.get_running_loop()
        async with self._semaphore:
            task = loop.run_in_executor(self.executor, self._download_sync, dict(track))
            try:
                return await asyncio.wait_for(asyncio.shield(task), timeout=timeout)
            except asyncio.TimeoutError as exc:
                raise RuntimeError(f"Тайм-аут загрузки YouTube ({timeout:.0f} сек.)") from exc

    async def close(self) -> None:
        executor = self.executor
        self.executor = None
        self._initialized = False
        if executor is not None:
            await asyncio.to_thread(executor.shutdown, False, cancel_futures=True)
