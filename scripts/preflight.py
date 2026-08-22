#!/usr/bin/env python3
"""Read-only production preflight for VLMB Music Bot."""
from __future__ import annotations
import importlib.util
import os
import shutil
import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
REQUIRED = ["TELEGRAM_BOT_TOKEN"]
OPTIONAL = ["YANDEX_TOKEN", "VK_TOKEN", "LASTFM_API_KEY", "REDIS_URL"]
DEPS = ["aiohttp", "aiosqlite", "telegram", "yt_dlp", "yandex_music", "openpyxl", "psutil"]
OPTIONAL_DEPS = ["redis"]
failed = 0
def check(ok: bool, label: str, detail: str = "") -> None:
    global failed
    print(f"{'PASS' if ok else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")
    if not ok: failed += 1
major, minor = sys.version_info[:2]
check((major, minor) >= (3, 12), "Python >= 3.12", f"{major}.{minor}")
for name in REQUIRED:
    value = os.getenv(name, "").strip(); check(bool(value), f"env {name}", "set" if value else "MISSING")
for name in OPTIONAL:
    value = os.getenv(name, "").strip(); print(f"{'INFO' if value else 'WARN'}  env {name} — {'set' if value else 'empty'}")
for dep in DEPS:
    check(importlib.util.find_spec(dep) is not None, f"dependency {dep}")
for dep in OPTIONAL_DEPS:
    print(f"INFO  optional dependency {dep} — {'installed' if importlib.util.find_spec(dep) else 'not installed'}")
deno = shutil.which("deno"); node = shutil.which("node")
check(bool(deno or node), "YouTube JS runtime", "deno" if deno else ("node" if node else "MISSING (install Deno >= 2.3 or Node >= 22)"))
for path in (ROOT / "music_bot_user_mixes.py", ROOT / "config.py"):
    check(path.exists(), f"file {path.name}")
for db in (ROOT / "bot_stats.db", ROOT / "vk_tokens.db"):
    if db.exists():
        try:
            con = sqlite3.connect(str(db)); result = con.execute("PRAGMA integrity_check").fetchone()[0]; con.close()
            check(result == "ok", f"SQLite {db.name}", str(result))
        except Exception as exc: check(False, f"SQLite {db.name}", str(exc))
    else: print(f"INFO  {db.name} — not present (will be created if applicable)")
print(f"\nPreflight {'OK' if failed == 0 else 'FAILED'}")
sys.exit(1 if failed else 0)
