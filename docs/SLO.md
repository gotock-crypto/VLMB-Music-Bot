# VLMB Service Level Objectives

SLOs are targets for the current single-instance production architecture. They are intentionally conservative until a longer production baseline is available.

## Availability

**Target:** >= 99.5% monthly process availability, excluding planned maintenance.

Measurement: healthcheck/watchdog state over the service observation window.

## Search latency

**Target:** P95 <= 3 seconds for successful provider search requests under normal provider conditions.

Measurement: application search duration, excluding Telegram rendering time.

## Download acceptance latency

**Target:** P95 <= 2 seconds from accepted download request to queue acknowledgement.

Measurement: enqueue/acceptance path only; actual provider download duration is tracked separately.

## Error rate

**Target:** < 2% of application requests ending in an unexpected internal error over a rolling 15-minute window.

Provider-specific failures are tracked separately so an isolated provider outage does not hide application health.

## Provider availability

**Target:** >= 98% successful calls for each normally enabled provider over a rolling 24-hour window, measured only when the provider is exercised.

## Rollback time

**Target:** <= 10 minutes from failed release detection to previous release healthcheck PASS during a controlled rollback.

## MTTR

**Initial target:** <= 30 minutes for a production application incident with an identified rollback path.

This is an operational target, not a guarantee. It must be revised after real incident/rollback evidence exists.

## Baseline policy

Do not claim an SLO is met from a single smoke test. Collect measurements over time, then compare the observed P50/P95/P99 and error rate with these targets.
