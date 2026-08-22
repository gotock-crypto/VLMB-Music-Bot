#!/usr/bin/env python3
"""Read-only production preflight for VLMB Music Bot."""
from __future__ import annotations

import argparse
import importlib.util
import os
import shlex
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

REQUIRED = ["TELEGRAM_BOT_TOKEN"]
OPTIONAL = ["YANDEX_TOKEN", "VK_TOKEN", "LASTFM_API_KEY", "REDIS_URL"]
DEPS = ["aiohttp", "aiosqlite", "redis", "telegram", "yt_dlp", "yandex_music", "openpyxl", "psutil"]

failed = 0


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a small dotenv-compatible file without printing secret values."""
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "A").isalnum() or key[0].isdigit():
            continue
        value = value.strip()
        try:
            # shlex handles quoted values while leaving ordinary values alone.
            parts = shlex.split(value, comments=True, posix=True)
            value = parts[0] if parts else ""
        except ValueError:
            # Fall back to the raw value; presence is all preflight needs.
            value = value.strip("'\"")
        values[key] = value
    return values


def load_environment(env_file: Path | None) -> dict[str, str]:
    env = dict(os.environ)
    if env_file and env_file.exists():
        file_values = parse_env_file(env_file)
        for key, value in file_values.items():
            env.setdefault(key, value)
    return env


def check(ok: bool, label: str, detail: str = "") -> None:
    global failed
    print(f"{'PASS' if ok else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failed += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file",
        type=Path,
        default=ROOT / ".env" if (ROOT / ".env").exists() else None,
        help="dotenv file used only for presence checks (default: production .env when present)",
    )
    args = parser.parse_args()
    env = load_environment(args.env_file)

    major, minor = sys.version_info[:2]
    check((major, minor) >= (3, 12), "Python >= 3.12", f"{major}.{minor}")

    for name in REQUIRED:
        value = env.get(name, "").strip()
        check(bool(value), f"env {name}", "set" if value else "MISSING")
    for name in OPTIONAL:
        value = env.get(name, "").strip()
        print(f"{'INFO' if value else 'WARN'}  env {name} — {'set' if value else 'empty'}")

    for dep in DEPS:
        check(importlib.util.find_spec(dep) is not None, f"dependency {dep}")

    for path in (ROOT / "music_bot_user_mixes.py", ROOT / "config.py"):
        check(path.exists(), f"file {path.name}")

    for db in (ROOT / "bot_stats.db", ROOT / "vk_tokens.db"):
        if db.exists():
            try:
                con = sqlite3.connect(str(db), timeout=20)
                result = con.execute("PRAGMA integrity_check").fetchone()[0]
                con.close()
                check(result == "ok", f"SQLite {db.name}", str(result))
            except Exception as exc:
                check(False, f"SQLite {db.name}", str(exc))
        else:
            print(f"INFO  {db.name} — not present (will be created if applicable)")

    print(f"\nPreflight {'OK' if failed == 0 else 'FAILED'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
