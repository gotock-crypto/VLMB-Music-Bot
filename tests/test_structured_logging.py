import json
import logging

from services.structured_logging import event_payload, log_event


def test_event_payload_contains_operational_fields_and_redacts_secrets():
    payload = event_payload(
        "download.completed",
        request_id="req-1",
        operation="download",
        provider="vk",
        duration_ms=12.345,
        status="ok",
        token="secret-token",
        nested={"api_key": "nested-secret", "value": 3},
    )
    assert payload["event"] == "download.completed"
    assert payload["duration_ms"] == 12.35
    assert payload["token"] == "<redacted>"
    assert payload["nested"]["api_key"] == "<redacted>"


def test_log_event_emits_json_without_secret(caplog):
    logger = logging.getLogger("vlmb-test")
    with caplog.at_level(logging.INFO, logger="vlmb-test"):
        log_event(logger, "auth.check", token="secret-token")
    record = caplog.records[-1]
    decoded = json.loads(record.message)
    assert decoded["token"] == "<redacted>"
    assert "secret-token" not in record.message
