# VLMB 4.0.0-rc2 Release Notes

## Phase 1 — Safe Foundation
- Enterprise architecture audit.
- SearchMusic and DownloadTrack application boundaries.
- Provider-independent adapter routing, health and failover.
- Callback/state safety retained.

## Phase 2 — Reliability & Operations
- User-scoped idempotent download queue submission.
- Graceful queue shutdown with bounded drain timeout.
- Safe structured JSON event logging with credential redaction.
- Initial SLOs, security controls and threat model.
- Regression tests for idempotency, shutdown, DownloadTrack failover and log redaction.
- Release artifact integrity gate in CI.

## Safety
No production database migration, `.env` change, production directory change, systemd architecture change, provider semantic rewrite or destructive production operation.
