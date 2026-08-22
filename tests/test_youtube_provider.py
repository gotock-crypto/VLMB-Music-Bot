from services.youtube_provider import YoutubeMusicManager


def test_youtube_provider_builds_po_token_resistant_client_config(monkeypatch):
    monkeypatch.setattr("config.YOUTUBE_PLAYER_CLIENTS", "tv,web_safari", raising=False)
    mgr = YoutubeMusicManager()
    options = mgr._common_options()
    assert options["extractor_args"]["youtube"]["player_client"] == ["tv", "web_safari"]
