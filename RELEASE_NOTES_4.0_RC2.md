# VLMB 4.0.0-rc2 Release Notes

## Phase 1 — Safe Foundation

- Added the enterprise architecture audit.
- Preserved the giant core as a compatibility bootstrap.
- Added `DownloadTrack` beside the existing `SearchMusic` application boundary.
- Retained provider-independent adapter routing, health and failover.
- Preserved callback catalog and explicit state-machine contracts.

## Phase 2 — Reliability & Operations

- Added user-scoped idempotent download queue submission.
- Added graceful queue shutdown with bounded drain timeout.
- Added safe structured JSON event logging with credential redaction.
- Documented initial SLOs and threat model/security controls.
- Added regression tests for idempotency, shutdown, DownloadTrack failover and log redaction.
- Added release artifact integrity enforcement to CI.

## Safety

- No production database migration.
- No `.env` change.
- No production directory change.
- No systemd architecture change.
- No provider semantic rewrite.
- No destructive production operation.

## Acceptance gate

This release candidate requires clean-checkout tests, artifact validation and server-side smoke/rollback verification before production acceptance.
