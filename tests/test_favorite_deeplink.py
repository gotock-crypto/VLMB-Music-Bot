import sqlite3

import pytest

from music_bot_user_mixes import UserStore, _track_uid_from_any


@pytest.mark.asyncio
async def test_pending_favorite_roundtrip_and_consume(tmp_path):
    db = str(tmp_path / "user.db")
    store = UserStore(db)
    track = {
        "source": "vk",
        "vk_key": "audio123_456",
        "artist": "Ария",
        "title": "Вулкан",
        "duration": 233,
    }
    uid = _track_uid_from_any(track)

    await store.set_pending_favorite(42, uid, track)
    pending = await store.get_pending_favorite(42, max_age_seconds=300)

    assert pending is not None
    assert pending["uid"] == uid
    assert pending["artist"] == "Ария"
    assert pending["title"] == "Вулкан"

    # The pending record is consumed once, preventing duplicate /start actions.
    assert await store.get_pending_favorite(42, max_age_seconds=300) is None


@pytest.mark.asyncio
async def test_pending_favorite_expires(tmp_path):
    db = str(tmp_path / "user.db")
    store = UserStore(db)
    track = {"source": "yt", "youtube_id": "abc", "artist": "Artist", "title": "Song"}
    uid = _track_uid_from_any(track)
    await store.set_pending_favorite(7, uid, track)

    # Force an old timestamp to verify stale records are ignored.
    conn = sqlite3.connect(db)
    try:
        conn.execute("UPDATE user_pending_favorite SET ts=? WHERE user_id=?", (0, 7))
        conn.commit()
    finally:
        conn.close()

    assert await store.get_pending_favorite(7, max_age_seconds=300) is None


@pytest.mark.asyncio
async def test_downloaded_audio_favorite_button_uses_native_callback():
    from music_bot_user_mixes import _favorite_reply_markup

    track = {
        "source": "vk",
        "vk_key": "audio123_456",
        "artist": "Ария",
        "title": "Вулкан",
    }
    markup = await _favorite_reply_markup(None, track)
    assert markup is not None
    button = markup.inline_keyboard[0][0]
    assert button.text == "❤️ Добавить в избранное"
    assert button.callback_data.startswith("fav_audio:")
    assert button.url is None
    assert len(button.callback_data.encode("utf-8")) <= 64


@pytest.mark.asyncio
async def test_native_favorite_callback_preserves_provider_uid_and_matches_history(tmp_path):
    from music_bot_user_mixes import _favorite_reply_markup

    db = str(tmp_path / "user.db")
    store = UserStore(db)
    track = {
        "source": "vk",
        "vk_key": "audio123_456",
        "artist": "ASVR",
        "title": "Air",
    }
    uid = _track_uid_from_any(track)
    await store.add_history(42, uid, track)

    markup = await _favorite_reply_markup(None, track)
    callback = markup.inline_keyboard[0][0].callback_data
    callback_uid = callback.split(":", 1)[1]

    assert callback_uid == uid
    assert await store.get_history_track(42, callback_uid) is not None


@pytest.mark.asyncio
async def test_native_favorite_callback_preserves_hash_uid(tmp_path):
    from music_bot_user_mixes import _favorite_reply_markup

    track = {"source": "vk", "artist": "Ария", "title": "Вулкан", "duration": 233}
    uid = _track_uid_from_any(track)
    assert uid.startswith("h:")
    markup = await _favorite_reply_markup(None, track)
    callback_uid = markup.inline_keyboard[0][0].callback_data.split(":", 1)[1]
    assert callback_uid == uid
