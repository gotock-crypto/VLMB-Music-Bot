from services.provider_health import ProviderHealth

def test_provider_health_records_success_and_failure():
    h = ProviderHealth()
    h.record_success("vk", "search", 10, count=3)
    h.record_failure("vk", "search", 20, RuntimeError("boom"))
    snap = h.snapshot()["vk:search"]
    assert snap["success"] == 1
    assert snap["failure"] == 1
    assert snap["success_rate"] == 0.5
    assert snap["last_error"] == "boom"

def test_provider_health_format_is_human_readable():
    h = ProviderHealth()
    h.record_success("youtube", "download", 123)
    assert "youtube:download" in h.format_lines()[0]
