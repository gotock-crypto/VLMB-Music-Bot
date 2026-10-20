# VLMB PostgreSQL cutover runbook

This release is prepared for PostgreSQL runtime, but it is **not safe to deploy to a server that has no PostgreSQL service or `DATABASE_URL` configured**. Keep the currently running SQLite-based bot in service until all pre-cutover checks pass.

## Preconditions

- Keep a verified backup of `/root/MusBot`, including both SQLite databases.
- Install PostgreSQL on the target host or provision a reachable PostgreSQL instance.
- Create an empty database dedicated to VLMB and a least-privilege login role.
- Add `DATABASE_URL=postgresql://...` and `DATABASE_TIMEOUT=20` to `/root/MusBot/.env`; keep `.env` mode `0600`. URL-encode reserved characters in the password. Never print or paste the URL into logs or chat.
- Ensure the `DATABASE_URL` target is the intended empty VLMB database. The SQLite files remain the migration source and must not be overwritten.

## Read-only validation before downtime

From the extracted release directory:

```bash
/root/MusBot/venv/bin/python3 scripts/preflight.py --skip-dependency-check --env-file /root/MusBot/.env
/root/MusBot/venv/bin/python3 -m py_compile music_bot_user_mixes.py config.py storage/postgres.py scripts/*.py
/root/MusBot/venv/bin/python3 scripts/migrate_sqlite_to_postgres.py --dry-run \
  --stats-db /root/MusBot/bot_stats.db --tokens-db /root/MusBot/vk_tokens.db
```

After the release dependencies (including `asyncpg`) are installed and PostgreSQL is reachable, check connectivity without changing data:

```bash
/root/MusBot/venv/bin/python3 scripts/migrate_sqlite_to_postgres.py \
  --env-file /root/MusBot/.env --check-connection \
  --stats-db /root/MusBot/bot_stats.db --tokens-db /root/MusBot/vk_tokens.db
```

## Cutover

Only after the preconditions and read-only checks pass, run:

```bash
RELEASE_DIR=/root/vlmb_release/MusBot /root/vlmb_release/MusBot/scripts/deploy_release.sh
```

The deployment script creates a code/data backup, migrates the two SQLite stores transactionally, deploys the PostgreSQL runtime, and performs service/health checks. It does not install the PostgreSQL server itself. If any preflight or connectivity check fails, do not stop the existing service.

## Post-cutover verification

```bash
systemctl is-active musicbot.service
pgrep -af '/root/MusBot/venv/bin/python3 /root/MusBot/music_bot_user_mixes.py'
/root/MusBot/venv/bin/python3 /root/MusBot/scripts/healthcheck.py
journalctl -u musicbot.service -n 100 --no-pager
```

Then exercise Telegram flows: `/start`, search and download from each enabled provider, `/repeat`, `/history`, `/favorites`, `/favorite`, `/mix`, `/settings`, and digest actions if used in groups. Compare PostgreSQL table row counts with the recorded SQLite source counts before accepting the migration.

## Rollback notes

The original SQLite files are intentionally retained. The deploy script can restore the previous code tree if cutover fails, but it does not roll back PostgreSQL data changes. Preserve both the code backup and SQLite files until acceptance is complete. Do not assume that a code rollback automatically reverts database contents.
