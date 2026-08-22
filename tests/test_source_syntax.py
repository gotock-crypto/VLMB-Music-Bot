from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[1]

def test_main_source_compiles():
    py_compile.compile(str(ROOT / "music_bot_user_mixes.py"), doraise=True)
    py_compile.compile(str(ROOT / "config.py"), doraise=True)
