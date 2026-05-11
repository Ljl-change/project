from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Track:
    id: str
    title: str
    file_path: Path
    artist: str = ""
    album: str = ""
    duration_ms: int = 0
    cover_path: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "file_path": str(self.file_path),
            "artist": self.artist,
            "album": self.album,
            "duration_ms": self.duration_ms,
            "cover_path": self.cover_path,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "Track":
        return cls(
            id=payload["id"],
            title=payload["title"],
            file_path=Path(payload["file_path"]),
            artist=payload.get("artist", ""),
            album=payload.get("album", ""),
            duration_ms=payload.get("duration_ms", 0),
            cover_path=payload.get("cover_path", ""),
        )
