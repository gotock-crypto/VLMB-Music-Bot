"""Small explicit state machine for user interaction auditing.

The Telegram layer can remain backward compatible while transitions are
registered and tested independently of Telegram objects.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable
from domain.errors import InvalidTransition

@dataclass(frozen=True)
class Transition:
    source: str
    event: str
    target: str

class StateMachine:
    def __init__(self, transitions: Iterable[Transition], initial: str = "idle"):
        self.initial = initial
        self._map: Dict[tuple[str, str], Transition] = {}
        for t in transitions:
            key = (t.source, t.event)
            if key in self._map:
                raise ValueError(f"duplicate transition: {key}")
            self._map[key] = t

    def transition(self, state: str, event: str) -> str:
        try:
            return self._map[(state, event)].target
        except KeyError as exc:
            raise InvalidTransition(f"{state} --{event}--> ?") from exc

    def allowed_events(self, state: str) -> FrozenSet[str]:
        return frozenset(event for (source, event) in self._map if source == state)

    def transitions(self) -> tuple[Transition, ...]:
        return tuple(self._map.values())

# Critical user-facing flow states. The existing bot may carry richer state
# payloads; this machine models the lifecycle that must remain valid.
CRITICAL_TRANSITIONS = (
    Transition("idle", "search", "searching"),
    Transition("idle", "charts", "charts"),
    Transition("idle", "settings", "settings"),
    Transition("idle", "help", "help"),
    Transition("searching", "result", "results"),
    Transition("results", "download", "downloading"),
    Transition("downloading", "download_ok", "track_ready"),
    Transition("track_ready", "favorite_add", "favorite_ready"),
    Transition("favorite_ready", "favorite_remove", "track_ready"),
    Transition("favorite_ready", "history", "history"),
    Transition("track_ready", "history", "history"),
    Transition("history", "download", "downloading"),
    Transition("results", "similar", "similar"),
    Transition("similar", "search_artist", "searching"),
    Transition("searching", "back", "results"),
    Transition("similar", "back", "results"),
    Transition("results", "back", "idle"),
    Transition("history", "back", "idle"),
    Transition("favorite_ready", "back", "idle"),
    Transition("charts", "back", "idle"),
    Transition("settings", "back", "idle"),
    Transition("help", "back", "idle"),
    Transition("downloading", "download_failed", "results"),
)

critical_flow_machine = StateMachine(CRITICAL_TRANSITIONS)
