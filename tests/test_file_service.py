from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from t_e.services.file_service import FileService


def test_write_and_read_utf8(tmp_path: Path) -> None:
    file_path = tmp_path / "test_utf8.txt"
    content = "こんにちは、世界！\nHello World!"

    FileService.write_file(file_path, content, "UTF-8")
    read_content, detected_enc = FileService.read_file(file_path)

    assert read_content == content
    assert detected_enc == "UTF-8"


def test_write_and_read_shift_jis(tmp_path: Path) -> None:
    file_path = tmp_path / "test_sjis.txt"
    content = "シフトジスで保存されたテキスト"

    FileService.write_file(file_path, content, "Shift_JIS")
    read_content, detected_enc = FileService.read_file(file_path)

    assert read_content == content
    assert detected_enc in ["Shift_JIS", "UTF-8"]


def test_write_and_read_euc_jp(tmp_path: Path) -> None:
    file_path = tmp_path / "test_euc.txt"
    content = "日本語EUCコードの文章です"

    FileService.write_file(file_path, content, "EUC-JP")
    read_content, detected_enc = FileService.read_file(file_path)

    assert read_content == content
    assert detected_enc in ["EUC-JP", "UTF-8", "Shift_JIS"]


def test_read_file_not_found(tmp_path: Path) -> None:
    non_existent = tmp_path / "non_existent.txt"
    with pytest.raises(FileNotFoundError):
        FileService.read_file(non_existent)


def test_read_file_unsupported_encoding(tmp_path: Path) -> None:
    file_path = tmp_path / "binary.bin"
    # UTF-8, CP932, EUC-JP 全てでデコードに失敗する無効バイト系列
    invalid_bytes = b"\x80\x81\xff\xfe\xf0\x00\x00"
    with open(file_path, "wb") as f:
        f.write(invalid_bytes)

    with pytest.raises(UnicodeDecodeError):
        FileService.read_file(file_path)


@pytest.mark.fuzz
@given(text=st.text(min_size=0, max_size=1000))
def test_file_service_fuzzing(tmp_path_factory: pytest.TempPathFactory, text: str) -> None:
    tmp_path = tmp_path_factory.mktemp("fuzz")
    file_path = tmp_path / "fuzz.txt"

    FileService.write_file(file_path, text, "UTF-8")
    read_content, detected_enc = FileService.read_file(file_path)

    assert read_content == text
    assert detected_enc == "UTF-8"
