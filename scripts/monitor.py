#!/usr/bin/env python3
"""Production watchdog: healthcheck + Telegram alert/recovery notification."""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

import aiohttp

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = Path(os.getenv("VLMB_STATE_DIR", "/var/lib/vlmb"))
STATE_FILE = STATE_DIR / "health-state.json"
ENV_FILE = Path(os.getenv("VLMB_ENV_FILE", str(ROOT / ".env")))


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"healthy": None, "last_alert": 0.0}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


async def send_alert(token: str, chat_ids: list[int], text: str) -> None:
    if not token or not chat_ids:
        return
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        for chat_id in chat_ids:
            try:
                await session.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})
            except Exception:
                pass


def run_healthcheck() -> tuple[bool, str]:
    proc = subprocess.run(
        [str(ROOT / "venv/bin/python3"), str(ROOT / "scripts/healthcheck.py")],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    output = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode == 0, output[-2500:]


async def main() -> int:
    env = load_env(ENV_FILE)
    healthy, details = run_healthcheck()
    state = load_state()
    previous = state.get("healthy")
    state["healthy"] = healthy
    state["checked_at"] = time.time()

    should_notify = previous is not healthy
    if should_notify:
        if healthy:
            text = "✅ VLMB: production healthcheck восстановлен."
        else:
            text = "🚨 VLMB: production healthcheck FAILED.\n\n" + details
        try:
            raw_ids = env.get("ADMIN_IDS", "").strip()
            if raw_ids:
                admin_ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip()]
            else:
                import sys
                sys.path.insert(0, str(ROOT))
                import config as runtime_config
                admin_ids = [int(x) for x in getattr(runtime_config, "ADMIN_IDS", [])]
        except Exception:
            admin_ids = []
        await send_alert(env.get("TELEGRAM_BOT_TOKEN", ""), admin_ids, text)

    save_state(state)
    print("HEALTHY" if healthy else "UNHEALTHY")
    if details:
        print(details)
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
