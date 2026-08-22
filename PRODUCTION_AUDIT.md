# VLMB Music Bot — Production Audit

Date: 2026-08-22

## Production

- Host: `45.43.90.131`
- Application: `/root/MusBot`
- systemd: `musicbot.service`
- Runtime: Python 3.12 virtual environment
- Production `.env`: external to Git, mode `0600`

## Release verification

- Python compile: passed
- Imports: passed
- Regression tests: `10 passed`
- Preflight with production `.env`: passed
- SQLite integrity: `bot_stats.db` and `vk_tokens.db` passed
- Healthcheck after deployment: passed
- Exactly one bot process after restart: passed
- Telegram smoke-test: accepted by user

## Deployment safety

Deployment validates the release before stopping the running service, creates a production backup, preserves `.env`, `venv`, SQLite databases and logs during code replacement, and contains an automatic rollback path.

## Known optional infrastructure

Redis is not required for startup and may remain unavailable. The bot continues with local/in-memory behavior.

## Known follow-up

YouTube/yt-dlp edge cases such as individual live events or provider-side restrictions remain separate operational issues; they do not invalidate the successful production deployment.
