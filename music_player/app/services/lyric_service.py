from __future__ import annotations

from pathlib import Path


class LyricService:
    def load_lyrics_for_track(self, audio_file_path: Path) -> list[str]:
        lyric_path = audio_file_path.with_suffix(".lrc")
        if not lyric_path.exists():
            return []

        lines = lyric_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        cleaned = [line.strip() for line in lines if line.strip()]
        return cleaned
