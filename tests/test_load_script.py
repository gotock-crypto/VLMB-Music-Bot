import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_queue_load_smoke():
    p=subprocess.run([sys.executable, str(ROOT/'scripts/load_test_queue.py'), '--jobs','20','--concurrency','4','--work-ms','1'], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout+p.stderr
