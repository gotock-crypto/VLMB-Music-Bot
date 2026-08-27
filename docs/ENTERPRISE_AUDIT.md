# VLMB Enterprise Audit

**Baseline:** VLMB 4.0.0-rc2 development line

This document is the Phase 1 audit gate. It records the current architecture, the target direction, and the remaining controlled work. It is deliberately evidence-based; a capability is not marked complete merely because a similarly named file exists.

## Architecture

| Area | CURRENT | TARGET | RISK | MIGRATION PLAN |
|---|---|---|---|---|
| Presentation | Legacy Telegram handlers remain in `music_bot_user_mixes.py` | Thin handlers calling application use cases | High coupling | Extract one flow at a time and retain legacy compatibility until verified |
| Application | `application/` exists; `SearchMusic` and `DownloadTrack` extracted | All critical user actions represented by use cases | Medium | Extract favorites, history, playlist, and remaining critical flows |
| Domain | Track/DownloadResult and TrackInfo boundaries exist | Provider-independent business models and policies | Low | Extend only when a concrete business rule requires it |
| Providers | Unified adapter contract, router, health | Stable provider port with isolated adapters | Medium | Continue contract tests; never expose provider-specific details to application |
| Storage | State store contract exists; legacy persistence remains | Explicit storage ports behind application/domain | High | Extract persistence responsibility incrementally; no schema rewrite |
| Callbacks | Catalog + audit + state contract | Authoritative catalog with replay/stale safety | Medium | Keep catalog authoritative and add tests for newly extracted flows |
| Deployment | Existing SSH/systemd/venv/SQLite deployment | Reproducible, validated, reversible releases | Medium | Improve artifact and rollback gates without changing production root |

## Giant core

`music_bot_user_mixes.py` remains the compatibility layer. It is intentionally not deleted or rewritten wholesale. The migration rule is:

`extract -> test -> behavior verify -> switch -> observe -> remove legacy`.

## Dependency direction

```text
presentation -> application -> domain
                         -> ports/interfaces -> providers/storage/infrastructure
```

Forbidden dependencies are enforced by the architecture audit where applicable: domain must not depend on Telegram or storage; application must not depend on concrete providers; providers must not depend on Telegram.

## Reliability

### CURRENT

- Provider error classification and failover exist.
- Circuit breaker exists.
- Provider health metrics exist.
- Bounded download queue exists.
- Queue retries are bounded and idempotent submission is covered by tests.
- Queue shutdown has a bounded drain path.
- Healthcheck/watchdog infrastructure exists.
- Deployment has preflight, backup and rollback paths.
- A deterministic rollback drill exists in CI.

### TARGET

- Complete production evidence for backup/restore, failover and deployment rollback.
- Critical legacy handlers extracted and production-verified incrementally.
- Final enterprise readiness assessment based on measured evidence rather than file presence.

## Security

Current controls include secret exclusion, safe filenames, path validation, media-host validation, SQLite integrity checks, disk-space checks, structured credential redaction and single-instance protection. Remaining operational verification is documented in `SECURITY.md` and `THREAT_MODEL.md`.

## Testing

The repository has unit, provider, callback/state, critical-flow, metrics, deployment and rollback tests. CI now validates the release tree before test-generated caches exist and compiles all architectural Python layers.

## Phase 1 / 2 exit status

- [x] Architecture audit documented.
- [x] Application/domain/provider boundaries exist.
- [x] Search and DownloadTrack use cases extracted with tests.
- [x] Callback/state safety gates exist.
- [x] Provider contract/failover foundation exists.
- [x] Idempotent queue submission and bounded graceful shutdown exist.
- [x] Production data remains outside ordinary code artifacts.
- [ ] Remaining critical legacy handlers extracted and production-verified.
- [ ] Production restore/failover/rollback evidence collected.

The unchecked items are intentionally evidence-driven migration/operations work, not reasons to rewrite the production core in one step.
