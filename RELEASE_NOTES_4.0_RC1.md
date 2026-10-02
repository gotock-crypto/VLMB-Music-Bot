# VLMB 4.0.0-rc1 — Architecture & Reliability

This release candidate is the first staged architecture/reliability pass after 3.0.6.

## What changed

1. Callback namespace catalog and static audit.
2. Explicit critical-flow state machine and tests.
3. Application/domain/provider/storage boundaries.
4. Unified provider adapter contract.
5. Adapter failover integration tests.
6. Queue/concurrency load smoke.
7. Guarded real rollback drill hook.
8. CI clean-checkout validation through release checks.
9. Existing metrics/provider-health boundary retained.
10. UX regression coverage preserved, including favorites and similar-search navigation.

## What is intentionally not finished

The 519 KB Telegram core is still the compatibility bootstrap. This RC does not claim a completed flag-day decomposition of every handler, SQLite operation, or provider implementation. Those extractions are gated by the new contracts and tests.
