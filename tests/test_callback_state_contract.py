from application.callbacks.catalog import CALLBACK_SPECS
from application.state.machine import critical_flow_machine


def test_callback_catalog_has_no_duplicate_prefixes():
    prefixes = [spec.prefix for spec in CALLBACK_SPECS]
    assert len(prefixes) == len(set(prefixes))


def test_critical_callback_events_are_known_to_the_state_machine_or_terminal():
    events = {spec.event for spec in CALLBACK_SPECS}
    machine_events = {event for t in critical_flow_machine.transitions() for event in (t.event,)}
    # History is represented by the histdl: callback, whose operation is download.
    assert {"search", "download", "favorite_add", "favorite_remove", "back"} <= events
    assert {"search", "download", "favorite_add", "favorite_remove", "history", "back"} <= machine_events
