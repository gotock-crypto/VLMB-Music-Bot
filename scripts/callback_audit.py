#!/usr/bin/env python3
"""Fail CI when callback_data literals/f-string prefixes drift outside the catalog."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from application.callbacks.audit import audit_callbacks
core = ROOT / "music_bot_user_mixes.py"
issues = audit_callbacks(core)
if issues:
    for issue in issues:
        print(f"UNREGISTERED CALLBACK: line {issue.line}: {issue.value}")
    raise SystemExit(1)
print("Callback audit OK")
