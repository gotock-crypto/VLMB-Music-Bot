import pytest
from services.metrics import MetricsRegistry

@pytest.mark.asyncio
async def test_metrics_percentiles():
    m = MetricsRegistry()
    await m.record("search", ok=True, seconds=0.1)
    await m.record("search", ok=False, seconds=0.5)
    snap = await m.snapshot()
    assert snap["counters"]["search.total"] == 2
    assert snap["counters"]["search.errors"] == 1
    assert snap["latency"]["search"]["p95"] >= 0.1
