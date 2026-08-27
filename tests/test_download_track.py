import pytest

from application.use_cases.download_track import DownloadTrack
from providers.base import MusicProviderAdapter
from services.provider_health import ProviderHealth
from services.provider_router import ProviderFailure, ProviderRouter


class FakeAdapter(MusicProviderAdapter):
    def __init__(self, name, result=None, error=None):
        self.name = name
        self.result = result
        self.error = error
        self.calls = 0

    async def search(self, query, **kwargs):
        return []

    async def download(self, track, **kwargs):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test_download_track_returns_first_success_and_records_health():
    health = ProviderHealth()
    first = FakeAdapter("vk", error=RuntimeError("connection reset"))
    second = FakeAdapter("ym", result={"path": "/tmp/a.mp3"})
    use_case = DownloadTrack(
        [first, second],
        router=ProviderRouter(failure_threshold=2),
        health=health,
    )

    result = await use_case.execute({"uid": "track-1"})
    assert result == {"path": "/tmp/a.mp3"}
    assert first.calls == 1
    assert second.calls == 1
    assert health.snapshot()["vk:download"]["failure"] == 1
    assert health.snapshot()["ym:download"]["success"] == 1


@pytest.mark.asyncio
async def test_download_track_normalizes_all_provider_failure():
    use_case = DownloadTrack(
        [FakeAdapter("vk", error=RuntimeError("timeout"))],
        router=ProviderRouter(failure_threshold=2),
    )
    with pytest.raises(ProviderFailure) as exc_info:
        await use_case.execute({"uid": "track-1"})
    assert exc_info.value.kind == "all_failed"
