from t_e.config import Settings


def test_default_settings() -> None:
    settings = Settings()
    assert settings.app_title == "T_E"
    assert settings.default_encoding == "UTF-8"
    assert settings.window_geometry == "900x600"
    assert settings.min_window_width == 400
    assert settings.min_window_height == 300
    assert settings.log_level == "INFO"
