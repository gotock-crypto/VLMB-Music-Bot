from services.playlist_manager import PlaylistManager


def test_manager_constructs():
    m = PlaylistManager(1)
    assert m.executor is not None
    m.executor.shutdown(wait=False, cancel_futures=True)
