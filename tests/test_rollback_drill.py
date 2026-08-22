import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_rollback_drill_simulation():
    p=subprocess.run([sys.executable, str(ROOT/'scripts/rollback_drill.py')], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout+p.stderr
    assert 'PASS' in p.stdout
