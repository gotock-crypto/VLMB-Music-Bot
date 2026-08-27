import asyncio

import pytest

from services.download_queue import DownloadQueue


@pytest.mark.asyncio
async def test_idempotent_submission_returns_same_job():
    queue = DownloadQueue(worker_count=1, max_size=5)
    first = await queue.submit(7, {"track": "a"}, idempotency_key="req-1")
    second = await queue.submit(7, {"track": "b"}, idempotency_key="req-1")
    assert second.job_id == first.job_id
    assert second.payload == {"track": "a"}
    await queue.close()


@pytest.mark.asyncio
async def test_idempotency_is_scoped_to_user():
    queue = DownloadQueue(worker_count=1, max_size=5)
    first = await queue.submit(7, {"track": "a"}, idempotency_key="req-1")
    second = await queue.submit(8, {"track": "b"}, idempotency_key="req-1")
    assert second.job_id != first.job_id
    await queue.close()


@pytest.mark.asyncio
async def test_shutdown_drains_running_work():
    started = asyncio.Event()
    finished = asyncio.Event()

    async def handler(job):
        started.set()
        await asyncio.sleep(0.01)
        finished.set()
        return "ok"

    queue = DownloadQueue(worker_count=1, max_size=5)
    await queue.start(handler)
    job = await queue.submit(1, {"track": "a"})
    await asyncio.wait_for(started.wait(), timeout=1)
    await queue.shutdown(drain=True, timeout=1)
    assert finished.is_set()
    assert job.status == "completed"
    assert queue.snapshot()["closing"] is True


@pytest.mark.asyncio
async def test_shutdown_rejects_new_work():
    queue = DownloadQueue(worker_count=1, max_size=5)
    await queue.shutdown(drain=False)
    with pytest.raises(RuntimeError, match="shutting down"):
        await queue.submit(1, {"track": "a"})
