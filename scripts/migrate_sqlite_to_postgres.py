#!/usr/bin/env python3
"""One-time, additive migration of the bot's SQLite stores to PostgreSQL.

Usage: DATABASE_URL=postgresql://... python scripts/migrate_sqlite_to_postgres.py \
  --stats-db bot_stats.db --tokens-db vk_tokens.db

The script never deletes source SQLite files or truncates destination tables.
It creates missing schema objects and inserts rows absent from PostgreSQL.
"""
from __future__ import annotations
import argparse
import asyncio
import os
import re
import sqlite3
import shlex
import sys
from pathlib import Path

try:
    import asyncpg
except ImportError:  # dry-run source validation does not require the driver
    asyncpg = None


def pg_ddl(sql: str) -> str:
    """Convert the SQLite DDL used by this project into PostgreSQL-compatible DDL."""
    # SQLite AUTOINCREMENT is valid only for INTEGER PRIMARY KEY. Preserve that
    # behavior with a PostgreSQL sequence-backed BIGSERIAL column.
    sql = re.sub(
        r'(?i)\b([A-Za-z_][A-Za-z0-9_]*)\s+INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b',
        r'\1 BIGSERIAL PRIMARY KEY',
        sql,
    )
    # Keep non-auto-increment integer primary keys as regular integer keys.
    sql = re.sub(r'\bINTEGER\b', 'BIGINT', sql, flags=re.I)
    sql = re.sub(r'\bREAL\b', 'DOUBLE PRECISION', sql, flags=re.I)
    # The application treats legacy timestamps as strings/numeric epoch values.
    sql = re.sub(r'\bTIMESTAMP\b', 'TEXT', sql, flags=re.I)
    sql = re.sub(r'(?i)DEFAULT\s+CURRENT_TIMESTAMP\b', 'DEFAULT (CURRENT_TIMESTAMP::text)', sql)
    sql = re.sub(r'\bBLOB\b', 'BYTEA', sql, flags=re.I)
    # SQLite-only table suffix; PostgreSQL does not support it.
    sql = re.sub(r'(?i)\s+WITHOUT\s+ROWID\s*$', '', sql)
    return sql


def quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'

async def migrate_file(conn: asyncpg.Connection, db_path: Path) -> dict:
    if not db_path.is_file():
        raise FileNotFoundError(f'SQLite database not found: {db_path}')
    source = sqlite3.connect(f'file:{db_path.resolve()}?mode=ro', uri=True)
    source.row_factory = sqlite3.Row
    report = {}
    try:
        tables = source.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        for table in tables:
            name, ddl = table['name'], table['sql']
            if not ddl:
                continue
            await conn.execute(pg_ddl(ddl).replace('CREATE TABLE ', 'CREATE TABLE IF NOT EXISTS ', 1))
            columns = [r['name'] for r in source.execute(f'PRAGMA table_info({quote(name)})')]
            if not columns:
                report[name] = {'source': 0, 'inserted': 0}
                continue
            rows = source.execute(f'SELECT * FROM {quote(name)}').fetchall()
            before = await conn.fetchval(f'SELECT count(*) FROM {quote(name)}')
            if rows:
                placeholders = ', '.join(f'${i}' for i in range(1, len(columns)+1))
                cols_sql = ', '.join(quote(c) for c in columns)
                # Additive and rerunnable: primary/unique conflicts retain existing target rows.
                sql = f'INSERT INTO {quote(name)} ({cols_sql}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
                await conn.executemany(sql, [tuple(row[c] for c in columns) for row in rows])
            after = await conn.fetchval(f'SELECT count(*) FROM {quote(name)}')
            report[name] = {'source': len(rows), 'target_before': before, 'target_after': after,
                            'inserted': after - before, 'already_present_or_conflicted': max(0, len(rows) - (after - before))}
            # Some tables have an `id` column that is not sequence-backed. Only
            # advance a sequence when PostgreSQL confirms one exists.
            if 'id' in columns:
                sequence_name = await conn.fetchval(
                    "SELECT pg_get_serial_sequence($1, 'id')", name
                )
                if sequence_name:
                    max_id = await conn.fetchval(
                        f"SELECT MAX({quote('id')}) FROM {quote(name)}"
                    )
                    if max_id is not None:
                        await conn.execute("SELECT setval($1::regclass, $2, true)", sequence_name, max_id)
        indexes = source.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL ORDER BY name").fetchall()
        for index in indexes:
            index_sql = re.sub(
                r'(?i)^CREATE (UNIQUE )?INDEX ',
                lambda m: 'CREATE ' + (m.group(1) or '') + 'INDEX IF NOT EXISTS ',
                pg_ddl(index['sql']),
                count=1,
            )
            await conn.execute(index_sql)
    finally:
        source.close()
    return report

async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stats-db', default='bot_stats.db', type=Path)
    parser.add_argument('--tokens-db', default='vk_tokens.db', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='validate source SQLite databases without connecting to PostgreSQL')
    parser.add_argument('--check-connection', action='store_true', help='validate DATABASE_URL and PostgreSQL connectivity without changing data')
    parser.add_argument('--env-file', type=Path, help='read DATABASE_URL from a dotenv-style file without printing secrets')
    args = parser.parse_args()
    if args.env_file:
        for raw in args.env_file.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:].lstrip()
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            try:
                parts = shlex.split(value.strip(), comments=True, posix=True)
                value = parts[0] if parts else ''
            except ValueError:
                value = value.strip().strip('\"\'')
            os.environ.setdefault(key.strip(), value)
    for path in (args.stats_db, args.tokens_db):
        if not path.is_file():
            parser.error(f'missing SQLite database: {path}')
        check = sqlite3.connect(f'file:{path.resolve()}?mode=ro', uri=True)
        try:
            integrity = check.execute('PRAGMA quick_check').fetchone()[0]
            if integrity != 'ok':
                parser.error(f'SQLite integrity check failed for {path}: {integrity}')
        finally:
            check.close()
    if args.dry_run:
        print('SQLite source files exist and are readable. No data was changed.')
        return 0
    if asyncpg is None:
        parser.error('asyncpg is required for migration; install requirements.txt first')
    dsn = os.getenv('DATABASE_URL', '').strip()
    if not dsn:
        parser.error('DATABASE_URL is required')
    if args.check_connection:
        conn = await asyncpg.connect(dsn=dsn, command_timeout=20)
        await conn.close()
        print('PostgreSQL connection validated. No data was changed.')
        return 0
    conn = await asyncpg.connect(dsn=dsn, command_timeout=120)
    try:
        # Single transaction ensures a failed migration does not leave a partial import.
        async with conn.transaction():
            all_reports = {}
            for path in (args.stats_db, args.tokens_db):
                all_reports[str(path)] = await migrate_file(conn, path)
        for path, report in all_reports.items():
            print(f'[{path}]')
            for table, counts in report.items():
                print(f'  {table}: source={counts["source"]}, inserted={counts["inserted"]}, target_after={counts["target_after"]}')
        print('Migration transaction committed. Verify counts before switching production.')
    finally:
        await conn.close()
    return 0

if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
