#!/usr/bin/env python3
"""Deterministic concurrency/queue smoke load test without external services."""
from __future__ import annotations
import argparse, asyncio, statistics, time

async def run(total: int, concurrency: int, work_ms: int):
    sem = asyncio.Semaphore(concurrency)
    waits=[]; durations=[]
    started = time.perf_counter()
    async def job(i):
        queued = time.perf_counter()
        async with sem:
            waits.append((time.perf_counter()-queued)*1000)
            t=time.perf_counter(); await asyncio.sleep(work_ms/1000); durations.append((time.perf_counter()-t)*1000)
    await asyncio.gather(*(job(i) for i in range(total)))
    elapsed=(time.perf_counter()-started)*1000
    p95=lambda xs: sorted(xs)[max(0, int(len(xs)*.95)-1)]
    print(f"jobs={total} concurrency={concurrency} elapsed_ms={elapsed:.1f} throughput/s={total/(elapsed/1000):.2f}")
    print(f"queue_wait_ms p50={statistics.median(waits):.1f} p95={p95(waits):.1f}; work_ms p50={statistics.median(durations):.1f} p95={p95(durations):.1f}")
    assert len(durations)==total
    assert max(waits) < max(1000.0, work_ms * (total/concurrency + 2) * 10)

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--jobs', type=int, default=100); p.add_argument('--concurrency', type=int, default=10); p.add_argument('--work-ms', type=int, default=20)
    a=p.parse_args(); asyncio.run(run(a.jobs, a.concurrency, a.work_ms))
