#!/usr/bin/env python3
"""VLMB 4.0 architecture guardrails."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
required=[ROOT/'application',ROOT/'domain',ROOT/'providers',ROOT/'storage']
missing=[str(p.relative_to(ROOT)) for p in required if not p.is_dir()]
if missing:
    raise SystemExit('Missing architecture layers: '+', '.join(missing))
core=ROOT/'music_bot_user_mixes.py'
size=core.stat().st_size
max_bytes=530_000
if size > max_bytes:
    raise SystemExit(f'Core grew beyond guardrail: {size} > {max_bytes} bytes')
for path in [ROOT/'providers/base.py', ROOT/'application/state/machine.py', ROOT/'application/callbacks/catalog.py', ROOT/'storage/contracts.py']:
    if not path.exists(): raise SystemExit(f'Missing boundary: {path.relative_to(ROOT)}')
print(f'Architecture audit OK: core={size} bytes; layers=application/domain/providers/storage')
