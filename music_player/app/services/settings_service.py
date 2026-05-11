from __future__ import annotations

from app.models.app_settings import AppSettings
from app.repositories.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, repository: SettingsRepository | None = None) -> None:
        self.repository = repository or SettingsRepository()

    def load_settings(self) -> AppSettings:
        return self.repository.load()

    def save_settings(self, settings: AppSettings) -> None:
        self.repository.save(settings)
