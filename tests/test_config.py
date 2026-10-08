"""Tests for Settings schema configuration."""

from __future__ import annotations

from pathlib import Path

from t_e.config import Settings


def test_default_settings() -> None:
    """Verify standard default configuration values."""
    # Arrange & Act
    settings = Settings()

    # Assert
    assert settings.app_title == "T_E"
    assert settings.default_encoding == "UTF-8"
    assert settings.window_geometry == "900x600"
    assert settings.min_window_width == 400
    assert settings.min_window_height == 300
    assert settings.log_level == "INFO"
    assert settings.data_dir.name == "data"


def test_custom_settings(tmp_path: Path) -> None:
    """Verify custom overriding of configuration fields."""
    # Arrange & Act
    custom_settings = Settings(
        app_title="Custom_Editor",
        default_encoding="Shift_JIS",
        window_geometry="1024x768",
        min_window_width=500,
        min_window_height=400,
        log_level="DEBUG",
        data_dir=tmp_path / "custom_data",
    )

    # Assert
    assert custom_settings.app_title == "Custom_Editor"
    assert custom_settings.default_encoding == "Shift_JIS"
    assert custom_settings.window_geometry == "1024x768"
    assert custom_settings.min_window_width == 500
    assert custom_settings.min_window_height == 400
    assert custom_settings.log_level == "DEBUG"
    assert custom_settings.data_dir == tmp_path / "custom_data"
