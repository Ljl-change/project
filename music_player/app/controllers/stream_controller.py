from __future__ import annotations

from app.models.stream_item import StreamItem
from app.services.audio_service import AudioService
from app.services.stream_probe_service import StreamProbeService
from app.ui.stream_page import StreamPage


class StreamController:
    def __init__(
        self,
        page: StreamPage,
        audio_service: AudioService,
        stream_service: StreamProbeService,
    ) -> None:
        self.page = page
        self.audio_service = audio_service
        self.stream_service = stream_service
        self.streams: list[StreamItem] = []
        self.filtered_indices: list[int] = []

        self.audio_service.set_video_output(self.page.video_panel)

        self.page.detect_button.clicked.connect(self.load_demo_streams)
        self.page.load_button.clicked.connect(self.load_selected_stream)
        self.page.play_button.clicked.connect(self.play_stream)
        self.page.stop_button.clicked.connect(self.stop_stream)
        self.page.stream_list.itemClicked.connect(self.on_stream_clicked)

        self.load_demo_streams()

    def load_demo_streams(self) -> None:
        self.streams = self.stream_service.load_demo_streams()
        self.apply_search_filter("")
        if self.streams:
            self.show_stream(self.streams[0])

    def apply_search_filter(self, keyword: str) -> None:
        term = keyword.strip().lower()
        self.filtered_indices.clear()
        self.page.stream_list.clear()

        for index, stream in enumerate(self.streams):
            haystack = f"{stream.name} {stream.description} {stream.url}".lower()
            if term and term not in haystack:
                continue
            self.filtered_indices.append(index)
            self.page.stream_list.addItem(f"{stream.name} | {stream.description}")

    def on_stream_clicked(self, item) -> None:
        row = self.page.stream_list.row(item)
        if not 0 <= row < len(self.filtered_indices):
            return
        self.show_stream(self.streams[self.filtered_indices[row]])

    def load_selected_stream(self) -> None:
        row = self.page.stream_list.currentRow()
        if not 0 <= row < len(self.filtered_indices):
            return
        self.show_stream(self.streams[self.filtered_indices[row]])

    def show_stream(self, stream: StreamItem) -> None:
        self.page.stream_name_label.setText(stream.name)
        self.page.status_label.setText(stream.description or "已载入直播源。")
        self.page.url_input.setText(stream.url)

    def play_stream(self) -> None:
        url = self.page.url_input.text().strip()
        if not url:
            self.page.status_label.setText("请输入直播地址。")
            return

        self.audio_service.load_stream(url)
        self.audio_service.play()
        self.page.status_label.setText("直播播放已连接，可以继续切换和筛选频道。")

    def stop_stream(self) -> None:
        self.audio_service.stop()
        self.page.status_label.setText("直播已停止。")
