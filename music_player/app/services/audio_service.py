from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioService:
    def __init__(self) -> None:
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.65)

    def set_video_output(self, output) -> None:
        self.player.setVideoOutput(output)

    def set_volume(self, value: int) -> None:
        self.audio_output.setVolume(value / 100)

    def load_local_track(self, file_path: Path) -> None:
        self.player.setSource(QUrl.fromLocalFile(str(file_path)))

    def load_stream(self, url: str) -> None:
        self.player.setSource(QUrl(url))

    def set_position(self, value: int) -> None:
        self.player.setPosition(value)

    def position(self) -> int:
        return self.player.position()

    def play(self) -> None:
        self.player.play()

    def pause(self) -> None:
        self.player.pause()

    def stop(self) -> None:
        self.player.stop()
