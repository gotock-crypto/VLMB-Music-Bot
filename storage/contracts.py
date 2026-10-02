"""Storage contracts used to peel persistence out of the Telegram core."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol

class UserStateStore(ABC):
    @abstractmethod
    async def set(self, user_id: int, state: str, data: Optional[dict[str, Any]] = None) -> None: ...
    @abstractmethod
    async def get(self, user_id: int) -> Optional[dict[str, Any]]: ...
    @abstractmethod
    async def clear(self, user_id: int) -> None: ...

class InMemoryUserStateStore(UserStateStore):
    def __init__(self):
        self._states: dict[int, dict[str, Any]] = {}
    async def set(self, user_id: int, state: str, data: Optional[dict[str, Any]] = None) -> None:
        self._states[user_id] = {"state": state, "data": dict(data or {})}
    async def get(self, user_id: int) -> Optional[dict[str, Any]]:
        value = self._states.get(user_id)
        return dict(value) if value else None
    async def clear(self, user_id: int) -> None:
        self._states.pop(user_id, None)
