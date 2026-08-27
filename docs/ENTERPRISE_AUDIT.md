# VLMB Enterprise Audit

**Baseline:** VLMB 4.0.0-rc1 development line

This document is the Phase 1 audit gate. It records the current architecture, the target direction, and the remaining controlled work. It is deliberately evidence-based; a capability is not marked complete merely because a similarly named file exists.

## Architecture

| Area | CURRENT | TARGET | RISK | MIGRATION PLAN |
|---|---|---|---|---|
| Presentation | Legacy Telegram handlers remain in `music_bot_user_mixes.py` | Thin handlers calling application use cases | High coupling | Extract one flow at a time and retain legacy compatibility until verified |
| Application | `application/` exists; `SearchMusic` extracted | All critical user actions represented by use cases | Medium | Extract DownloadTrack, favorites, history, then switch call sites |
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
- Queue retries are bounded.
- Healthcheck/watchdog infrastructure exists.
- Deployment has preflight, backup and rollback paths.

### TARGET

- Idempotent download submission.
- Explicit graceful queue shutdown.
- Controlled retry policy with observable outcomes.
- Actionable SLO/alert definitions.
- Verified backup/restore drills.

## Security

Current controls include secret exclusion, safe filenames, path validation, media-host validation, SQLite integrity checks and disk-space checks. Remaining Phase 2 work is documented in `SECURITY.md` and `THREAT_MODEL.md`.

## Testing

The repository has unit, provider, callback/state, critical-flow, metrics, deployment and rollback tests. Phase 2 requires stronger idempotency, shutdown, structured logging, SLO and security regression coverage.

## Phase 1 exit criteria

- [x] Architecture audit documented.
- [x] Application/domain/provider boundaries exist.
- [x] Search use case extracted with tests.
- [x] Callback/state safety gates exist.
- [x] Provider contract/failover foundation exists.
- [x] Production data remains outside ordinary code artifacts.
- [ ] Remaining critical legacy handlers extracted.

The final unchecked item is intentionally a migration stream rather than a single rewrite. Phase 1 is considered structurally complete once the critical behavior has an application entry point and its legacy call site has been switched and production-verified.
