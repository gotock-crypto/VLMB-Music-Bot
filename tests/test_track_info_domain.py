from domain.track_info import TrackInfo, track_uid_from_any


def test_track_info_generates_canonical_provider_uid():
    track = TrackInfo(
        idx=0,
        track_id="123",
        title="Song",
        artist="Artist",
        album="",
        duration_sec=120,
        source="ym",
    )
    assert track.ensure_uid() == "ym:123"


def test_track_uid_helper_preserves_existing_uid():
    assert track_uid_from_any({"uid": "vk:audio123_456", "source": "vk"}) == "vk:audio123_456"


def test_track_uid_helper_uses_stable_hash_fallback():
    track = {"source": "vk", "artist": "Ария", "title": "Вулкан", "duration": 233}
    uid = track_uid_from_any(track)
    assert uid.startswith("h:")
    assert uid == track_uid_from_any(track)
