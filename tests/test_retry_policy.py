import asyncio

import pytest

from services.provider_router import ProviderFailure
from services.retry_policy import is_retryable, retry_async


def test_retry_classification_is_transient_only():
    assert is_retryable(ProviderFailure("ym", "search", "timeout"))
    assert is_retryable(ProviderFailure("ym", "search", "rate_limit"))
    assert is_retryable(ProviderFailure("ym", "search", "unavailable"))
    assert not is_retryable(ProviderFailure("ym", "search", "unauthorized"))
    assert not is_retryable(ProviderFailure("ym", "search", "no_result"))
    assert not is_retryable(ProviderFailure("ym", "search", "invalid"))


@pytest.mark.asyncio
async def test_retry_async_retries_transient_failure():
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ProviderFailure("ym", "download", "timeout")
        return "ok"

    result = await retry_async(operation, max_attempts=3, base_delay=0, max_delay=0)
    assert result == "ok"
    assert attempts == 3


@pytest.mark.asyncio
async def test_retry_async_does_not_retry_non_transient_failure():
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        raise ProviderFailure("ym", "search", "invalid")

    with pytest.raises(ProviderFailure):
        await retry_async(operation, max_attempts=3, base_delay=0, max_delay=0)
    assert attempts == 1


@pytest.mark.asyncio
async def test_queue_retry_state_is_bounded():
    from services.download_queue import DownloadQueue

    attempts = 0
    queue = DownloadQueue(worker_count=1, max_size=4)

    async def handler(job):
        nonlocal attempts
        attempts += 1
        raise asyncio.TimeoutError("temporary timeout")

    await queue.start(handler)
    job = await queue.submit(1, {"track": "x"}, idempotency_key="retry-test")
    await asyncio.wait_for(queue._queue.join(), timeout=5)
    assert job.status == "failed"
    assert job.retries == queue.max_retries
    assert attempts == queue.max_retries + 1
    await queue.shutdown(drain=False)
