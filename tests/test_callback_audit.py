from pathlib import Path
from application.callbacks.audit import audit_callbacks, extract_callback_literals
from application.callbacks.catalog import resolve_callback

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "music_bot_user_mixes.py"

def test_callback_catalog_resolves_all_static_and_fstring_prefixes():
    occurrences = extract_callback_literals(CORE)
    assert occurrences
    unresolved = audit_callbacks(CORE)
    assert unresolved == [], [(x.value, x.line) for x in unresolved]

def test_callback_uid_is_never_normalized_by_catalog():
    for uid in ("vk:audio123_456", "yt:abc", "ym:987", "h:deadbeef"):
        spec = resolve_callback("fav_audio:" + uid)
        assert spec is not None
        assert spec.event == "favorite_add"
