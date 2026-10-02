# Production audit snapshot

Source: server archive supplied for this project, plus the current public Git repository.

## Snapshot data

The supplied SQLite snapshot contains approximately:

- 260 users
- 150 chats
- 7,988 stats events
- 7,287 user actions
- 1,446 user history records
- 4,193 Telegram audio `file_id` cache records
- 1,403 sent digest-track records
- 2 digest subscriptions
- 3 VK token records

Both supplied SQLite databases passed `PRAGMA integrity_check` before release packaging.

## Main findings

### P0 — credentials

The server snapshot contained hard-coded Telegram/Yandex/Last.fm credentials in `config.py`, and the historical `bot.log` contained Telegram Bot API URLs with the bot token embedded in them. The release removes credentials from source and redacts the supplied logs. Production should still rotate the exposed credentials.

### P0 — deployment drift

The production snapshot and Git version are not identical. The release therefore keeps the existing monolith behavior and adds explicit deployment/rollback tooling rather than replacing the production tree blindly.

### P1 — provider reliability

The supplied logs showed YouTube/yt-dlp JavaScript-runtime and HTTP 403 failures, plus Yandex HTTP 451 responses. Existing fallback logic is retained. The release adds in-process provider search/download success-rate and latency metrics so these issues can be observed without changing routing behavior.

### P1 — Telegram polling conflicts

The supplied historical log contains repeated HTTP 409 `getUpdates` conflicts. This usually means more than one polling client was active. The existing single-instance lock remains in place, and the deployment procedure explicitly checks for exactly one bot process after restart.

### P1 — architecture

The main bot remains a large monolithic module. To minimize regression risk, this release extracts only the existing artist-first ranking rule into a tested module and adds provider health as a separate low-risk service. A broader handler/provider/storage decomposition should be done later in small, tested steps.

## Release safety principle

No database schema migration, destructive data operation, or replacement of the production virtualenv is part of this release. Deployment excludes `.env`, SQLite databases, runtime logs, and `venv/` from the code sync.
