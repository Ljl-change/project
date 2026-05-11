from __future__ import annotations

from app.models.playlist import Playlist
from app.models.track import Track
from app.repositories.playlist_repository import PlaylistRepository
from app.services.metadata_service import MetadataService


class PlaylistService:
    def __init__(
        self,
        repository: PlaylistRepository | None = None,
        metadata_service: MetadataService | None = None,
    ) -> None:
        self.repository = repository or PlaylistRepository()
        self.metadata_service = metadata_service

    def load_playlists(self) -> list[Playlist]:
        playlists = self.repository.list_all()
        if playlists:
            for playlist in playlists:
                if self._refresh_playlist_metadata(playlist):
                    self.repository.save(playlist)
            return playlists

        default_playlist = Playlist(name="默认歌单")
        self.repository.save(default_playlist)
        return [default_playlist]

    def create_playlist(self, name: str) -> Playlist:
        playlist = Playlist(name=name)
        self.repository.save(playlist)
        return playlist

    def rename_playlist(self, playlist: Playlist, name: str) -> Playlist:
        playlist.name = name
        self.repository.save(playlist)
        return playlist

    def delete_playlist(self, playlist_id: str) -> None:
        self.repository.delete(playlist_id)

    def save_playlist(self, playlist: Playlist) -> None:
        self.repository.save(playlist)

    def add_tracks(self, playlist: Playlist, tracks: list[Track]) -> Playlist:
        existing_ids = {track.id for track in playlist.tracks}
        for track in tracks:
            if track.id not in existing_ids:
                playlist.tracks.append(track)
                existing_ids.add(track.id)
        self.repository.save(playlist)
        return playlist

    def reorder_tracks(self, playlist: Playlist, ordered_track_ids: list[str]) -> Playlist:
        track_map = {track.id: track for track in playlist.tracks}
        reordered_tracks = [track_map[track_id] for track_id in ordered_track_ids if track_id in track_map]
        if len(reordered_tracks) == len(playlist.tracks):
            playlist.tracks = reordered_tracks
            self.repository.save(playlist)
        return playlist

    def _refresh_playlist_metadata(self, playlist: Playlist) -> bool:
        if self.metadata_service is None:
            return False

        changed = False
        refreshed_tracks: list[Track] = []
        for track in playlist.tracks:
            if not track.file_path.exists():
                refreshed_tracks.append(track)
                continue

            title_looks_raw = track.title == track.file_path.stem
            has_enough_metadata = bool(track.artist or track.album) or (track.duration_ms > 0 and not title_looks_raw)
            if has_enough_metadata:
                refreshed_tracks.append(track)
                continue

            refreshed_track = self.metadata_service.build_track_from_path(track.file_path)
            if refreshed_track.to_dict() != track.to_dict():
                changed = True
            refreshed_tracks.append(refreshed_track)

        if changed:
            playlist.tracks = refreshed_tracks
        return changed
