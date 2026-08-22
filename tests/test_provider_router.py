import asyncio
import pytest
from services.provider_router import ProviderRouter, ProviderFailure, classify_error


def test_classification():
    assert classify_error(asyncio.TimeoutError()) == "timeout"
    assert classify_error(RuntimeError("HTTP 429")) == "rate_limit"
    assert classify_error(RuntimeError("HTTP 403 forbidden")) == "unauthorized"


@pytest.mark.asyncio
async def test_failover():
    router = ProviderRouter()
    async def bad():
        raise RuntimeError("timeout")
    async def good():
        return [{"title": "ok"}]
    result = await router.failover("search", [("a", bad), ("b", good)])
    assert result == [{"title": "ok"}]
