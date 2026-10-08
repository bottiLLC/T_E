"""Configuration module for T_E application settings."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import structlog
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent.parent

log = structlog.get_logger()


class Settings(BaseSettings):
    """Application configuration schema backed by Pydantic V2 Settings."""

    app_title: str = "T_E"
    default_encoding: str = "UTF-8"
    window_geometry: str = "900x600"
    min_window_width: int = 400
    min_window_height: int = 300
    log_level: str = "INFO"
    data_dir: Path = Field(default_factory=lambda: _PROJECT_ROOT / "data")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings: Final[Settings] = Settings()
log.info("settings_loaded", app_title=settings.app_title)
