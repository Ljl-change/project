from __future__ import annotations

from PyQt6.QtWidgets import QLabel


class LyricWidget(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__("歌词区预留", parent)
        self.setWordWrap(True)

    def set_lyrics(self, lines: list[str]) -> None:
        if not lines:
            self.setText("当前歌曲没有找到本地 .lrc 歌词。")
            return
        self.setText("\n".join(lines[:12]))
