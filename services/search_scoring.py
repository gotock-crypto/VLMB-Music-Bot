"""Search ranking logic shared by the bot and unit tests.

Behavior intentionally matches the production ranking rule that existed before
this refactor: exact performer match, performer prefix, performer substring,
then original order. No quality thresholds or source filtering are added here.
"""

import re
from typing import Any, Dict, Iterable, List


def normalize_text(value: str) -> str:
    value = (value or "").casefold().replace("ё", "е")
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value, flags=re.UNICODE).strip()


def artist_query(query: str) -> str:
    q = re.sub(r"\s+", " ", (query or "").strip())
    for separator in (" - ", " — ", " – "):
        if separator in q:
            left = q.split(separator, 1)[0].strip()
            if left:
                return left
    return q


def rank_tracks_by_artist(tracks: Iterable[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    items = list(tracks or [])
    artist_q = normalize_text(artist_query(query))
    if not artist_q:
        return items

    def key(item: Dict[str, Any]) -> int:
        artist = normalize_text((item or {}).get("artist", ""))
        if artist == artist_q:
            return 0
        if artist.startswith(artist_q + " ") or artist.startswith(artist_q + ","):
            return 1
        if artist_q in artist:
            return 2
        return 3

    return sorted(items, key=key)
