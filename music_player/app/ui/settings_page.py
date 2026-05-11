from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QSlider, QVBoxLayout, QWidget


class SettingsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("pageRoot")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(22, 22, 22, 22)
        hero_layout.setSpacing(10)

        title = QLabel("设置")
        title.setObjectName("heroTitle")
        desc = QLabel("这里先保留播放器基础设置，后续可以继续扩展主题、托盘、启动项等。")
        desc.setObjectName("heroMeta")
        hero_layout.addWidget(title)
        hero_layout.addWidget(desc)
        layout.addWidget(hero_card)

        card = QFrame()
        card.setObjectName("sectionCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(14)

        volume_title = QLabel("默认音量")
        volume_title.setObjectName("sectionTitle")
        volume_text = QLabel("拖动滑块调整应用启动和播放时的默认音量。")
        volume_text.setObjectName("softText")
        card_layout.addWidget(volume_title)
        card_layout.addWidget(volume_text)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(65)
        card_layout.addWidget(self.volume_slider)

        layout.addWidget(card)
        layout.addStretch()
