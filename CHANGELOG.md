# Changelog

## 2026-08-22 — Production maintenance release

- Synced production-safe environment configuration.
- Made Redis optional for service startup.
- Added explicit dotenv-aware preflight checks without exposing secrets.
- Updated YouTube/yt-dlp runtime requirements.
- Added provider health metrics and artist-first search scoring modules.
- Added regression coverage for deployment, rollback, configuration and provider behavior.
- Added safe deployment and rollback scripts that preserve `.env`, `venv` and production SQLite data.
- Production release passed compile/import checks and 10 regression tests before deployment.
- Production smoke-test accepted after deployment.

## Notes

- Real `.env`, production databases and runtime logs are never committed.
- Redis remains optional; the bot falls back to local/in-memory behavior when unavailable.
