from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.video_panel import VideoPanel


class StreamPage(QWidget):
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

        self.title_label = QLabel("流媒体直播")
        self.title_label.setObjectName("heroTitle")
        self.stream_name_label = QLabel("当前没有选中直播源")
        self.stream_name_label.setObjectName("sectionTitle")
        self.status_label = QLabel("后续这里会显示探测、缓冲和播放状态。")
        self.status_label.setObjectName("heroMeta")
        hero_layout.addWidget(self.title_label)
        hero_layout.addWidget(self.stream_name_label)
        hero_layout.addWidget(self.status_label)
        layout.addWidget(hero_card)

        video_card = QFrame()
        video_card.setObjectName("sectionCard")
        video_layout = QVBoxLayout(video_card)
        video_layout.setContentsMargins(20, 20, 20, 20)
        video_layout.setSpacing(14)

        video_title = QLabel("视频画面")
        video_title.setObjectName("sectionTitle")
        video_layout.addWidget(video_title)

        video_shell = QFrame()
        video_shell.setObjectName("videoCard")
        video_shell_layout = QVBoxLayout(video_shell)
        video_shell_layout.setContentsMargins(10, 10, 10, 10)
        self.video_panel = VideoPanel()
        self.video_panel.setMinimumHeight(320)
        video_shell_layout.addWidget(self.video_panel)
        video_layout.addWidget(video_shell)

        self.stream_list = QListWidget()
        video_layout.addWidget(self.stream_list)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/live-stream.m3u8")
        video_layout.addWidget(self.url_input)

        button_row = QHBoxLayout()
        self.detect_button = QPushButton("检测示例源")
        self.detect_button.setObjectName("ghostButton")
        self.load_button = QPushButton("载入选中项")
        self.play_button = QPushButton("播放直播")
        self.stop_button = QPushButton("停止直播")
        self.stop_button.setObjectName("ghostButton")
        button_row.addWidget(self.detect_button)
        button_row.addWidget(self.load_button)
        button_row.addWidget(self.play_button)
        button_row.addWidget(self.stop_button)
        video_layout.addLayout(button_row)

        layout.addWidget(video_card, stretch=1)
