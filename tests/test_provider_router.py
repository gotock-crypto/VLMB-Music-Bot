import asyncio
import pytest
from services.provider_router import ProviderRouter, ProviderFailure, classify_error


def test_classification():
    assert classify_error(asyncio.TimeoutError()) == "timeout"
    assert classify_error(RuntimeError("HTTP 429")) == "rate_limit"
    assert classify_error(RuntimeError("HTTP 403 forbidden")) == "unauthorized"
    assert classify_error(RuntimeError("connection reset")) == "unavailable"
    assert classify_error(RuntimeError("invalid result")) == "invalid"
    assert classify_error(RuntimeError("HTTP 404 not found")) == "no_result"


@pytest.mark.asyncio
async def test_failover():
    router = ProviderRouter()

    async def bad():
        raise RuntimeError("timeout")

    async def good():
        return [{"title": "ok"}]

    result = await router.failover("search", [("a", bad), ("b", good)])
    assert result == [{"title": "ok"}]
    assert router.last_route["search"] == "b"


@pytest.mark.asyncio
async def test_all_providers_failed_returns_normalized_router_error():
    router = ProviderRouter(failure_threshold=3)

    async def ym_fail():
        raise RuntimeError("timeout")

    async def vk_fail():
        raise RuntimeError("connection reset")

    async def yt_fail():
        raise RuntimeError("HTTP 429 rate limit")

    with pytest.raises(ProviderFailure) as exc_info:
        await router.failover("search", [("ym", ym_fail), ("vk", vk_fail), ("yt", yt_fail)])

    assert exc_info.value.provider == "router"
    assert exc_info.value.kind == "all_failed"
    assert "ym:timeout" in str(exc_info.value)
    assert "vk:unavailable" in str(exc_info.value)
    assert "yt:rate_limit" in str(exc_info.value)


@pytest.mark.asyncio
async def test_circuit_opens_at_threshold_and_blocks_next_call():
    router = ProviderRouter(cooldown_seconds=60, failure_threshold=2)
    calls = 0

    async def bad():
        nonlocal calls
        calls += 1
        raise RuntimeError("timeout")

    with pytest.raises(ProviderFailure) as first:
        await router.call("ym", "search", bad)
    assert first.value.kind == "timeout"
    assert router.status()["ym"]["failures"] == 1
    assert router.status()["ym"]["available"] is True

    with pytest.raises(ProviderFailure) as second:
        await router.call("ym", "search", bad)
    assert second.value.kind == "timeout"
    assert router.status()["ym"]["failures"] == 2
    assert router.status()["ym"]["available"] is False

    with pytest.raises(ProviderFailure) as blocked:
        await router.call("ym", "search", bad)
    assert blocked.value.kind == "circuit_open"
    assert calls == 2
