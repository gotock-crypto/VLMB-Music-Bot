from services.search_engine import rank_tracks, score_track


def test_exact_artist_title_wins():
    rows = [
        {"artist": "Miyagi & Andy Panda", "title": "Captain", "source": "yt"},
        {"artist": "Miyagi", "title": "Captain", "source": "vk"},
        {"artist": "MiyaGi", "title": "Captain (Live)", "source": "ym"},
    ]
    ranked = rank_tracks(rows, "Miyagi Captain")
    assert ranked[0]["artist"] == "Miyagi"
    assert ranked[0]["title"] == "Captain"
    assert "_vlmb_score" in ranked[0]


def test_dedup_artist_title():
    rows = [
        {"artist": "Miyagi", "title": "Captain", "source": "vk", "url": "a"},
        {"artist": "Miyagi", "title": "Captain", "source": "yt", "url": "b"},
    ]
    assert len(rank_tracks(rows, "Miyagi Captain")) == 1
