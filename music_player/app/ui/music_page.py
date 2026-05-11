from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.lyric_widget import LyricWidget
from app.ui.widgets.playlist_widget import PlaylistWidget


class MusicPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("pageRoot")

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(18)

        left_column = QVBoxLayout()
        left_column.setSpacing(16)
        root_layout.addLayout(left_column, stretch=7)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(22, 22, 22, 22)
        hero_layout.setSpacing(10)

        self.title_label = QLabel("我的音乐空间")
        self.title_label.setObjectName("heroTitle")
        self.current_track_label = QLabel("当前没有播放歌曲")
        self.current_track_label.setObjectName("sectionTitle")
        self.track_meta_label = QLabel("把常听的歌整理进歌单，播放、搜索、排序都已经接好了。")
        self.track_meta_label.setObjectName("heroMeta")
        hero_layout.addWidget(self.title_label)
        hero_layout.addWidget(self.current_track_label)
        hero_layout.addWidget(self.track_meta_label)
        left_column.addWidget(hero_card)

        playlist_card = QFrame()
        playlist_card.setObjectName("sectionCard")
        playlist_layout = QVBoxLayout(playlist_card)
        playlist_layout.setContentsMargins(20, 20, 20, 20)
        playlist_layout.setSpacing(14)

        playlist_header = QHBoxLayout()
        playlist_title = QLabel("歌单管理")
        playlist_title.setObjectName("sectionTitle")
        playlist_hint = QLabel("支持新建、重命名、删除和拖拽排序")
        playlist_hint.setObjectName("accentPill")
        playlist_header.addWidget(playlist_title)
        playlist_header.addStretch()
        playlist_header.addWidget(playlist_hint)
        playlist_layout.addLayout(playlist_header)

        playlist_row = QHBoxLayout()
        self.playlist_selector = QComboBox()
        self.new_playlist_input = QLineEdit()
        self.new_playlist_input.setPlaceholderText("输入新歌单名称")
        self.create_playlist_button = QPushButton("新建歌单")
        self.rename_playlist_button = QPushButton("重命名歌单")
        self.rename_playlist_button.setObjectName("ghostButton")
        self.delete_playlist_button = QPushButton("删除歌单")
        self.delete_playlist_button.setObjectName("ghostButton")
        playlist_row.addWidget(self.playlist_selector, stretch=1)
        playlist_row.addWidget(self.new_playlist_input, stretch=1)
        playlist_row.addWidget(self.create_playlist_button)
        playlist_row.addWidget(self.rename_playlist_button)
        playlist_row.addWidget(self.delete_playlist_button)
        playlist_layout.addLayout(playlist_row)

        mode_row = QHBoxLayout()
        self.play_mode_label = QLabel("播放模式")
        self.play_mode_label.setObjectName("softText")
        self.play_mode_selector = QComboBox()
        self.play_mode_selector.addItem("列表循环", "loop")
        self.play_mode_selector.addItem("单曲循环", "single")
        self.play_mode_selector.addItem("随机播放", "shuffle")
        mode_row.addWidget(self.play_mode_label)
        mode_row.addWidget(self.play_mode_selector)
        mode_row.addStretch()
        playlist_layout.addLayout(mode_row)

        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索当前歌单中的歌曲")
        self.clear_search_button = QPushButton("清空搜索")
        self.clear_search_button.setObjectName("ghostButton")
        search_row.addWidget(self.search_input, stretch=1)
        search_row.addWidget(self.clear_search_button)
        playlist_layout.addLayout(search_row)

        left_column.addWidget(playlist_card)

        player_card = QFrame()
        player_card.setObjectName("sectionCard")
        player_layout = QVBoxLayout(player_card)
        player_layout.setContentsMargins(20, 20, 20, 20)
        player_layout.setSpacing(14)

        player_title = QLabel("播放控制")
        player_title.setObjectName("sectionTitle")
        player_layout.addWidget(player_title)

        progress_row = QHBoxLayout()
        self.play_button = QPushButton("播放")
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        progress_row.addWidget(self.play_button)
        progress_row.addWidget(self.progress_slider, stretch=1)
        player_layout.addLayout(progress_row)

        time_row = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setObjectName("softText")
        self.duration_label = QLabel("00:00")
        self.duration_label.setObjectName("softText")
        time_row.addWidget(self.current_time_label)
        time_row.addStretch()
        time_row.addWidget(self.duration_label)
        player_layout.addLayout(time_row)

        control_row = QHBoxLayout()
        self.add_button = QPushButton("添加歌曲")
        self.import_folder_button = QPushButton("导入文件夹")
        self.remove_track_button = QPushButton("移除歌曲")
        self.import_folder_button.setObjectName("ghostButton")
        self.remove_track_button.setObjectName("ghostButton")
        self.prev_button = QPushButton("上一首")
        self.prev_button.setObjectName("ghostButton")
        self.next_button = QPushButton("下一首")
        self.next_button.setObjectName("ghostButton")
        control_row.addWidget(self.add_button)
        control_row.addWidget(self.import_folder_button)
        control_row.addWidget(self.remove_track_button)
        control_row.addWidget(self.prev_button)
        control_row.addWidget(self.next_button)
        player_layout.addLayout(control_row)

        self.playlist_widget = PlaylistWidget()
        player_layout.addWidget(self.playlist_widget, stretch=1)
        left_column.addWidget(player_card, stretch=1)

        right_column = QVBoxLayout()
        right_column.setSpacing(16)
        root_layout.addLayout(right_column, stretch=3)

        cover_card = QFrame()
        cover_card.setObjectName("coverCard")
        cover_layout = QVBoxLayout(cover_card)
        cover_layout.setContentsMargins(20, 20, 20, 20)
        cover_layout.setSpacing(14)

        cover_title = QLabel("正在播放")
        cover_title.setObjectName("sectionTitle")
        cover_layout.addWidget(cover_title)

        self.cover_art = QFrame()
        self.cover_art.setObjectName("coverArt")
        cover_art_layout = QVBoxLayout(self.cover_art)
        cover_art_layout.setContentsMargins(20, 20, 20, 20)
        cover_art_layout.setSpacing(8)
        cover_art_layout.addStretch()
        self.cover_image = QLabel()
        self.cover_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_image.setScaledContents(False)
        self.cover_image.hide()
        self.cover_letter = QLabel("A")
        self.cover_letter.setObjectName("coverLetter")
        self.cover_letter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_meta = QLabel("Aurora Player")
        self.cover_meta.setObjectName("coverMeta")
        self.cover_meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover_art_layout.addWidget(self.cover_image)
        cover_art_layout.addWidget(self.cover_letter)
        cover_art_layout.addWidget(self.cover_meta)
        cover_art_layout.addStretch()
        self.cover_art.setMinimumHeight(260)
        cover_layout.addWidget(self.cover_art)

        self.now_playing_title = QLabel("还没有选择歌曲")
        self.now_playing_title.setObjectName("sectionTitle")
        self.now_playing_meta = QLabel("选中一首歌后，这里会显示播放中的曲目信息。")
        self.now_playing_meta.setObjectName("heroMeta")
        self.play_mode_badge = QLabel("列表循环")
        self.play_mode_badge.setObjectName("accentPill")
        cover_layout.addWidget(self.now_playing_title)
        cover_layout.addWidget(self.now_playing_meta)
        cover_layout.addWidget(self.play_mode_badge)
        cover_layout.addStretch()
        right_column.addWidget(cover_card)

        stat_card = QFrame()
        stat_card.setObjectName("sectionCard")
        stat_layout = QVBoxLayout(stat_card)
        stat_layout.setContentsMargins(20, 20, 20, 20)
        stat_layout.setSpacing(10)

        stat_title = QLabel("快速信息")
        stat_title.setObjectName("sectionTitle")
        stat_layout.addWidget(stat_title)

        self.playlist_count_label = QLabel("歌单数: 0")
        self.playlist_count_label.setObjectName("softText")
        self.track_count_label = QLabel("当前歌单歌曲数: 0")
        self.track_count_label.setObjectName("softText")
        self.search_state_label = QLabel("当前未启用搜索过滤")
        self.search_state_label.setObjectName("softText")
        stat_layout.addWidget(self.playlist_count_label)
        stat_layout.addWidget(self.track_count_label)
        stat_layout.addWidget(self.search_state_label)
        stat_layout.addStretch()
        right_column.addWidget(stat_card, stretch=1)

        lyric_card = QFrame()
        lyric_card.setObjectName("sectionCard")
        lyric_layout = QVBoxLayout(lyric_card)
        lyric_layout.setContentsMargins(20, 20, 20, 20)
        lyric_layout.setSpacing(10)

        lyric_title = QLabel("本地歌词")
        lyric_title.setObjectName("sectionTitle")
        lyric_layout.addWidget(lyric_title)

        self.lyric_widget = LyricWidget()
        self.lyric_widget.setObjectName("softText")
        lyric_layout.addWidget(self.lyric_widget)

        right_column.addWidget(lyric_card, stretch=1)

    def set_cover_pixmap(self, pixmap: QPixmap | None) -> None:
        if pixmap is None or pixmap.isNull():
            self.cover_image.clear()
            self.cover_image.hide()
            self.cover_letter.show()
            self.cover_meta.show()
            return

        scaled = pixmap.scaled(
            210,
            210,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.cover_image.setPixmap(scaled)
        self.cover_image.show()
        self.cover_letter.hide()
        self.cover_meta.hide()
