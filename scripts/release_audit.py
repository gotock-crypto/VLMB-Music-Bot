#!/usr/bin/env python3
"""Deterministic release/security audit for VLMB source trees."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "music_bot_user_mixes.py", "config.py", "requirements.txt",
    "scripts/preflight.py", "scripts/healthcheck.py",
    "scripts/deploy_release.sh", "scripts/rollback_release.sh",
    "services/provider_health.py", "services/search_scoring.py",
    "services/provider_router.py", "services/search_engine.py",
    "services/metrics.py", "services/download_queue.py",
    "services/security.py", "services/playlist_manager.py",
    "tests/test_provider_router.py", "tests/test_search_engine.py",
    "tests/test_metrics.py", "tests/test_security.py",
    "tests/test_playlist_manager.py", ".github/workflows/ci.yml",
    "RELEASE_VERSION", "RELEASE_MANIFEST.md",
]
SECRET_PATTERNS = [
    re.compile(r"api\.telegram\.org/bot\d{5,}:[A-Za-z0-9_-]+"),
    re.compile(r"TELEGRAM_BOT_TOKEN\s*=\s*[\"']\d{5,}:[A-Za-z0-9_-]+"),
    re.compile(r"YANDEX_TOKEN\s*=\s*[\"']y0_[A-Za-z0-9_-]{20,}"),
    re.compile(r"VK_TOKEN\s*=\s*[\"'][A-Za-z0-9_-]{30,}"),
]
TEXT_EXTS = {".py", ".sh", ".md", ".txt", ".yml", ".yaml", ".json", ".service", ".example"}


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}{' — ' + detail if detail else ''}")
    if not ok:
        raise SystemExit(1)


def secret_scan() -> list[str]:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == ".env" or path.suffix not in TEXT_EXTS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(str(path.relative_to(ROOT)))
                break
    return sorted(set(hits))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="strict CI mode")
    args = parser.parse_args()

    for rel in REQUIRED:
        check((ROOT / rel).exists(), f"required file {rel}")

    hits = secret_scan()
    check(not hits, "secret scan", ", ".join(hits) if hits else "no credentials detected")

    if args.ci:
        compile_targets = ["music_bot_user_mixes.py", "config.py"] + [str(p.relative_to(ROOT)) for p in (ROOT / "services").glob("*.py")] + [str(p.relative_to(ROOT)) for p in (ROOT / "scripts").glob("*.py")]
        result = subprocess.run([sys.executable, "-m", "py_compile", *compile_targets], cwd=ROOT)
        check(result.returncode == 0, "py_compile", "passed")
        result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)
        check(result.returncode == 0, "pytest", "passed")

    print("\nRelease audit OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
