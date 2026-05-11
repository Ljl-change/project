from __future__ import annotations

from pathlib import Path


class LibraryController:
    SUPPORTED_EXTENSIONS = {".mp3", ".ogg", ".wav", ".flac", ".m4a", ".aac"}

    def scan_folder(self, folder_path: Path) -> list[Path]:
        if not folder_path.exists() or not folder_path.is_dir():
            return []

        tracks: list[Path] = []
        for path in folder_path.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                tracks.append(path)

        tracks.sort(key=lambda item: item.name.lower())
        return tracks
