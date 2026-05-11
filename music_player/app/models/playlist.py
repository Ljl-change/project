from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from app.models.track import Track


@dataclass
class Playlist:
    name: str
    tracks: list[Track] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "tracks": [track.to_dict() for track in self.tracks],
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Playlist":
        return cls(
            id=payload.get("id", uuid4().hex),
            name=payload["name"],
            tracks=[Track.from_dict(item) for item in payload.get("tracks", [])],
        )
