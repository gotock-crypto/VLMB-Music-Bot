import pytest
from providers.base import CallableProviderAdapter
from services.provider_router import ProviderRouter, ProviderFailure

@pytest.mark.asyncio
async def test_adapter_has_unified_search_download_contract():
    async def search(query, **kwargs): return [{"title": query}]
    async def download(track, **kwargs): return {"path": "/tmp/x"}
    adapter = CallableProviderAdapter("fake", search=search, download=download)
    assert await adapter.search("x") == [{"title": "x"}]
    assert await adapter.download({"uid": "1"}) == {"path": "/tmp/x"}

@pytest.mark.asyncio
async def test_adapter_failover_uses_router_circuit_policy():
    router = ProviderRouter(cooldown_seconds=60, failure_threshold=1)
    async def bad(query, **kwargs): raise TimeoutError("timeout")
    async def good(query, **kwargs): return [query]
    a = CallableProviderAdapter("bad", search=bad)
    b = CallableProviderAdapter("good", search=good)
    from services.provider_router import adapter_failover
    result = await adapter_failover(router, "search", [a, b], lambda x: x.search("ok"))
    assert result == ["ok"]
    assert router.last_route["search"] == "good"
