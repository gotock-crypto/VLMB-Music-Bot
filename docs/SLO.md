# VLMB Service Level Objectives

These are initial targets for the current single-instance production architecture. They are not claims of measured compliance until a production-like baseline exists.

- Availability: >= 99.5% monthly, excluding planned maintenance.
- Search latency: P95 <= 3s for successful provider searches under normal conditions.
- Download acceptance: P95 <= 2s from accepted request to queue acknowledgement.
- Unexpected application error rate: < 2% over a rolling 15-minute window.
- Exercised provider availability: >= 98% over a rolling 24-hour window.
- Controlled rollback: <= 10 minutes to previous-release healthcheck PASS.
- Initial MTTR target: <= 30 minutes when a rollback path exists.

Measure P50/P95/P99, throughput, queue wait, CPU/RAM/I/O, provider latency and error rate before declaring an SLO achieved.
