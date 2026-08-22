"""Low-overhead application metrics for searches, downloads and providers."""
from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict, deque
from typing import Any, Dict


class MetricsRegistry:
    def __init__(self, max_latency_samples: int = 5000):
        self.started_at = time.time()
        self.counters = defaultdict(int)
        self.latencies = defaultdict(lambda: deque(maxlen=max_latency_samples))
        self._lock = asyncio.Lock()

    async def inc(self, name: str, value: int = 1) -> None:
        async with self._lock:
            self.counters[name] += int(value)

    async def observe(self, name: str, seconds: float) -> None:
        async with self._lock:
            self.latencies[name].append(max(0.0, float(seconds)))

    async def record(self, name: str, *, ok: bool, seconds: float) -> None:
        await self.inc(f"{name}.total")
        await self.inc(f"{name}.success" if ok else f"{name}.errors")
        await self.observe(name, seconds)

    async def snapshot(self) -> Dict[str, Any]:
        async with self._lock:
            lat = {}
            for name, samples in self.latencies.items():
                values = sorted(samples)
                if values:
                    def pct(p: float) -> float:
                        idx = min(len(values)-1, max(0, int(round((len(values)-1)*p))))
                        return round(values[idx], 4)
                    lat[name] = {
                        "count": len(values),
                        "avg": round(sum(values)/len(values), 4),
                        "p50": pct(.50), "p95": pct(.95), "p99": pct(.99),
                    }
            return {
                "uptime_s": round(max(0.0, time.time() - self.started_at), 1),
                "counters": dict(self.counters),
                "latency": lat,
            }

    async def to_json(self) -> str:
        return json.dumps(await self.snapshot(), ensure_ascii=False, sort_keys=True)
