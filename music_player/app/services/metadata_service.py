from __future__ import annotations

from io import BytesIO
from hashlib import sha1
from pathlib import Path

from PIL import Image

try:
    from mutagen import File as MutagenFile
    from mutagen.flac import FLAC
    from mutagen.id3 import APIC
    from mutagen.mp4 import MP4, MP4Cover
except ImportError:
    MutagenFile = None
    FLAC = ()
    APIC = ()
    MP4 = ()
    MP4Cover = ()

from app.models.track import Track
from app.utils.constants import CACHE_DIR
from app.utils.path_utils import ensure_directory


class MetadataService:
    def __init__(self) -> None:
        self.cover_cache_dir = ensure_directory(CACHE_DIR / "covers")

    def build_track_from_path(self, file_path: Path) -> Track:
        normalized_path = file_path.resolve()
        track_id = sha1(str(normalized_path).encode("utf-8")).hexdigest()
        title = normalized_path.stem
        artist = ""
        album = ""
        duration_ms = 0
        cover_path = ""

        if MutagenFile is None:
            return Track(
                id=track_id,
                title=title,
                file_path=normalized_path,
                artist=artist,
                album=album,
                duration_ms=duration_ms,
                cover_path=cover_path,
            )

        try:
            audio = MutagenFile(normalized_path)
        except Exception:
            audio = None

        if audio is not None:
            title = self._read_first_tag(audio, ("title", "\xa9nam", "TIT2")) or title
            artist = self._read_first_tag(audio, ("artist", "\xa9ART", "albumartist", "TPE1")) or ""
            album = self._read_first_tag(audio, ("album", "\xa9alb", "TALB")) or ""
            duration_ms = self._read_duration_ms(audio)
            cover_path = self._extract_cover_art(audio, track_id)

        return Track(
            id=track_id,
            title=title,
            file_path=normalized_path,
            artist=artist,
            album=album,
            duration_ms=duration_ms,
            cover_path=cover_path,
        )

    def _read_first_tag(self, audio, keys: tuple[str, ...]) -> str:
        tags = getattr(audio, "tags", None)
        if not tags:
            return ""

        for key in keys:
            try:
                value = tags.get(key)
            except Exception:
                value = None
            text = self._coerce_text(value)
            if text:
                return text

        for key in keys:
            if hasattr(tags, "keys"):
                for existing_key in tags.keys():
                    if str(existing_key).lower() == key.lower():
                        text = self._coerce_text(tags.get(existing_key))
                        if text:
                            return text
        return ""

    def _coerce_text(self, value) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (list, tuple)):
            for item in value:
                text = self._coerce_text(item)
                if text:
                    return text
            return ""
        if hasattr(value, "text"):
            return self._coerce_text(value.text)
        return str(value).strip()

    def _read_duration_ms(self, audio) -> int:
        info = getattr(audio, "info", None)
        length = getattr(info, "length", 0) or 0
        return max(0, int(length * 1000))

    def _extract_cover_art(self, audio, track_id: str) -> str:
        cached_path = self.cover_cache_dir / f"{track_id}.png"
        if cached_path.exists():
            return str(cached_path)

        image_bytes = b""

        if isinstance(audio, FLAC):
            if audio.pictures:
                image_bytes = audio.pictures[0].data
        elif isinstance(audio, MP4):
            covr = audio.tags.get("covr") if audio.tags else None
            if covr:
                first_cover = covr[0]
                if isinstance(first_cover, MP4Cover):
                    image_bytes = bytes(first_cover)
        else:
            tags = getattr(audio, "tags", None)
            if tags and hasattr(tags, "getall"):
                pictures = tags.getall("APIC")
                if pictures:
                    first_picture = pictures[0]
                    if isinstance(first_picture, APIC):
                        image_bytes = first_picture.data

        if not image_bytes:
            return ""

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            image.thumbnail((520, 520))
            image.save(cached_path, format="PNG")
        except Exception:
            return ""

        return str(cached_path)
