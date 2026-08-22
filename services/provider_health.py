"""In-process provider health metrics with zero external dependencies."""

from collections import defaultdict
from dataclasses import dataclass
from time import monotonic
import re
from typing import Any, Dict, Optional


@dataclass
class _Counter:
    success: int = 0
    failure: int = 0
    total_latency_ms: float = 0.0
    last_latency_ms: float = 0.0
    last_success_ts: Optional[float] = None
    last_failure_ts: Optional[float] = None
    last_error: str = ""
    consecutive_failures: int = 0
    last_count: int = 0

    @property
    def total(self) -> int:
        return self.success + self.failure

    @property
    def success_rate(self) -> float:
        return self.success / self.total if self.total else 0.0


class ProviderHealth:
    """Track search/download reliability without changing provider behavior."""

    def __init__(self) -> None:
        self._data: Dict[str, _Counter] = defaultdict(_Counter)

    def record_success(self, provider: str, operation: str, latency_ms: float, count: int = 0) -> None:
        c = self._data[f"{provider}:{operation}"]
        c.success += 1
        c.total_latency_ms += max(0.0, float(latency_ms))
        c.last_latency_ms = max(0.0, float(latency_ms))
        c.last_success_ts = monotonic()
        c.consecutive_failures = 0
        c.last_count = int(count or 0)

    def record_failure(self, provider: str, operation: str, latency_ms: float, error: Any) -> None:
        c = self._data[f"{provider}:{operation}"]
        c.failure += 1
        c.total_latency_ms += max(0.0, float(latency_ms))
        c.last_latency_ms = max(0.0, float(latency_ms))
        c.last_failure_ts = monotonic()
        c.consecutive_failures += 1
        c.last_error = re.sub(r"https?://\S+", "<url>", str(error or ""))[:240]

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        now = monotonic()
        out: Dict[str, Dict[str, Any]] = {}
        for key, c in self._data.items():
            out[key] = {
                "success": c.success,
                "failure": c.failure,
                "total": c.total,
                "success_rate": c.success_rate,
                "avg_latency_ms": (c.total_latency_ms / c.total) if c.total else 0.0,
                "last_latency_ms": c.last_latency_ms,
                "last_success_age_s": None if c.last_success_ts is None else max(0.0, now - c.last_success_ts),
                "last_failure_age_s": None if c.last_failure_ts is None else max(0.0, now - c.last_failure_ts),
                "consecutive_failures": c.consecutive_failures,
                "last_error": c.last_error,
                "last_count": c.last_count,
            }
        return out

    def format_lines(self) -> list[str]:
        lines = []
        for key, item in sorted(self.snapshot().items()):
            lines.append(
                f"  {key}: {item['success']}/{item['total']} ok="
                f"{item['success_rate']:.1%}, avg={item['avg_latency_ms']:.0f}ms, "
                f"last={item['last_latency_ms']:.0f}ms, consecutive_failures={item['consecutive_failures']}"
            )
            if item["last_error"]:
                lines.append(f"    last_error={item['last_error']}")
        return lines
