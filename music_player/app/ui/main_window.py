from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.music_page import MusicPage
from app.ui.settings_page import SettingsPage
from app.ui.stream_page import StreamPage
from app.utils.constants import APP_NAME


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1220, 900)
        self.setStyleSheet(
            """
            QMainWindow {
                background: #f7fae8;
            }
            QWidget {
                color: #30411b;
                font-family: 'Microsoft YaHei UI';
                font-size: 14px;
            }
            QFrame#shell {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #fbfdf2,
                    stop: 0.55 #f5f9df,
                    stop: 1 #ebf4c6
                );
            }
            QFrame#sidebar {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #bfdc72,
                    stop: 0.5 #abc95b,
                    stop: 1 #90b345
                );
                border-radius: 28px;
            }
            QFrame#contentShell {
                background: rgba(255, 255, 255, 0.42);
                border-radius: 30px;
            }
            QFrame#topBar, QFrame#playerBar {
                background: rgba(255, 255, 255, 0.74);
                border: 1px solid #dfebb0;
                border-radius: 22px;
            }
            QWidget#pageRoot {
                background: rgba(255, 255, 255, 0.28);
                border: 1px solid #e1edb2;
                border-radius: 26px;
            }
            QFrame#heroCard, QFrame#sectionCard, QFrame#coverCard {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid #dfebb0;
                border-radius: 22px;
            }
            QFrame#coverArt {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #d9ec97,
                    stop: 0.5 #bedf68,
                    stop: 1 #96b947
                );
                border-radius: 28px;
            }
            QFrame#videoCard {
                background: #29361a;
                border: 1px solid #98b856;
                border-radius: 22px;
            }
            QLabel#brandTitle {
                color: #f9ffef;
                font-size: 28px;
                font-weight: 900;
            }
            QLabel#brandMeta {
                color: #f2fbdd;
                font-size: 13px;
            }
            QLabel#heroTitle {
                font-size: 30px;
                font-weight: 800;
                color: #263915;
            }
            QLabel#heroMeta {
                font-size: 15px;
                color: #71854c;
            }
            QLabel#sectionTitle {
                font-size: 20px;
                font-weight: 800;
                color: #365018;
            }
            QLabel#softText {
                color: #748552;
            }
            QLabel#accentPill {
                background: #eef7c8;
                color: #506823;
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: 700;
            }
            QLabel#coverLetter {
                color: #fbfff1;
                font-size: 72px;
                font-weight: 900;
            }
            QLabel#coverMeta {
                color: #fbfff1;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton#navButton {
                background: transparent;
                color: #f7fde9;
                border: none;
                border-radius: 18px;
                text-align: left;
                padding: 14px 18px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton#navButton:hover {
                background: rgba(255, 255, 255, 0.20);
            }
            QPushButton#navButton[active="true"] {
                background: rgba(255, 255, 255, 0.92);
                color: #38501a;
            }
            QPushButton {
                background: #bfdc5a;
                color: #2c4112;
                border: none;
                border-radius: 16px;
                padding: 10px 16px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: #b0d04b;
            }
            QPushButton#ghostButton {
                background: #f0f6d8;
                color: #617935;
            }
            QPushButton#ghostButton:hover {
                background: #e7f0c8;
            }
            QPushButton#playerMini {
                background: #edf5d2;
                color: #445f1c;
                border-radius: 18px;
                min-width: 44px;
                max-width: 44px;
                min-height: 44px;
                max-height: 44px;
                padding: 0;
                font-size: 16px;
            }
            QLineEdit, QComboBox, QListWidget {
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid #dfebb0;
                border-radius: 16px;
                padding: 10px 12px;
            }
            QLineEdit:focus, QComboBox:focus, QListWidget:focus {
                border: 1px solid #a9c95b;
            }
            QListWidget::item {
                background: transparent;
                border-radius: 12px;
                padding: 10px 12px;
                margin: 4px 0;
            }
            QListWidget::item:selected {
                background: #eef7c6;
                color: #2b3d12;
            }
            QSlider::groove:horizontal {
                background: #dfe8bd;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #bbd95f;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #a2c14f;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            """
        )

        root = QWidget()
        self.setCentralWidget(root)

        outer = QHBoxLayout(root)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(18)

        shell = QFrame()
        shell.setObjectName("shell")
        outer.addWidget(shell)

        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(18, 18, 18, 18)
        shell_layout.setSpacing(18)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        shell_layout.addWidget(self.sidebar)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(22, 24, 22, 24)
        sidebar_layout.setSpacing(16)

        brand_title = QLabel("Aurora")
        brand_title.setObjectName("brandTitle")
        brand_meta = QLabel("左侧导航结构\n音乐、直播、设置一目了然")
        brand_meta.setObjectName("brandMeta")
        sidebar_layout.addWidget(brand_title)
        sidebar_layout.addWidget(brand_meta)

        self.music_nav_button = QPushButton("音乐空间")
        self.music_nav_button.setObjectName("navButton")
        self.stream_nav_button = QPushButton("直播频道")
        self.stream_nav_button.setObjectName("navButton")
        self.settings_nav_button = QPushButton("偏好设置")
        self.settings_nav_button.setObjectName("navButton")

        sidebar_layout.addSpacing(12)
        sidebar_layout.addWidget(self.music_nav_button)
        sidebar_layout.addWidget(self.stream_nav_button)
        sidebar_layout.addWidget(self.settings_nav_button)
        sidebar_layout.addStretch()

        footer_label = QLabel("浅黄绿色主题\n本地音乐播放器")
        footer_label.setObjectName("brandMeta")
        sidebar_layout.addWidget(footer_label)

        self.content_shell = QFrame()
        self.content_shell.setObjectName("contentShell")
        shell_layout.addWidget(self.content_shell, stretch=1)

        content_layout = QVBoxLayout(self.content_shell)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        self.top_bar = QFrame()
        self.top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(18, 14, 18, 14)
        top_layout.setSpacing(12)

        self.top_search_input = QLineEdit()
        self.top_search_input.setPlaceholderText("搜索歌曲、歌单或直播频道")
        self.quick_tag_label = QLabel("本地播放器")
        self.quick_tag_label.setObjectName("accentPill")
        self.user_label = QLabel("Aurora User")
        self.user_label.setObjectName("softText")
        top_layout.addWidget(self.top_search_input, stretch=1)
        top_layout.addWidget(self.quick_tag_label)
        top_layout.addWidget(self.user_label)
        content_layout.addWidget(self.top_bar)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, stretch=1)

        self.music_page = MusicPage()
        self.stream_page = StreamPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.music_page)
        self.stack.addWidget(self.stream_page)
        self.stack.addWidget(self.settings_page)

        self.player_bar = QFrame()
        self.player_bar.setObjectName("playerBar")
        player_bar_layout = QHBoxLayout(self.player_bar)
        player_bar_layout.setContentsMargins(18, 14, 18, 14)
        player_bar_layout.setSpacing(14)

        self.player_track_title = QLabel("还没有选择歌曲")
        self.player_track_title.setObjectName("sectionTitle")
        self.player_track_meta = QLabel("底部播放器条会同步当前播放信息")
        self.player_track_meta.setObjectName("softText")

        player_text_layout = QVBoxLayout()
        player_text_layout.setSpacing(4)
        player_text_layout.addWidget(self.player_track_title)
        player_text_layout.addWidget(self.player_track_meta)
        player_bar_layout.addLayout(player_text_layout, stretch=1)

        self.player_prev_button = QPushButton("⏮")
        self.player_prev_button.setObjectName("playerMini")
        self.player_play_button = QPushButton("▶")
        self.player_play_button.setObjectName("playerMini")
        self.player_next_button = QPushButton("⏭")
        self.player_next_button.setObjectName("playerMini")
        player_bar_layout.addWidget(self.player_prev_button)
        player_bar_layout.addWidget(self.player_play_button)
        player_bar_layout.addWidget(self.player_next_button)

        self.player_progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.player_progress_slider.setRange(0, 0)
        player_bar_layout.addWidget(self.player_progress_slider, stretch=2)

        self.player_time_label = QLabel("00:00 / 00:00")
        self.player_time_label.setObjectName("softText")
        player_bar_layout.addWidget(self.player_time_label)

        content_layout.addWidget(self.player_bar)

        self.music_nav_button.clicked.connect(lambda: self.set_current_page(0))
        self.stream_nav_button.clicked.connect(lambda: self.set_current_page(1))
        self.settings_nav_button.clicked.connect(lambda: self.set_current_page(2))
        self.set_current_page(0)

    def set_current_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self._set_nav_active(self.music_nav_button, index == 0)
        self._set_nav_active(self.stream_nav_button, index == 1)
        self._set_nav_active(self.settings_nav_button, index == 2)

    def _set_nav_active(self, button: QPushButton, active: bool) -> None:
        button.setProperty("active", active)
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        for callback in getattr(self, "_before_close_callbacks", []):
            callback()
        super().closeEvent(event)

    def register_before_close(self, callback) -> None:
        callbacks = getattr(self, "_before_close_callbacks", [])
        callbacks.append(callback)
        self._before_close_callbacks = callbacks
