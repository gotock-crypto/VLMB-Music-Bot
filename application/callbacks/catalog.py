"""Callback/state contract catalog for the Telegram boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CallbackSpec:
    prefix: str
    event: str
    description: str
    state_sensitive: bool = True

# Public + administrative callback namespaces used by 3.0.6. Keeping these
# namespaces explicit makes accidental callback drift visible in CI.
_SPECS = [
    ("mix:", "mix", "mix flow"), ("digest:", "digest", "digest flow"),
    ("admin_", "admin", "admin flow"), ("tokens_menu", "tokens", "token menu"),
    ("add_token", "add_token", "add provider token"), ("refresh_tokens", "refresh_tokens", "refresh tokens"),
    ("remove_token_menu", "remove_token", "remove token menu"), ("del_token:", "remove_token", "remove token"),
    ("user_settings:", "settings", "user settings"),
    ("pldl:", "playlist_download", "playlist item"), ("plall:", "playlist_download_all", "playlist all"),
    ("noop", "noop", "noop"), ("current_page", "noop", "current page"),
    ("dlbest:", "download", "download best"), ("dlall:", "download_all", "download all"),
    ("dlall_cancel:", "download_cancel", "cancel download all"),
    ("fav_audio:", "favorite_add", "add exact UID to favorites"),
    ("fav_audio_remove:", "favorite_remove", "remove exact UID from favorites"),
    ("favtoggle:", "favorite_toggle", "toggle favorite"), ("favdl:", "download", "download favorite"),
    ("favrm:", "favorite_remove", "remove favorite"), ("histdl:", "download", "download history item"),
    ("dl:", "download", "download selected result"), ("page:", "page", "paginate"),
    ("more:", "more", "load more"), ("chart_dl:", "download", "download chart item"),
    ("charts:", "charts", "chart selection"), ("similar_search:", "search_artist", "search similar artist"),
    ("back_search:", "back", "return to search results"), ("search:", "search_artist", "search artist"),
    ("main_menu", "back", "main menu"), ("charts_menu", "charts", "charts menu"),
    ("similar_menu", "similar", "similar artists menu"), ("help_menu", "help", "help menu"),
    ("new_search", "search", "new search"), ("close_search", "back", "close search"),
]
CALLBACK_SPECS = tuple(CallbackSpec(*row) for row in _SPECS)
PREFIXES = tuple(sorted((s.prefix for s in CALLBACK_SPECS if s.prefix.endswith((':', '_'))), key=len, reverse=True))
EXACT = {s.prefix: s for s in CALLBACK_SPECS if not s.prefix.endswith((':', '_'))}
BY_PREFIX = {s.prefix: s for s in CALLBACK_SPECS}

def resolve_callback(data: str) -> Optional[CallbackSpec]:
    if data in EXACT:
        return EXACT[data]
    for prefix in PREFIXES:
        if data.startswith(prefix):
            return BY_PREFIX[prefix]
    return None
