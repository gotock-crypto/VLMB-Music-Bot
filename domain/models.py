"""Domain models used by the provider/application boundaries."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

@dataclass(frozen=True)
class Track:
    uid: str
    title: str
    artist: str = ""
    duration: Optional[int] = None
    source: str = ""
    url: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DownloadResult:
    uid: str
    path: str
    provider: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
