from __future__ import annotations

import json

from app.models.stream_item import StreamItem
from app.utils.constants import DEMO_STREAMS_FILE


class StreamProbeService:
    def load_demo_streams(self) -> list[StreamItem]:
        if not DEMO_STREAMS_FILE.exists():
            return []

        raw_items = json.loads(DEMO_STREAMS_FILE.read_text(encoding="utf-8"))
        return [StreamItem(**item) for item in raw_items]
