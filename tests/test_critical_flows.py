from application.state.machine import critical_flow_machine


def run(events):
    state = "idle"
    for event in events:
        state = critical_flow_machine.transition(state, event)
    return state


def test_search_download_favorite_remove():
    assert run(["search", "result", "download", "download_ok", "favorite_add", "favorite_remove"]) == "track_ready"


def test_search_similar_search_back():
    assert run(["search", "result", "similar", "search_artist", "result", "back"]) == "idle"


def test_history_redownload():
    assert run(["search", "result", "download", "download_ok", "history", "download"]) == "downloading"


def test_download_failure_returns_to_results():
    assert run(["search", "result", "download", "download_failed"]) == "results"


def test_charts_back_to_main_menu():
    assert run(["charts", "back"]) == "idle"


def test_settings_back_to_main_menu():
    assert run(["settings", "back"]) == "idle"


def test_help_back_to_main_menu():
    assert run(["help", "back"]) == "idle"
