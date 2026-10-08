"""Tests for FileService operations and encoding transformations."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from t_e.services.file_service import FileService


def test_write_and_read_utf8(tmp_path: Path) -> None:
    """Verify writing and reading content encoded in UTF-8."""
    # Arrange
    file_path = tmp_path / "test_utf8.txt"
    content = "こんにちは、世界！\nHello World!"

    # Act
    FileService.write_file(file_path, content, "UTF-8")
    read_content, detected_enc = FileService.read_file(file_path)

    # Assert
    assert read_content == content
    assert detected_enc == "UTF-8"


def test_write_and_read_shift_jis(tmp_path: Path) -> None:
    """Verify writing and reading content encoded in Shift_JIS."""
    # Arrange
    file_path = tmp_path / "test_sjis.txt"
    content = "シフトジスで保存されたテキスト"

    # Act
    FileService.write_file(file_path, content, "Shift_JIS")
    read_content, detected_enc = FileService.read_file(file_path)

    # Assert
    assert read_content == content
    assert detected_enc in ["Shift_JIS", "UTF-8"]


def test_write_and_read_euc_jp(tmp_path: Path) -> None:
    """Verify writing and reading content encoded in EUC-JP."""
    # Arrange
    file_path = tmp_path / "test_euc.txt"
    content = "日本語EUCコードの文章です"

    # Act
    FileService.write_file(file_path, content, "EUC-JP")
    read_content, detected_enc = FileService.read_file(file_path)

    # Assert
    assert read_content == content
    assert detected_enc in ["EUC-JP", "UTF-8", "Shift_JIS"]


def test_read_file_not_found(tmp_path: Path) -> None:
    """Verify FileNotFoundError is raised when file does not exist."""
    # Arrange
    non_existent = tmp_path / "non_existent.txt"

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="File not found:"):
        FileService.read_file(non_existent)


def test_read_file_unsupported_encoding(tmp_path: Path) -> None:
    """Verify UnicodeDecodeError is raised for invalid byte sequences."""
    # Arrange
    file_path = tmp_path / "binary.bin"
    invalid_bytes = b"\x80\x81\xff\xfe\xf0\x00\x00"
    file_path.write_bytes(invalid_bytes)

    # Act & Assert
    with pytest.raises(UnicodeDecodeError, match="Unsupported text encoding"):
        FileService.read_file(file_path)


def test_read_file_oserror_raises_oserror(tmp_path: Path) -> None:
    """Verify OSError during read is logged and re-raised."""
    # Arrange
    file_path = tmp_path / "valid.txt"
    file_path.write_text("sample content", encoding="utf-8")

    # Act & Assert
    with (
        patch("builtins.open", side_effect=OSError("Disk read failure")),
        pytest.raises(OSError, match="Disk read failure"),
    ):
        FileService.read_file(file_path)


def test_write_file_oserror_raises_oserror(tmp_path: Path) -> None:
    """Verify OSError during write is logged and re-raised."""
    # Arrange
    file_path = tmp_path / "dest.txt"

    # Act & Assert
    with (
        patch("builtins.open", side_effect=OSError("Disk write permission denied")),
        pytest.raises(OSError, match="Disk write permission denied"),
    ):
        FileService.write_file(file_path, "sample content", "UTF-8")


@pytest.mark.fuzz
@given(text=st.text(min_size=0, max_size=1000))
def test_file_service_fuzzing(tmp_path_factory: pytest.TempPathFactory, text: str) -> None:
    """Fuzz testing verifying arbitrary Unicode strings round-trip in UTF-8."""
    # Arrange
    tmp_path = tmp_path_factory.mktemp("fuzz")
    file_path = tmp_path / "fuzz.txt"

    # Act
    FileService.write_file(file_path, text, "UTF-8")
    read_content, detected_enc = FileService.read_file(file_path)

    # Assert
    assert read_content == text
    assert detected_enc == "UTF-8"
