from __future__ import annotations

import json

from app.utils.constants import HISTORY_FILE
from app.utils.path_utils import ensure_directory


class HistoryRepository:
    def load(self) -> dict:
        if not HISTORY_FILE.exists():
            return {"recent_tracks": [], "recent_streams": []}
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))

    def save(self, payload: dict) -> None:
        ensure_directory(HISTORY_FILE.parent)
        HISTORY_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
