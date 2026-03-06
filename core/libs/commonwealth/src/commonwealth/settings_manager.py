"""
CoratiaOS Settings Manager — Persistent configuration with schema validation.
Uses Pydantic models for type-safe settings with JSON persistence.
"""
import json
import pathlib
from typing import Type, TypeVar

from loguru import logger
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

CORATIAOS_CONFIG_BASE = pathlib.Path("/root/.config/coratiaos")


class SettingsManager:
    """Generic settings manager that persists Pydantic models to JSON files."""

    def __init__(
        self,
        model_class: Type[T],
        config_dir: pathlib.Path = CORATIAOS_CONFIG_BASE,
        config_name: str = "settings.json",
    ) -> None:
        self._model_class = model_class
        self._config_file = config_dir / config_name
        self._settings: T = self._load()

    def _load(self) -> T:
        """Load settings from disk, or create with defaults."""
        if self._config_file.exists():
            try:
                data = json.loads(self._config_file.read_text())
                return self._model_class.model_validate(data)
            except Exception as e:
                logger.warning(f"Failed to load settings from {self._config_file}: {e}")
        return self._model_class()

    def save(self) -> None:
        """Persist current settings to disk."""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config_file.write_text(self._settings.model_dump_json(indent=2))
        logger.info(f"Settings saved to {self._config_file}")

    @property
    def settings(self) -> T:
        return self._settings

    @settings.setter
    def settings(self, value: T) -> None:
        self._settings = value
        self.save()

    def reset(self) -> None:
        """Reset to defaults."""
        self._settings = self._model_class()
        self.save()
