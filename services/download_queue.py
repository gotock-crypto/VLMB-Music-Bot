"""Bounded async download job queue with priority, retries and cancellation."""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Optional


@dataclass
class DownloadJob:
    job_id: str
    user_id: int
    payload: Dict[str, Any]
    priority: int = 100
    retries: int = 0
    status: str = "queued"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    error: str = ""
    result: Any = None
    task: Optional[asyncio.Task] = None


class DownloadQueue:
    def __init__(self, worker_count: int = 3, max_size: int = 100):
        self.worker_count = max(1, int(worker_count))
        self.max_size = max(1, int(max_size))
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=self.max_size)
        self.jobs: Dict[str, DownloadJob] = {}
        self._workers: list[asyncio.Task] = []
        self._seq = 0
        self._handler: Optional[Callable[[DownloadJob], Awaitable[Any]]] = None
        self._started = False

    async def start(self, handler: Callable[[DownloadJob], Awaitable[Any]]) -> None:
        if self._started:
            return
        self._handler = handler
        self._started = True
        self._workers = [asyncio.create_task(self._worker(i), name=f"vlmb-download-worker-{i}") for i in range(self.worker_count)]

    async def _worker(self, worker_id: int) -> None:
        while True:
            _, seq, job_id = await self._queue.get()
            job = self.jobs.get(job_id)
            if not job:
                self._queue.task_done(); continue
            if job.status == "cancelled":
                self._queue.task_done(); continue
            job.status = "running"; job.updated_at = time.time()
            try:
                if self._handler is None:
                    raise RuntimeError("queue handler is not configured")
                job.result = await self._handler(job)
                job.status = "completed"
                job.error = ""
            except asyncio.CancelledError:
                job.status = "cancelled"
                raise
            except Exception as exc:
                job.retries += 1
                job.error = str(exc)[:300]
                if job.retries <= 2:
                    job.status = "queued"
                    await asyncio.sleep(min(5.0, 0.5 * (2 ** (job.retries - 1))))
                    await self._queue.put((job.priority, seq, job.job_id))
                else:
                    job.status = "failed"
            finally:
                job.updated_at = time.time()
                self._queue.task_done()

    async def submit(self, user_id: int, payload: Dict[str, Any], priority: int = 100) -> DownloadJob:
        if self._queue.full():
            raise RuntimeError("download queue is full")
        self._seq += 1
        job = DownloadJob(str(uuid.uuid4()), int(user_id), dict(payload), int(priority))
        self.jobs[job.job_id] = job
        await self._queue.put((job.priority, self._seq, job.job_id))
        return job

    def get(self, job_id: str) -> Optional[DownloadJob]:
        return self.jobs.get(job_id)

    async def cancel(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if not job or job.status in {"completed", "failed", "cancelled"}:
            return False
        job.status = "cancelled"; job.updated_at = time.time()
        if job.task and not job.task.done():
            job.task.cancel()
        return True

    def snapshot(self) -> Dict[str, Any]:
        counts: Dict[str, int] = {}
        for job in self.jobs.values():
            counts[job.status] = counts.get(job.status, 0) + 1
        return {"workers": self.worker_count, "queued": self._queue.qsize(), "jobs": counts}

    async def close(self) -> None:
        for task in self._workers:
            task.cancel()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear(); self._started = False
