from __future__ import annotations

import json

from app.models.playlist import Playlist
from app.utils.constants import PLAYLISTS_DIR
from app.utils.path_utils import ensure_directory


class PlaylistRepository:
    def list_all(self) -> list[Playlist]:
        ensure_directory(PLAYLISTS_DIR)
        playlists: list[Playlist] = []
        for path in sorted(PLAYLISTS_DIR.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            playlists.append(Playlist.from_dict(payload))
        return playlists

    def save(self, playlist: Playlist) -> None:
        ensure_directory(PLAYLISTS_DIR)
        target = PLAYLISTS_DIR / f"{playlist.id}.json"
        target.write_text(
            json.dumps(playlist.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def delete(self, playlist_id: str) -> None:
        target = PLAYLISTS_DIR / f"{playlist_id}.json"
        if target.exists():
            target.unlink()
