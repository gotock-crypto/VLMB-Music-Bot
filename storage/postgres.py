"""Small asyncpg adapter for the bot's legacy SQLite-shaped query interface.

All runtime persistence is PostgreSQL. The adapter only translates the existing
query surface; it does not open or fall back to local SQLite files.
"""
from __future__ import annotations

import os
import re
from typing import Any, Sequence

import asyncpg


class PgCursor:
    def __init__(self, rows=(), rowcount=0, lastrowid=None):
        self._rows = list(rows)
        self._index = 0
        self.rowcount = int(rowcount or 0)
        self.lastrowid = lastrowid

    async def fetchone(self):
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return row

    async def fetchall(self):
        rows = self._rows[self._index:]
        self._index = len(self._rows)
        return rows

    async def close(self):
        return None


class PgConnection:
    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn
        self._tx = None

    async def _begin_write_transaction(self) -> None:
        """Match aiosqlite's implicit write transaction until commit/rollback/close."""
        if self._tx is None:
            self._tx = self._conn.transaction()
            await self._tx.start()

    @staticmethod
    def _translate(sql: str) -> str | None:
        raw = sql.strip().rstrip(';')
        if not raw:
            return None
        # PRAGMA table_info is translated for schema-aware legacy code. Other
        # SQLite tuning pragmas have no PostgreSQL equivalent and are safe no-ops.
        match = re.match(r'(?is)^PRAGMA\s+table_info\((.+)\)$', raw)
        if match:
            table = match.group(1).strip().strip('\"`[]')
            return ("SELECT ordinal_position-1 AS cid, column_name AS name, data_type AS type, "
                    "CASE WHEN is_nullable='NO' THEN 1 ELSE 0 END AS notnull, "
                    "column_default AS dflt_value, CASE WHEN column_default LIKE 'nextval(%' THEN 1 ELSE 0 END AS pk "
                    "FROM information_schema.columns WHERE table_schema=current_schema() AND table_name='" + table.replace("'", "''") + "' ORDER BY ordinal_position")
        if re.match(r'(?is)^PRAGMA\s+', raw):
            return None
        # Introspection queries used by the legacy admin/reporting code.
        if 'sqlite_master' in raw and 'type=\'table\'' in raw:
            if 'name NOT LIKE' in raw:
                return "SELECT table_name AS name FROM information_schema.tables WHERE table_schema = current_schema() ORDER BY table_name"
            return "SELECT 1 FROM information_schema.tables WHERE table_schema = current_schema() AND table_name = $1"
        # Preserve the source SQL before normalizing SQLite-specific INSERT forms.
        replace_match = re.match(r'(?is)^INSERT\s+OR\s+REPLACE\s+INTO\s+([\w"]+)', raw)
        ignore_match = re.match(r'(?is)^INSERT\s+OR\s+IGNORE\s+INTO\s+([\w"]+)', raw)

        # SQLite DDL -> PostgreSQL DDL. Telegram IDs and counters may exceed int32.
        raw = re.sub(r'\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b', 'BIGSERIAL PRIMARY KEY', raw, flags=re.I)
        raw = re.sub(r'\b(id)\s+INTEGER\s+PRIMARY\s+KEY\b', r'\1 BIGSERIAL PRIMARY KEY', raw, flags=re.I)
        raw = re.sub(r'\bINTEGER\b', 'BIGINT', raw, flags=re.I)
        raw = re.sub(r'\bREAL\b', 'DOUBLE PRECISION', raw, flags=re.I)
        raw = re.sub(r'\bTIMESTAMP\b', 'TEXT', raw, flags=re.I)
        raw = re.sub(r'(?i)DEFAULT\s+CURRENT_TIMESTAMP\b', 'DEFAULT (CURRENT_TIMESTAMP::text)', raw)

        if replace_match:
            table = replace_match.group(1).strip('"').lower()
            raw = re.sub(r'(?is)^INSERT\s+OR\s+REPLACE\s+INTO', 'INSERT INTO', raw)
            if table == 'tg_audio_cache':
                raw += (' ON CONFLICT (query_key) DO UPDATE SET file_id=EXCLUDED.file_id, '
                        'artist=EXCLUDED.artist, title=EXCLUDED.title, duration=EXCLUDED.duration, '
                        'unique_id=EXCLUDED.unique_id, created_at=EXCLUDED.created_at')
            elif table == 'user_last':
                raw += ' ON CONFLICT (user_id) DO UPDATE SET uid=EXCLUDED.uid, track_json=EXCLUDED.track_json, ts=EXCLUDED.ts'
            else:
                raise ValueError(f'INSERT OR REPLACE has no PostgreSQL conflict mapping for table {table!r}')
        elif ignore_match:
            raw = re.sub(r'(?is)^INSERT\s+OR\s+IGNORE\s+INTO', 'INSERT INTO', raw)
            if 'ON CONFLICT' not in raw.upper():
                raw += ' ON CONFLICT DO NOTHING'

        return PgConnection._qmark_to_dollar(raw)

    @staticmethod
    def _qmark_to_dollar(sql: str) -> str:
        """Translate SQLite ? placeholders without touching quoted text or SQL comments."""
        out = []
        i = 0
        index = 0
        quote = None
        line_comment = False
        block_comment = False
        while i < len(sql):
            ch = sql[i]
            nxt = sql[i + 1] if i + 1 < len(sql) else ''
            if line_comment:
                out.append(ch)
                if ch == '\n':
                    line_comment = False
                i += 1
                continue
            if block_comment:
                out.append(ch)
                if ch == '*' and nxt == '/':
                    out.append(nxt)
                    i += 2
                    block_comment = False
                else:
                    i += 1
                continue
            if quote:
                out.append(ch)
                if ch == quote:
                    if nxt == quote and quote == "'":
                        out.append(nxt)
                        i += 2
                        continue
                    quote = None
                elif ch == '\\' and quote == "'":
                    if nxt:
                        out.append(nxt)
                        i += 2
                        continue
                i += 1
                continue
            if ch == '-' and nxt == '-':
                out.extend((ch, nxt)); i += 2; line_comment = True; continue
            if ch == '/' and nxt == '*':
                out.extend((ch, nxt)); i += 2; block_comment = True; continue
            if ch in ("'", '"'):
                quote = ch
                out.append(ch)
                i += 1
                continue
            if ch == '?':
                index += 1
                out.append(f'${index}')
            else:
                out.append(ch)
            i += 1
        return ''.join(out)

    async def execute(self, sql: str, args: Sequence[Any] = ()) -> PgCursor:
        query = self._translate(sql)
        if query is None:
            return PgCursor()
        upper = query.lstrip().upper()
        if upper.startswith('INSERT INTO') and 'RETURNING' not in upper:
            m = re.match(r'(?is)^INSERT\s+INTO\s+([\w"]+)', query)
            if m and m.group(1).strip('"').lower() == 'group_digest_subscriptions':
                query += ' RETURNING id'
                upper = query.lstrip().upper()

        # Preserve SQLite-style implicit DML transaction boundaries.
        if upper.startswith(('INSERT', 'UPDATE', 'DELETE', 'REPLACE')):
            await self._begin_write_transaction()

        if upper.startswith(('SELECT', 'WITH', 'SHOW', 'EXPLAIN')) or ' RETURNING ' in upper:
            records = await self._conn.fetch(query, *(args or ()))
            last_id = records[0]['id'] if records and 'id' in records[0].keys() and ' RETURNING ' in upper else None
            return PgCursor(records, len(records), last_id)
        status = await self._conn.execute(query, *(args or ()))
        found = re.search(r'(\d+)$', status or '')
        return PgCursor(rowcount=int(found.group(1)) if found else 0)

    async def executemany(self, sql: str, seq_of_args):
        query = self._translate(sql)
        if query is None:
            return PgCursor()
        if query.lstrip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'REPLACE')):
            await self._begin_write_transaction()
        await self._conn.executemany(query, list(seq_of_args))
        return PgCursor()

    async def commit(self):
        if self._tx is not None:
            tx, self._tx = self._tx, None
            await tx.commit()

    async def rollback(self):
        if self._tx is not None:
            tx, self._tx = self._tx, None
            await tx.rollback()

    async def close(self):
        if self._tx is not None:
            tx, self._tx = self._tx, None
            try:
                await tx.rollback()
            except Exception:
                pass
        await self._conn.close()


async def connect(_db_path: str | None = None, **_kwargs) -> PgConnection:
    dsn = os.getenv('DATABASE_URL', '').strip()
    if not dsn:
        raise RuntimeError('DATABASE_URL is required; SQLite fallback is disabled')
    return PgConnection(await asyncpg.connect(dsn=dsn, command_timeout=float(os.getenv('DATABASE_TIMEOUT', '20'))))
