from __future__ import annotations

import random
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem, QMessageBox

from app.controllers.library_controller import LibraryController
from app.models.app_settings import AppSettings
from app.models.playlist import Playlist
from app.models.track import Track
from app.services.audio_service import AudioService
from app.services.lyric_service import LyricService
from app.services.metadata_service import MetadataService
from app.services.playlist_service import PlaylistService
from app.ui.music_page import MusicPage
from app.utils.time_utils import format_milliseconds


class PlayerController:
    def __init__(
        self,
        page: MusicPage,
        audio_service: AudioService,
        metadata_service: MetadataService,
        playlist_service: PlaylistService,
        library_controller: LibraryController,
        lyric_service: LyricService,
    ) -> None:
        self.page = page
        self.audio_service = audio_service
        self.metadata_service = metadata_service
        self.playlist_service = playlist_service
        self.library_controller = library_controller
        self.lyric_service = lyric_service
        self.playlists: list[Playlist] = self.playlist_service.load_playlists()
        self.current_playlist_index = 0
        self.current_track_index = -1
        self.filtered_track_indices: list[int] = []
        self.is_dragging_slider = False
        self.pending_restore_position = 0
        self.play_mode = "loop"

        self.page.add_button.clicked.connect(self.add_tracks)
        self.page.import_folder_button.clicked.connect(self.import_folder)
        self.page.remove_track_button.clicked.connect(self.remove_selected_track)
        self.page.create_playlist_button.clicked.connect(self.create_playlist)
        self.page.rename_playlist_button.clicked.connect(self.rename_current_playlist)
        self.page.delete_playlist_button.clicked.connect(self.delete_current_playlist)
        self.page.playlist_selector.currentIndexChanged.connect(self.switch_playlist)
        self.page.play_mode_selector.currentIndexChanged.connect(self.change_play_mode)
        self.page.search_input.textChanged.connect(self.apply_search_filter)
        self.page.clear_search_button.clicked.connect(self.clear_search)
        self.page.play_button.clicked.connect(self.toggle_playback)
        self.page.prev_button.clicked.connect(self.play_previous)
        self.page.next_button.clicked.connect(self.play_next)
        self.page.playlist_widget.itemDoubleClicked.connect(self.play_selected_track)
        self.page.playlist_widget.order_changed.connect(self.reorder_current_playlist)
        self.page.playlist_widget.track_menu_requested.connect(self.show_track_context_menu)
        self.page.progress_slider.sliderPressed.connect(self.begin_slider_drag)
        self.page.progress_slider.sliderReleased.connect(self.seek_position)

        self.audio_service.player.positionChanged.connect(self.update_position)
        self.audio_service.player.durationChanged.connect(self.update_duration)
        self.audio_service.player.playbackStateChanged.connect(self.update_play_button)
        self.audio_service.player.mediaStatusChanged.connect(self.handle_media_status)

        self._refresh_playlist_selector()
        self.switch_playlist(0)
        self._update_sidebar_summary()
        self._update_play_mode_badge()

    @property
    def current_playlist(self) -> Playlist:
        return self.playlists[self.current_playlist_index]

    def create_playlist(self) -> None:
        name = self.page.new_playlist_input.text().strip() or "新歌单"
        playlist = self.playlist_service.create_playlist(name)
        self.playlists.append(playlist)
        self._refresh_playlist_selector()
        self.page.playlist_selector.setCurrentIndex(len(self.playlists) - 1)
        self.page.new_playlist_input.clear()
        self._update_sidebar_summary()

    def rename_current_playlist(self) -> None:
        name = self.page.new_playlist_input.text().strip()
        if not name:
            QMessageBox.information(self.page, "提示", "请先输入新的歌单名称。")
            return

        updated_playlist = self.playlist_service.rename_playlist(self.current_playlist, name)
        self.playlists[self.current_playlist_index] = updated_playlist
        self._refresh_playlist_selector()
        self.page.playlist_selector.setCurrentIndex(self.current_playlist_index)
        self.page.new_playlist_input.clear()
        self._update_sidebar_summary()

    def delete_current_playlist(self) -> None:
        if len(self.playlists) <= 1:
            QMessageBox.information(self.page, "提示", "至少保留一个歌单。")
            return

        playlist = self.current_playlist
        self.playlist_service.delete_playlist(playlist.id)
        del self.playlists[self.current_playlist_index]
        self.current_playlist_index = max(0, self.current_playlist_index - 1)
        self.current_track_index = -1
        self._refresh_playlist_selector()
        self.page.playlist_selector.setCurrentIndex(self.current_playlist_index)
        self._update_sidebar_summary()

    def add_tracks(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self.page,
            "选择音频文件",
            "",
            "音频文件 (*.mp3 *.ogg *.wav *.flac *.m4a *.aac)",
        )
        self._add_paths_to_current_playlist([Path(file_name) for file_name in files])

    def import_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self.page, "选择音乐文件夹")
        if not folder:
            return
        paths = self.library_controller.scan_folder(Path(folder))
        self._add_paths_to_current_playlist(paths)

    def _add_paths_to_current_playlist(self, paths: list[Path]) -> None:
        tracks = [self.metadata_service.build_track_from_path(path) for path in paths]
        if not tracks:
            return

        updated_playlist = self.playlist_service.add_tracks(self.current_playlist, tracks)
        self.playlists[self.current_playlist_index] = updated_playlist
        self._refresh_track_list()
        self._update_sidebar_summary()

        if self.current_track_index == -1 and updated_playlist.tracks:
            self.load_track(0)

    def remove_selected_track(self) -> None:
        filtered_row = self.page.playlist_widget.currentRow()
        row = self._filtered_row_to_track_index(filtered_row)
        if row is None:
            return
        self.remove_track_by_index(row)

    def remove_track_by_index(self, row: int) -> None:
        if not 0 <= row < len(self.current_playlist.tracks):
            return

        del self.current_playlist.tracks[row]
        self.playlist_service.save_playlist(self.current_playlist)
        if self.current_track_index == row:
            self.audio_service.stop()
            self.current_track_index = -1
            self._reset_now_playing_panel("当前没有播放歌曲", "可以添加新歌曲，或切换到其他歌单。")
        elif self.current_track_index > row:
            self.current_track_index -= 1

        self._refresh_track_list()
        self._update_sidebar_summary()

    def reorder_current_playlist(self, ordered_track_ids: list[str]) -> None:
        if self.page.search_input.text().strip():
            return

        current_track_id = ""
        if 0 <= self.current_track_index < len(self.current_playlist.tracks):
            current_track_id = self.current_playlist.tracks[self.current_track_index].id

        updated_playlist = self.playlist_service.reorder_tracks(self.current_playlist, ordered_track_ids)
        self.playlists[self.current_playlist_index] = updated_playlist

        if current_track_id:
            self.current_track_index = self._find_track_index_by_id(current_track_id)
        self._refresh_track_list()
        self._update_sidebar_summary()

    def switch_playlist(self, index: int) -> None:
        if not 0 <= index < len(self.playlists):
            return

        self.current_playlist_index = index
        self.current_track_index = -1
        self.clear_search()
        self._refresh_track_list()
        self._update_sidebar_summary()
        playlist = self.current_playlist
        if playlist.tracks:
            self.load_track(0)
        else:
            self._reset_now_playing_panel(
                "当前歌单没有歌曲",
                "点击“添加歌曲”或“导入文件夹”导入本地音频。",
            )

    def change_play_mode(self) -> None:
        self.play_mode = self.page.play_mode_selector.currentData() or "loop"
        self._update_play_mode_badge()

    def clear_search(self) -> None:
        self.page.search_input.blockSignals(True)
        self.page.search_input.clear()
        self.page.search_input.blockSignals(False)
        self.apply_search_filter("")

    def apply_search_filter(self, text: str) -> None:
        keyword = text.strip().lower()
        self.filtered_track_indices.clear()
        self.page.playlist_widget.clear()

        allow_reorder = not keyword
        mode = (
            self.page.playlist_widget.DragDropMode.InternalMove
            if allow_reorder
            else self.page.playlist_widget.DragDropMode.NoDragDrop
        )
        self.page.playlist_widget.setDragDropMode(mode)
        self.page.playlist_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.page.playlist_widget.setDragEnabled(allow_reorder)
        self.page.playlist_widget.setAcceptDrops(allow_reorder)
        self.page.playlist_widget.viewport().setAcceptDrops(allow_reorder)
        self.page.playlist_widget.setDropIndicatorShown(allow_reorder)

        for index, track in enumerate(self.current_playlist.tracks):
            haystack = " ".join(
                [
                    track.title,
                    track.artist,
                    track.album,
                    track.file_path.name,
                ]
            ).lower()
            if keyword and keyword not in haystack:
                continue

            self.filtered_track_indices.append(index)
            item = QListWidgetItem(track.title)
            item.setData(256, track.id)
            self.page.playlist_widget.addItem(item)

        if self.current_track_index in self.filtered_track_indices:
            filtered_row = self.filtered_track_indices.index(self.current_track_index)
            self.page.playlist_widget.setCurrentRow(filtered_row)
        self._update_sidebar_summary()

    def load_track(self, index: int, restore_position: int = 0) -> None:
        if not 0 <= index < len(self.current_playlist.tracks):
            return

        self.current_track_index = index
        track = self.current_playlist.tracks[index]
        self.audio_service.load_local_track(track.file_path)
        self.page.current_track_label.setText(track.title)
        self.page.track_meta_label.setText(self._build_track_description(track))
        self.page.now_playing_title.setText(track.title)
        self.page.now_playing_meta.setText(self._build_now_playing_meta(track))
        self.page.cover_letter.setText(track.title[:1].upper())
        self.page.cover_meta.setText(track.artist or track.album or "Local Track")
        self._update_cover_art(track)
        self.page.lyric_widget.set_lyrics(self.lyric_service.load_lyrics_for_track(track.file_path))
        if index in self.filtered_track_indices:
            self.page.playlist_widget.setCurrentRow(self.filtered_track_indices.index(index))
        self.pending_restore_position = restore_position

    def current_track(self) -> Track | None:
        if not 0 <= self.current_track_index < len(self.current_playlist.tracks):
            return None
        return self.current_playlist.tracks[self.current_track_index]

    def play_selected_track(self, item) -> None:
        filtered_row = self.page.playlist_widget.row(item)
        track_index = self._filtered_row_to_track_index(filtered_row)
        if track_index is None:
            return
        self.load_track(track_index)
        self.audio_service.play()

    def toggle_playback(self) -> None:
        if not self.current_playlist.tracks:
            QMessageBox.information(self.page, "提示", "当前歌单还没有歌曲。")
            return

        if self.current_track_index == -1:
            target_index = self.filtered_track_indices[0] if self.filtered_track_indices else 0
            self.load_track(target_index)

        state = self.audio_service.player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.audio_service.pause()
        else:
            self.audio_service.play()

    def play_previous(self) -> None:
        target_index = self._resolve_previous_index()
        if target_index is None:
            return
        self.load_track(target_index)
        self.audio_service.play()

    def play_next(self) -> None:
        target_index = self._resolve_next_index()
        if target_index is None:
            return
        self.load_track(target_index)
        self.audio_service.play()

    def update_position(self, position: int) -> None:
        if not self.is_dragging_slider:
            self.page.progress_slider.setValue(position)
        self.page.current_time_label.setText(format_milliseconds(position))

    def update_duration(self, duration: int) -> None:
        self.page.progress_slider.setRange(0, max(duration, 0))
        self.page.duration_label.setText(format_milliseconds(duration))
        if self.pending_restore_position > 0 and duration > 0:
            self.audio_service.set_position(min(self.pending_restore_position, duration))
            self.pending_restore_position = 0

    def begin_slider_drag(self) -> None:
        self.is_dragging_slider = True

    def seek_position(self) -> None:
        self.is_dragging_slider = False
        self.audio_service.set_position(self.page.progress_slider.value())

    def update_play_button(self, state: QMediaPlayer.PlaybackState) -> None:
        self.page.play_button.setText("暂停" if state == QMediaPlayer.PlaybackState.PlayingState else "播放")

    def handle_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        if status != QMediaPlayer.MediaStatus.EndOfMedia or not self.current_playlist.tracks:
            return

        if self.play_mode == "single":
            self.load_track(self.current_track_index)
            self.audio_service.play()
            return

        self.play_next()

    def show_track_context_menu(self, track_id: str, global_pos) -> None:
        track = self._find_track_by_id(track_id)
        if track is None:
            return

        from PyQt6.QtWidgets import QApplication, QMenu

        menu = QMenu(self.page)
        play_action = menu.addAction("播放所选")
        remove_action = menu.addAction("移除歌曲")
        open_folder_action = menu.addAction("打开所在文件夹")
        copy_path_action = menu.addAction("复制文件路径")

        chosen = menu.exec(global_pos)
        if chosen == play_action:
            track_index = self._find_track_index_by_id(track_id)
            if track_index >= 0:
                self.load_track(track_index)
                self.audio_service.play()
        elif chosen == remove_action:
            track_index = self._find_track_index_by_id(track_id)
            if track_index >= 0:
                self.remove_track_by_index(track_index)
        elif chosen == open_folder_action:
            if track.file_path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(track.file_path.parent)))
            else:
                QMessageBox.warning(self.page, "提示", "文件不存在，无法打开所在文件夹。")
        elif chosen == copy_path_action:
            QApplication.clipboard().setText(str(track.file_path))

    def restore_from_settings(self, settings: AppSettings) -> None:
        playlist_index = self._find_playlist_index_by_id(settings.last_playlist_id)
        if playlist_index >= 0:
            self.page.playlist_selector.setCurrentIndex(playlist_index)

        self._set_play_mode(settings.play_mode or "loop")

        if not self.current_playlist.tracks:
            return

        track_index = self._find_track_index_by_id(settings.last_track_id)
        if track_index >= 0:
            self.load_track(track_index, restore_position=settings.last_position_ms)

    def export_playback_state(self) -> AppSettings:
        playlist_id = self.current_playlist.id if self.playlists else ""
        track_id = ""
        if 0 <= self.current_track_index < len(self.current_playlist.tracks):
            track_id = self.current_playlist.tracks[self.current_track_index].id

        return AppSettings(
            play_mode=self.play_mode,
            last_playlist_id=playlist_id,
            last_track_id=track_id,
            last_position_ms=self.audio_service.position(),
        )

    def _refresh_playlist_selector(self) -> None:
        self.page.playlist_selector.blockSignals(True)
        self.page.playlist_selector.clear()
        for playlist in self.playlists:
            self.page.playlist_selector.addItem(playlist.name, playlist.id)
        self.page.playlist_selector.blockSignals(False)

    def _refresh_track_list(self) -> None:
        self.apply_search_filter(self.page.search_input.text())

    def _set_play_mode(self, mode: str) -> None:
        self.play_mode = mode
        self._update_play_mode_badge()
        for index in range(self.page.play_mode_selector.count()):
            if self.page.play_mode_selector.itemData(index) == mode:
                self.page.play_mode_selector.blockSignals(True)
                self.page.play_mode_selector.setCurrentIndex(index)
                self.page.play_mode_selector.blockSignals(False)
                return

    def _resolve_next_index(self) -> int | None:
        tracks = self.current_playlist.tracks
        if not tracks:
            return None
        if len(tracks) == 1:
            return 0

        if self.play_mode == "shuffle":
            choices = [index for index in range(len(tracks)) if index != self.current_track_index]
            return random.choice(choices)

        if self.current_track_index == -1:
            return 0
        return (self.current_track_index + 1) % len(tracks)

    def _resolve_previous_index(self) -> int | None:
        tracks = self.current_playlist.tracks
        if not tracks:
            return None
        if len(tracks) == 1:
            return 0

        if self.play_mode == "shuffle":
            choices = [index for index in range(len(tracks)) if index != self.current_track_index]
            return random.choice(choices)

        if self.current_track_index == -1:
            return 0
        return (self.current_track_index - 1) % len(tracks)

    def _filtered_row_to_track_index(self, filtered_row: int) -> int | None:
        if not 0 <= filtered_row < len(self.filtered_track_indices):
            return None
        return self.filtered_track_indices[filtered_row]

    def _find_playlist_index_by_id(self, playlist_id: str) -> int:
        for index, playlist in enumerate(self.playlists):
            if playlist.id == playlist_id:
                return index
        return -1

    def _find_track_index_by_id(self, track_id: str) -> int:
        for index, track in enumerate(self.current_playlist.tracks):
            if track.id == track_id:
                return index
        return -1

    def _find_track_by_id(self, track_id: str) -> Track | None:
        for track in self.current_playlist.tracks:
            if track.id == track_id:
                return track
        return None

    def _update_play_mode_badge(self) -> None:
        mapping = {
            "loop": "列表循环",
            "single": "单曲循环",
            "shuffle": "随机播放",
        }
        self.page.play_mode_badge.setText(mapping.get(self.play_mode, "列表循环"))

    def _update_sidebar_summary(self) -> None:
        self.page.playlist_count_label.setText(f"歌单数: {len(self.playlists)}")
        self.page.track_count_label.setText(f"当前歌单歌曲数: {len(self.current_playlist.tracks)}")
        keyword = self.page.search_input.text().strip()
        if keyword:
            self.page.search_state_label.setText(f"正在过滤: {keyword}")
        else:
            self.page.search_state_label.setText("当前未启用搜索过滤")

    def _build_track_description(self, track: Track) -> str:
        parts = [part for part in (track.artist, track.album) if part]
        if parts:
            return " / ".join(parts)
        return str(track.file_path)

    def _build_now_playing_meta(self, track: Track) -> str:
        parts = [part for part in (track.artist, track.album) if part]
        if track.duration_ms > 0:
            parts.append(format_milliseconds(track.duration_ms))
        if parts:
            return " · ".join(parts)
        return track.file_path.name

    def _update_cover_art(self, track: Track) -> None:
        if track.cover_path and Path(track.cover_path).exists():
            from PyQt6.QtGui import QPixmap

            self.page.set_cover_pixmap(QPixmap(track.cover_path))
            return
        self.page.set_cover_pixmap(None)

    def _reset_now_playing_panel(self, headline: str, detail: str) -> None:
        self.page.current_track_label.setText(headline)
        self.page.track_meta_label.setText(detail)
        self.page.current_time_label.setText("00:00")
        self.page.duration_label.setText("00:00")
        self.page.progress_slider.setRange(0, 0)
        self.page.now_playing_title.setText("还没有选择歌曲")
        self.page.now_playing_meta.setText("选中一首歌后，这里会显示播放中的曲目信息。")
        self.page.cover_letter.setText("A")
        self.page.cover_meta.setText("Aurora Player")
        self.page.set_cover_pixmap(None)
        self.page.lyric_widget.set_lyrics([])
