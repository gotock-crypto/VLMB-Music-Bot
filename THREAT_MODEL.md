# VLMB Threat Model

## Assets

Telegram/provider credentials, user state/history, production SQLite databases, downloaded media/filesystem capacity and provider access.

## Main threats

| Threat | Control |
|---|---|
| Secret exposure | `.env` exclusion, secret audit, structured-log redaction |
| SSRF | URL and host validation |
| Path traversal | Safe filename/path handling |
| Disk/resource exhaustion | Disk checks, bounded queue/workers/retries |
| Provider outage | Health, circuit breaker and failover |
| Callback replay/stale action | Callback catalog and state validation |
| Duplicate download | User-scoped idempotency key |
| Database corruption | Backup, integrity check and restore drill |
| Failed deployment | Preflight, healthcheck and rollback |
| Multiple polling instances | Single-instance protection/deployment checks |

External provider responses are untrusted input and are normalized at the provider/application boundary.
