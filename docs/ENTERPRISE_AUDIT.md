# VLMB Enterprise Audit

**Baseline:** VLMB 4.0.0-rc2 development line

## Phase 1 status

Architecture boundaries, callback/state safety, provider contracts, SearchMusic and the TrackInfo domain boundary are implemented and covered by tests. The giant core remains the compatibility layer by design.

### CURRENT → TARGET

| Area | CURRENT | TARGET | Risk | Migration |
|---|---|---|---|---|
| Presentation | Telegram handlers still live in `music_bot_user_mixes.py` | Thin handlers calling application use cases | High | Extract/switch one critical flow at a time |
| Application | SearchMusic and DownloadTrack boundaries exist | Critical user actions represented by use cases | Medium | Continue favorites/history/playlist extraction |
| Domain | Track/DownloadResult/TrackInfo | Provider-independent policies/models | Low | Add only concrete business rules |
| Providers | Adapter contract + router + health | Stable provider port | Medium | Contract tests and isolated adapters |
| Storage | Storage contracts coexist with legacy persistence | Explicit application storage ports | High | Incremental extraction; no schema rewrite |
| Callback/state | Catalog + audits + state machine | Full stale/replay safety | Medium | Extend regression coverage with each extraction |
| Deployment | SSH/systemd/venv/SQLite with backup/rollback | Reproducible validated artifact flow | Medium | Improve release gates without changing production root |

## Phase 2 status

Implemented foundation: bounded queue, bounded retries, provider failover/circuit breaker, idempotent queue submission, graceful queue shutdown API, provider health, latency metrics, healthcheck/watchdog, SLO definitions, security controls, threat model and safe structured logging.

Remaining items are operational evidence rather than missing architecture: production baseline collection, restore drill and full deployment verification.

## Safety boundary

No production database, `.env`, production directory, systemd architecture or user-facing behavior is changed by the Phase 1/2 development package.
