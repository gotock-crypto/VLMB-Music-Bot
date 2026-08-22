import pytest
from storage.contracts import InMemoryUserStateStore

@pytest.mark.asyncio
async def test_state_store_roundtrip_and_clear():
    store = InMemoryUserStateStore()
    await store.set(1, "similar_artists", {"ts": 1})
    assert await store.get(1) == {"state": "similar_artists", "data": {"ts": 1}}
    await store.clear(1)
    assert await store.get(1) is None
