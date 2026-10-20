import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "migrate_sqlite_to_postgres.py"
SPEC = importlib.util.spec_from_file_location("migrate_sqlite_to_postgres", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_pg_ddl_converts_autoincrement_and_sqlite_types():
    ddl = MODULE.pg_ddl(
        "CREATE TABLE sample (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_id INTEGER PRIMARY KEY, ratio REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    assert "id BIGSERIAL PRIMARY KEY" in ddl
    assert "user_id BIGINT PRIMARY KEY" in ddl
    assert "ratio DOUBLE PRECISION" in ddl
    assert "created_at TEXT DEFAULT (CURRENT_TIMESTAMP::text)" in ddl


def test_env_file_parser_dependency_is_imported():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "import shlex" in source
