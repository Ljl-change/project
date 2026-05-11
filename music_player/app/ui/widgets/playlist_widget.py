from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QListWidget


class PlaylistWidget(QListWidget):
    order_changed = pyqtSignal(list)
    track_menu_requested = pyqtSignal(str, object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._emit_track_menu_request)

    def dropEvent(self, event) -> None:  # type: ignore[override]
        super().dropEvent(event)
        ordered_ids = []
        for row in range(self.count()):
            item = self.item(row)
            ordered_ids.append(item.data(256))
        self.order_changed.emit(ordered_ids)

    def _emit_track_menu_request(self, position) -> None:
        item = self.itemAt(position)
        if item is None:
            return
        track_id = item.data(256)
        if not track_id:
            return
        self.track_menu_requested.emit(track_id, self.viewport().mapToGlobal(position))
