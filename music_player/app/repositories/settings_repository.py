from __future__ import annotations

import json
from dataclasses import asdict, fields

from app.models.app_settings import AppSettings
from app.utils.constants import SETTINGS_FILE
from app.utils.path_utils import ensure_directory


class SettingsRepository:
    def load(self) -> AppSettings:
        if not SETTINGS_FILE.exists():
            settings = AppSettings()
            self.save(settings)
            return settings

        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            settings = AppSettings()
            self.save(settings)
            return settings

        if not isinstance(data, dict):
            settings = AppSettings()
            self.save(settings)
            return settings

        defaults = asdict(AppSettings())
        valid_keys = {field.name for field in fields(AppSettings)}
        merged = defaults | {key: value for key, value in data.items() if key in valid_keys}
        settings = AppSettings(**merged)

        if merged != data:
            self.save(settings)
        return settings

    def save(self, settings: AppSettings) -> None:
        ensure_directory(SETTINGS_FILE.parent)
        SETTINGS_FILE.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
