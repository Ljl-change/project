from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class StreamItem:
    name: str
    url: str
    description: str = ""
    status: str = "idle"
    id: str = field(default_factory=lambda: uuid4().hex)
