from __future__ import annotations

from PyQt6.QtGui import QKeySequence, QShortcut

from app.controllers.library_controller import LibraryController
from app.controllers.player_controller import PlayerController
from app.controllers.stream_controller import StreamController
from app.services.audio_service import AudioService
from app.services.lyric_service import LyricService
from app.services.metadata_service import MetadataService
from app.services.playlist_service import PlaylistService
from app.services.settings_service import SettingsService
from app.services.stream_probe_service import StreamProbeService
from app.ui.main_window import MainWindow
from app.utils.time_utils import format_milliseconds


class AppController:
    def __init__(self, window: MainWindow) -> None:
        self.window = window
        self.audio_service = AudioService()
        self.metadata_service = MetadataService()
        self.playlist_service = PlaylistService(metadata_service=self.metadata_service)
        self.settings_service = SettingsService()
        self.stream_probe_service = StreamProbeService()
        self.lyric_service = LyricService()
        self.library_controller = LibraryController()

        self.player_controller = PlayerController(
            self.window.music_page,
            self.audio_service,
            self.metadata_service,
            self.playlist_service,
            self.library_controller,
            self.lyric_service,
        )
        self.stream_controller = StreamController(
            self.window.stream_page,
            self.audio_service,
            self.stream_probe_service,
        )

        self._apply_initial_settings()
        self._connect_events()

    def _apply_initial_settings(self) -> None:
        settings = self.settings_service.load_settings()
        self.window.resize(settings.window_width, settings.window_height)
        self.audio_service.set_volume(settings.volume)
        self.window.settings_page.volume_slider.setValue(settings.volume)
        self.player_controller.restore_from_settings(settings)

    def _connect_events(self) -> None:
        self.window.settings_page.volume_slider.valueChanged.connect(self.audio_service.set_volume)
        self.window.register_before_close(self.save_app_state)

        self.window.top_search_input.textChanged.connect(self._handle_global_search)

        self.window.player_prev_button.clicked.connect(self.player_controller.play_previous)
        self.window.player_play_button.clicked.connect(self.player_controller.toggle_playback)
        self.window.player_next_button.clicked.connect(self.player_controller.play_next)
        self.window.player_progress_slider.sliderReleased.connect(self._seek_from_footer)

        self.audio_service.player.positionChanged.connect(self._sync_footer_progress)
        self.audio_service.player.durationChanged.connect(self._sync_footer_progress)
        self.audio_service.player.playbackStateChanged.connect(self._sync_footer_play_button)
        self.audio_service.player.sourceChanged.connect(self._sync_footer_track_info)

        self._register_shortcuts()
        self._sync_footer_track_info()
        self._sync_footer_progress()
        self._sync_footer_play_button()

    def save_app_state(self) -> None:
        saved = self.settings_service.load_settings()
        playback_state = self.player_controller.export_playback_state()
        saved.play_mode = playback_state.play_mode
        saved.last_playlist_id = playback_state.last_playlist_id
        saved.last_track_id = playback_state.last_track_id
        saved.last_position_ms = playback_state.last_position_ms
        saved.volume = self.window.settings_page.volume_slider.value()
        saved.window_width = self.window.width()
        saved.window_height = self.window.height()
        self.settings_service.save_settings(saved)

    def _handle_global_search(self, text: str) -> None:
        current_page = self.window.stack.currentIndex()
        if current_page == 0:
            self.window.music_page.search_input.setText(text)
        elif current_page == 1:
            self.stream_controller.apply_search_filter(text)

    def _sync_footer_track_info(self, *args) -> None:
        track = self.player_controller.current_track()
        if track is None:
            self.window.player_track_title.setText("还没有选择歌曲")
            self.window.player_track_meta.setText("底部播放器条会同步当前播放信息")
            return

        self.window.player_track_title.setText(track.title)
        self.window.player_track_meta.setText(track.file_path.name)

    def _sync_footer_progress(self, *args) -> None:
        position = self.audio_service.position()
        duration = self.audio_service.player.duration()
        self.window.player_progress_slider.setRange(0, max(duration, 0))
        self.window.player_progress_slider.setValue(position)
        self.window.player_time_label.setText(
            f"{format_milliseconds(position)} / {format_milliseconds(duration)}"
        )

    def _sync_footer_play_button(self, *args) -> None:
        state = self.audio_service.player.playbackState()
        self.window.player_play_button.setText(
            "⏸" if state == self.audio_service.player.PlaybackState.PlayingState else "▶"
        )

    def _seek_from_footer(self) -> None:
        self.audio_service.set_position(self.window.player_progress_slider.value())

    def _register_shortcuts(self) -> None:
        self.shortcut_focus_search = QShortcut(QKeySequence("Ctrl+F"), self.window)
        self.shortcut_focus_search.activated.connect(self.window.top_search_input.setFocus)

        self.shortcut_music = QShortcut(QKeySequence("Ctrl+1"), self.window)
        self.shortcut_music.activated.connect(lambda: self.window.set_current_page(0))
        self.shortcut_stream = QShortcut(QKeySequence("Ctrl+2"), self.window)
        self.shortcut_stream.activated.connect(lambda: self.window.set_current_page(1))
        self.shortcut_settings = QShortcut(QKeySequence("Ctrl+3"), self.window)
        self.shortcut_settings.activated.connect(lambda: self.window.set_current_page(2))

        self.shortcut_play_pause = QShortcut(QKeySequence("Space"), self.window)
        self.shortcut_play_pause.activated.connect(self._toggle_active_page_playback)
        self.shortcut_prev = QShortcut(QKeySequence("Ctrl+Left"), self.window)
        self.shortcut_prev.activated.connect(self.player_controller.play_previous)
        self.shortcut_next = QShortcut(QKeySequence("Ctrl+Right"), self.window)
        self.shortcut_next.activated.connect(self.player_controller.play_next)

    def _toggle_active_page_playback(self) -> None:
        if self.window.top_search_input.hasFocus() or self.window.music_page.search_input.hasFocus():
            return
        if self.window.stack.currentIndex() == 1:
            self.stream_controller.play_stream()
        else:
            self.player_controller.toggle_playback()
