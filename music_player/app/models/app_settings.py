from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppSettings:
    volume: int = 65
    play_mode: str = "loop"
    theme: str = "warm"
    last_track_id: str = ""
    last_playlist_id: str = ""
    last_position_ms: int = 0
    window_width: int = 980
    window_height: int = 760
