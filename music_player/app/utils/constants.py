from __future__ import annotations

from pathlib import Path


APP_NAME = "Aurora Player"
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
PLAYLISTS_DIR = DATA_DIR / "playlists"
CACHE_DIR = DATA_DIR / "cache"
SETTINGS_FILE = DATA_DIR / "settings.json"
HISTORY_FILE = DATA_DIR / "history.json"
ASSETS_DIR = BASE_DIR / "assets"
DEMO_STREAMS_FILE = ASSETS_DIR / "demo_streams.json"
