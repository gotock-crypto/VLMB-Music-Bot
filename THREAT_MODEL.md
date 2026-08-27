# VLMB Threat Model

## Assets

- Telegram bot credentials and provider credentials.
- User state and history.
- `bot_stats.db` and `vk_tokens.db`.
- Downloaded media and filesystem capacity.
- Provider access and availability.

## Threats and controls

| Threat | Impact | Existing/required control |
|---|---|---|
| Secret committed to Git | Credential compromise | `.env` exclusion + secret scan |
| SSRF via user URL | Network/internal service access | URL/host validation |
| Path traversal | Arbitrary file write | Filename/path sanitization |
| Malicious filename | Filesystem abuse | Safe filename policy |
| Oversized download | Disk exhaustion | Disk checks + bounded download behavior |
| Queue flooding | Resource exhaustion | Bounded queue + workers + retries |
| Provider outage | Availability degradation | Health + circuit breaker + failover |
| Callback replay/stale action | Incorrect state mutation | Callback catalog + state validation |
| Duplicate download submission | Duplicate work/data | Idempotency key at application/queue boundary |
| Database corruption | Data loss/outage | Backup + SQLite integrity checks + restore drill |
| Failed deployment | Service outage | Preflight + healthcheck + rollback |
| Multiple polling instances | Telegram update conflicts | Single-instance protection / deployment checks |

## Trust boundaries

```text
Telegram/user input
        ↓
presentation
        ↓
application
        ↓
domain + ports
   ↙          ↘
providers    storage
```

External provider responses are untrusted input and must be normalized before application use.

## Security acceptance

A new feature is not complete if it introduces a new user-controlled network destination, filesystem write path, persistence mutation, callback namespace or retry loop without a corresponding validation and regression test.
