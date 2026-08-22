import pytest
from application.state.machine import critical_flow_machine
from domain.errors import InvalidTransition

def test_critical_download_favorite_history_flow():
    s = "idle"
    for event, expected in [
        ("search", "searching"), ("result", "results"),
        ("download", "downloading"), ("download_ok", "track_ready"),
        ("favorite_add", "favorite_ready"), ("history", "history"),
        ("download", "downloading"),
    ]:
        s = critical_flow_machine.transition(s, event)
        assert s == expected

def test_similar_back_flow():
    s = critical_flow_machine.transition("results", "similar")
    s = critical_flow_machine.transition(s, "back")
    assert s == "results"

def test_invalid_transition_is_explicit():
    with pytest.raises(InvalidTransition):
        critical_flow_machine.transition("idle", "favorite_remove")
