"""Offline regression tests for the SQLite-shaped PostgreSQL compatibility layer."""
import importlib.util
import sys
import types
from pathlib import Path

if "asyncpg" not in sys.modules:
    fake = types.ModuleType("asyncpg")
    fake.Connection = object
    sys.modules["asyncpg"] = fake

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vlmb_pg_adapter_test", ROOT / "storage" / "postgres.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_integer_ddl_is_widened_and_autoincrement_is_serial():
    sql = MODULE.PgConnection._translate(
        "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER PRIMARY KEY, count INTEGER)"
    )
    assert "id BIGSERIAL PRIMARY KEY" in sql
    assert "user_id BIGINT PRIMARY KEY" in sql
    assert "count BIGINT" in sql


def test_qmark_translation_skips_quoted_literals_and_comments():
    source = """SELECT ?, '?' AS literal, "?" AS ident -- ?
WHERE id = ? /* ? */"""
    expected = """SELECT $1, '?' AS literal, "?" AS ident -- ?
WHERE id = $2 /* ? */"""
    assert MODULE.PgConnection._qmark_to_dollar(source) == expected


def test_insert_or_ignore_is_generic_and_idempotent():
    sql = MODULE.PgConnection._translate(
        "INSERT OR IGNORE INTO forwarded_file_ids(file_id, added_at) VALUES(?, ?)"
    )
    assert sql == "INSERT INTO forwarded_file_ids(file_id, added_at) VALUES($1, $2) ON CONFLICT DO NOTHING"


def test_insert_or_replace_uses_known_conflict_key():
    sql = MODULE.PgConnection._translate(
        "INSERT OR REPLACE INTO user_last(user_id, uid, track_json, ts) VALUES(?,?,?,?)"
    )
    assert "ON CONFLICT (user_id) DO UPDATE SET" in sql
    assert "VALUES($1,$2,$3,$4)" in sql


def test_unknown_insert_or_replace_fails_closed():
    import pytest
    with pytest.raises(ValueError, match="no PostgreSQL conflict mapping"):
        MODULE.PgConnection._translate("INSERT OR REPLACE INTO unknown_table(id) VALUES(?)")


def test_subscription_insert_returns_lastrowid():
    import asyncio

    class FakeRecord(dict):
        pass

    class FakeTransaction:
        async def start(self):
            return None
        async def commit(self):
            return None
        async def rollback(self):
            return None

    class FakeConnection:
        def transaction(self):
            return FakeTransaction()

        async def fetch(self, query, *args):
            assert query.endswith("RETURNING id")
            assert args == (123,)
            return [FakeRecord(id=42)]

        async def execute(self, query, *args):
            raise AssertionError("RETURNING query must use fetch")

        async def close(self):
            return None

    conn = MODULE.PgConnection(FakeConnection())
    cursor = asyncio.run(
        conn.execute("INSERT INTO group_digest_subscriptions(chat_id) VALUES(?)", (123,))
    )
    assert cursor.lastrowid == 42
    assert asyncio.run(cursor.fetchone())["id"] == 42


def test_write_transaction_commits_explicitly():
    import asyncio

    class FakeTransaction:
        def __init__(self):
            self.started = self.committed = self.rolled_back = False
        async def start(self):
            self.started = True
        async def commit(self):
            self.committed = True
        async def rollback(self):
            self.rolled_back = True

    class FakeConnection:
        def __init__(self):
            self.tx = FakeTransaction()
        def transaction(self):
            return self.tx
        async def execute(self, query, *args):
            return "UPDATE 1"
        async def close(self):
            return None

    async def run():
        raw = FakeConnection()
        conn = MODULE.PgConnection(raw)
        await conn.execute("UPDATE users SET username=? WHERE user_id=?", ("a", 1))
        assert raw.tx.started
        assert not raw.tx.committed
        await conn.commit()
        assert raw.tx.committed
        assert conn._tx is None

    asyncio.run(run())


def test_uncommitted_write_rolls_back_on_close():
    import asyncio

    class FakeTransaction:
        def __init__(self):
            self.started = self.committed = self.rolled_back = False
        async def start(self):
            self.started = True
        async def commit(self):
            self.committed = True
        async def rollback(self):
            self.rolled_back = True

    class FakeConnection:
        def __init__(self):
            self.tx = FakeTransaction()
            self.closed = False
        def transaction(self):
            return self.tx
        async def execute(self, query, *args):
            return "DELETE 1"
        async def close(self):
            self.closed = True

    async def run():
        raw = FakeConnection()
        conn = MODULE.PgConnection(raw)
        await conn.execute("DELETE FROM users WHERE user_id=?", (1,))
        await conn.close()
        assert raw.tx.rolled_back
        assert raw.closed

    asyncio.run(run())
