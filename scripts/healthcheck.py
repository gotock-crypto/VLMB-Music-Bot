#!/usr/bin/env python3
"""Read-only production health/security checks."""
from __future__ import annotations

import os
import re
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

fail = 0

def report(ok: bool, label: str, detail: str = ""):
    global fail
    print(f"{'PASS' if ok else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        fail += 1

report(not (ROOT / ".env").exists() or (ROOT / ".env").stat().st_mode & 0o077 == 0, ".env permissions", "0600 or stricter")

secret_re = re.compile(r"(?:api\.telegram\.org/bot|TELEGRAM_BOT_TOKEN\s*=\s*[\'"]?[0-9]{5,}:[A-Za-z0-9_-]+|YANDEX_TOKEN\s*=\s*[\'"]?y0_)")
for path in [ROOT / "config.py", ROOT / "music_bot_user_mixes.py"]:
    text = path.read_text(errors="ignore") if path.exists() else ""
    report(not secret_re.search(text), f"no hard-coded token in {path.name}")

for log in (ROOT / "bot.log", ROOT / "bot-debug.log"):
    if log.exists():
        text = log.read_text(errors="ignore")
        report(not re.search(r"api\.telegram\.org/bot[0-9]{5,}:[A-Za-z0-9_-]+", text), f"no Telegram token in {log.name}")

for db in (ROOT / "bot_stats.db", ROOT / "vk_tokens.db"):
    if db.exists():
        try:
            con = sqlite3.connect(str(db))
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            con.close()
            report(integrity == "ok", f"SQLite integrity {db.name}", integrity)
        except Exception as exc:
            report(False, f"SQLite integrity {db.name}", str(exc))

usage = shutil.disk_usage(ROOT)
free_gb = usage.free / (1024**3)
report(free_gb > 1.0, "disk free space", f"{free_gb:.2f} GiB free")

print(f"\nHealthcheck {'OK' if fail == 0 else 'FAILED'}")
raise SystemExit(1 if fail else 0)
