from services.search_scoring import rank_tracks_by_artist

def test_artist_first_order_is_stable():
    tracks = [
        {"artist": "Other", "title": "A"},
        {"artist": "Ария", "title": "B"},
        {"artist": "Ария Live", "title": "C"},
        {"artist": "Супер Ария", "title": "D"},
    ]
    ranked = rank_tracks_by_artist(tracks, "Ария - Штиль")
    assert [x["title"] for x in ranked] == ["B", "C", "D", "A"]

def test_empty_query_preserves_order():
    tracks = [{"artist": "b"}, {"artist": "a"}]
    assert rank_tracks_by_artist(tracks, "   ") == tracks
