import config


def test_redis_is_optional_by_default():
    assert config.REDIS_URL == "" or config.REDIS_URL.startswith("redis://")


def test_youtube_runtime_defaults_are_safe():
    assert config.YOUTUBE_JS_RUNTIME in ("deno", "node", "")
    assert config.YOUTUBE_PLAYER_CLIENTS
