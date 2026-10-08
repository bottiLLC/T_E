"""Tests for backup_manager module and data backup verification."""

from __future__ import annotations

import json
import os
import zipfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

from backup_manager import get_backup_dir, run_backup, set_backup_dir


@pytest.fixture(autouse=True)
def _isolate_backup_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Isolate backup configuration file and env var for every test."""
    isolated_config = tmp_path / "data" / "backup_config.json"
    isolated_default_dir = tmp_path / "backups"
    monkeypatch.delenv("BACKUP_DIR", raising=False)
    with (
        patch("backup_manager._CONFIG_FILE", isolated_config),
        patch("backup_manager._DEFAULT_BACKUP_DIR", isolated_default_dir),
    ):
        yield


def test_get_backup_dir_default(tmp_path: Path) -> None:
    """Verify default backup destination path is returned when unconfigured."""
    # Act
    backup_dir = get_backup_dir()

    # Assert
    assert backup_dir == (tmp_path / "backups").resolve()


def test_get_backup_dir_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify BACKUP_DIR environment variable is respected when config file absent."""
    # Arrange
    env_target = tmp_path / "env_backups"
    monkeypatch.setenv("BACKUP_DIR", str(env_target))

    # Act
    backup_dir = get_backup_dir()

    # Assert
    assert backup_dir == env_target.resolve()


def test_get_backup_dir_invalid_json(tmp_path: Path) -> None:
    """Verify corrupted JSON config falls back gracefully to default directory."""
    # Arrange
    corrupt_config = tmp_path / "data" / "backup_config.json"
    corrupt_config.parent.mkdir(parents=True, exist_ok=True)
    corrupt_config.write_text("invalid json content", encoding="utf-8")

    # Act
    backup_dir = get_backup_dir()

    # Assert
    assert backup_dir == (tmp_path / "backups").resolve()


def test_set_and_get_backup_dir(tmp_path: Path) -> None:
    """Verify setting custom backup directory updates configuration file."""
    # Arrange
    target = tmp_path / "custom_backups"

    # Act
    res = set_backup_dir(str(target))
    backup_dir = get_backup_dir()

    # Assert
    assert res["success"] is True
    assert "バックアップ先を設定しました" in str(res["message"])
    assert backup_dir == target.resolve()


def test_set_backup_dir_oserror_handling() -> None:
    """Verify set_backup_dir captures OSError and returns failure dictionary."""
    # Act
    with patch.object(Path, "mkdir", side_effect=OSError("Read-only filesystem")):
        res = set_backup_dir("/invalid/path")

    # Assert
    assert res["success"] is False
    assert "保存先パスが無効" in str(res["message"])


def test_run_backup_empty_or_missing_source(tmp_path: Path) -> None:
    """Verify run_backup aborts safely when source directory is empty or missing."""
    # Arrange
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    # Act
    res = run_backup(app_name="test_app", source_dir=empty_dir)

    # Assert
    assert res["success"] is False
    assert "バックアップ対象が存在しないか空欄です" in str(res["message"])


def test_run_backup_destination_mkdir_oserror(tmp_path: Path) -> None:
    """Verify run_backup fails gracefully when destination folder creation fails."""
    # Arrange
    source_dir = tmp_path / "valid_source"
    source_dir.mkdir()
    (source_dir / "test.txt").write_text("data", encoding="utf-8")

    # Act
    with patch.object(Path, "mkdir", side_effect=OSError("Permission denied on destination")):
        res = run_backup(app_name="t_e", source_dir=source_dir)

    # Assert
    assert res["success"] is False
    assert "保存先フォルダの作成に失敗しました" in str(res["message"])


def test_run_backup_success_and_config_exclusion_kb(tmp_path: Path) -> None:
    """Verify run_backup creates valid zip archive excluding config and formats KB."""
    # Arrange
    source_dir = tmp_path / "data_source"
    source_dir.mkdir()
    (source_dir / "file1.txt").write_text("small data", encoding="utf-8")
    (source_dir / "file2.json").write_text(json.dumps({"key": "val"}), encoding="utf-8")

    config_in_source = source_dir / "backup_config.json"
    config_in_source.write_text("{}", encoding="utf-8")

    backup_dest = tmp_path / "backup_out"
    set_backup_dir(str(backup_dest))

    with patch("backup_manager._CONFIG_FILE", config_in_source):
        # Act
        res = run_backup(app_name="t_e", source_dir=source_dir)

        # Assert
        assert res["success"] is True
        assert "バックアップ完了" in str(res["message"])
        assert "KB" in str(res["size"])
        destination = Path(str(res["destination"]))
        assert destination.is_file()
        assert zipfile.is_zipfile(destination)

        with zipfile.ZipFile(destination, "r") as zf:
            assert zf.testzip() is None
            assert "file1.txt" in zf.namelist()
            assert "file2.json" in zf.namelist()
            assert "backup_config.json" not in zf.namelist()


def test_run_backup_success_mb_size(tmp_path: Path) -> None:
    """Verify run_backup formats size string in MB when archive exceeds 1MB."""
    # Arrange
    source_dir = tmp_path / "data_large"
    source_dir.mkdir()
    # Uncompressible random data so zipfile exceeds 1MB
    (source_dir / "random.bin").write_bytes(os.urandom(1024 * 1024 + 1024))

    backup_dest = tmp_path / "backup_mb_out"
    set_backup_dir(str(backup_dest))

    # Act
    res = run_backup(app_name="t_e", source_dir=source_dir)

    # Assert
    assert res["success"] is True
    assert "MB" in str(res["size"])


def test_run_backup_corrupted_zip_interlock(tmp_path: Path) -> None:
    """Verify interlock detects corruption when testzip reports errors."""
    # Arrange
    source_dir = tmp_path / "data_corrupt"
    source_dir.mkdir()
    (source_dir / "test.txt").write_text("data", encoding="utf-8")

    # Act
    with patch("zipfile.ZipFile.testzip", return_value="test.txt"):
        res = run_backup(app_name="t_e", source_dir=source_dir)

    # Assert
    assert res["success"] is False
    assert "整合性チェック失敗" in str(res["message"])


def test_run_backup_move_oserror(tmp_path: Path) -> None:
    """Verify run_backup catches OSError during final destination move."""
    # Arrange
    source_dir = tmp_path / "data_move_fail"
    source_dir.mkdir()
    (source_dir / "test.txt").write_text("data", encoding="utf-8")

    # Act
    with patch("shutil.move", side_effect=OSError("Cross-device link failure")):
        res = run_backup(app_name="t_e", source_dir=source_dir)

    # Assert
    assert res["success"] is False
    assert "確定移動に失敗しました" in str(res["message"])
