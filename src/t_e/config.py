import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

log = structlog.get_logger()


class Settings(BaseSettings):
    app_title: str = "T_E"
    default_encoding: str = "UTF-8"
    window_geometry: str = "900x600"
    min_window_width: int = 400
    min_window_height: int = 300
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
log.info("settings_loaded", app_title=settings.app_title)
