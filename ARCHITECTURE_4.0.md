# VLMB 4.0 Architecture & Reliability

## Target boundaries

```text
Telegram / bot handlers
        |
        v
application (commands, callbacks, state)
        |
        v
domain (models, policies, errors)
   |                 |
   v                 v
providers          storage
   |                 |
   v                 v
YM / VK / YT      SQLite / session state
```

## Migration rule

`music_bot_user_mixes.py` remains the compatibility bootstrap during 4.0. Each extracted responsibility must gain tests before the old implementation is removed.

## State audit

The callback catalog is authoritative for callback namespaces currently emitted by the core. CI runs `scripts/callback_audit.py` and fails on unregistered literal/f-string callback prefixes.

## Provider contract

Application code should depend on `MusicProviderAdapter.search()`, `.download()` and `.health()`. Existing managers are wrapped by adapters so provider implementation can move without changing application code.

## Reliability checks

- callback audit
- critical state transitions
- provider adapter failover
- queue/concurrency smoke
- rollback drill simulation
- architecture guardrails
- full pytest in CI

## Production rule

Do not deploy RC1 over 3.0.6 until CI is green and the server-side Telegram smoke flow is complete. Keep the pre-release backup for rollback.
