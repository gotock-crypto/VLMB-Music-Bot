"""Small dependency-free structured logging helper.

The helper is intentionally independent of Telegram and providers. It emits one
JSON object per event and redacts common credential-bearing fields before output.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Mapping

_SENSITIVE_KEYS = {
    "token", "bot_token", "api_token", "access_token", "refresh_token",
    "password", "passwd", "secret", "api_key", "authorization", "cookie",
}


def _safe(value: Any, *, key: str = "") -> Any:
    if key.casefold() in _SENSITIVE_KEYS:
        return "<redacted>"
    if isinstance(value, Mapping):
        return {str(k): _safe(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    return value


def event_payload(
    event: str,
    *,
    operation: str = "",
    request_id: str = "",
    provider: str = "",
    duration_ms: float | None = None,
    status: str = "",
    error_type: str = "",
    **fields: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"event": str(event)}
    for key, value in {
        "operation": operation,
        "request_id": request_id,
        "provider": provider,
        "duration_ms": None if duration_ms is None else round(max(0.0, float(duration_ms)), 2),
        "status": status,
        "error_type": error_type,
        **fields,
    }.items():
        if value not in ("", None):
            payload[key] = _safe(value, key=key)
    return payload


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    """Emit a safe JSON event without exposing credential-like values."""
    logger.info(json.dumps(event_payload(event, **fields), ensure_ascii=False, sort_keys=True))
