from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def test_config_has_no_hardcoded_runtime_secrets():
    text = (ROOT / "config.py").read_text()
    assert not re.search(r"[0-9]{5,}:[A-Za-z0-9_-]{20,}", text)
    assert "TELEGRAM_BOT_TOKEN = _env(\"TELEGRAM_BOT_TOKEN\", \"\").strip()" in text
    assert "YANDEX_TOKEN = _env(\"YANDEX_TOKEN\", \"\").strip()" in text
    assert "LASTFM_API_KEY = _env(\"LASTFM_API_KEY\", \"\").strip()" in text
