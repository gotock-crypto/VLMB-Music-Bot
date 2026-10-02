"""Input and file safety helpers for public bot handlers."""
from __future__ import annotations

import os
import re
from urllib.parse import urlparse

ALLOWED_MEDIA_HOSTS = {"vk.com", "vk.ru", "psv4.userapi.com", "youtube.com", "www.youtube.com", "youtu.be", "music.yandex.ru"}


def safe_filename(value: str, max_length: int = 64) -> str:
    value = re.sub(r"[\x00-\x1f\x7f]", "", value or "")
    value = value.replace("/", "_").replace("\\", "_").replace("..", "_")
    value = re.sub(r"[^\w\-.() ]+", "_", value, flags=re.UNICODE).strip(" .")
    return (value or "track")[:max(8, int(max_length))]


def validate_http_url(url: str, allowed_hosts: set[str] | None = None) -> bool:
    try:
        p = urlparse((url or "").strip())
        if p.scheme not in {"http", "https"} or not p.hostname:
            return False
        hosts = allowed_hosts if allowed_hosts is not None else ALLOWED_MEDIA_HOSTS
        host = p.hostname.casefold().rstrip(".")
        return any(host == h or host.endswith("." + h) for h in hosts)
    except Exception:
        return False


def safe_path(base_dir: str, filename: str) -> str:
    base = os.path.abspath(base_dir)
    path = os.path.abspath(os.path.join(base, safe_filename(filename)))
    if os.path.commonpath([base, path]) != base:
        raise ValueError("unsafe path")
    return path
