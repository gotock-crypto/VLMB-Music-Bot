"""High-quality music search normalization, scoring and deduplication."""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Tuple


def normalize_text(value: str) -> str:
    value = (value or "").casefold().replace("ё", "е")
    value = re.sub(r"[’'`´]", "", value)
    value = re.sub(r"[\[\]{}()]+", " ", value)
    value = re.sub(r"[^\w\s&+.-]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def _tokens(value: str) -> set[str]:
    return {x for x in re.split(r"\s+", normalize_text(value)) if x}


def split_query(query: str) -> Tuple[str, str]:
    q = normalize_text(query)
    for sep in (" - ", " — ", " – ", " —", "-"):
        if sep in q:
            a, b = q.split(sep, 1)
            if a.strip() and b.strip():
                return a.strip(), b.strip()
    return "", q


def _artist_title(item: Dict[str, Any]) -> Tuple[str, str]:
    artist = str(item.get("artist") or item.get("performer") or "")
    title = str(item.get("title") or item.get("name") or "")
    return normalize_text(artist), normalize_text(title)


def score_track(item: Dict[str, Any], query: str) -> float:
    artist, title = _artist_title(item)
    q_artist, q_title = split_query(query)
    q = normalize_text(query)
    if not artist and not title:
        return 0.0
    score = 0.0
    if q_artist:
        if artist == q_artist: score += 0.50
        elif artist.startswith(q_artist): score += 0.36
        elif q_artist in artist: score += 0.24
        else: score += 0.12 * SequenceMatcher(None, q_artist, artist).ratio()
        if q_title:
            if title == q_title: score += 0.38
            elif q_title in title: score += 0.24
            else: score += 0.12 * SequenceMatcher(None, q_title, title).ratio()
    else:
        combined = f"{artist} {title}".strip()
        score += 0.55 * SequenceMatcher(None, q, combined).ratio()
        qt = _tokens(q)
        ct = _tokens(combined)
        if qt:
            score += 0.35 * (len(qt & ct) / len(qt))
    source = str(item.get("source") or "").casefold()
    score += {"vk": 0.04, "ym": 0.03, "yt": 0.02}.get(source, 0.0)
    if item.get("duration"):
        score += 0.01
    return min(score, 1.0)


def deduplicate_tracks(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    seen: set[tuple] = set()
    for item in items:
        artist, title = _artist_title(item)
        # Cross-provider duplicates are one logical track. Prefer exact artist/title
        # matches and keep the first provider when metadata is otherwise equal.
        key = (artist, title) if (artist and title) else (str(item.get("url") or ""),)
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(item))
    return result


def rank_tracks(items: Iterable[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    enriched = []
    for idx, item in enumerate(items):
        row = dict(item)
        row["_vlmb_score"] = round(score_track(row, query), 6)
        row["_vlmb_original_index"] = idx
        enriched.append(row)
    enriched = deduplicate_tracks(enriched)
    enriched.sort(key=lambda x: (-float(x.get("_vlmb_score", 0)), int(x.get("_vlmb_original_index", 0))))
    for row in enriched:
        row.pop("_vlmb_original_index", None)
    return enriched
