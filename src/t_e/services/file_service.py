"""Filesystem I/O service supporting multi-encoding detection and writing."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import Final

import structlog

log = structlog.get_logger()

ENCODING_MAP: Final[MappingProxyType[str, str]] = MappingProxyType(
    {
        "UTF-8": "utf-8",
        "Shift_JIS": "cp932",
        "EUC-JP": "euc-jp",
    }
)

_SUPPORTED_ENCODINGS: Final[tuple[str, ...]] = ("utf-8", "cp932", "euc-jp")


class FileService:
    """Service providing safe, encoded read and write operations on text files."""

    @staticmethod
    def read_file(filepath: str | Path) -> tuple[str, str]:
        """Read a text file and determine its character encoding.

        Attempts decoding against UTF-8, CP932 (Shift_JIS), and EUC-JP sequentially.

        Args:
            filepath: Path to the target text file.

        Returns:
            tuple[str, str]: Tuple consisting of decoded content string and the UI
                encoding label ('UTF-8', 'Shift_JIS', or 'EUC-JP').

        Raises:
            FileNotFoundError: If the target file path does not point to an existing file.
            UnicodeDecodeError: If decoding fails for all supported encodings.
            OSError: If an operating system error occurs during reading.
        """
        path = Path(filepath)
        log.info("read_file_start", path=str(path))

        if not path.is_file():
            log.error("read_file_not_found", path=str(path))
            raise FileNotFoundError(f"File not found: {path}")

        for enc in _SUPPORTED_ENCODINGS:
            try:
                with open(path, encoding=enc, newline="") as f:
                    content = f.read()

                detected_ui_enc = "UTF-8"
                if enc == "cp932":
                    detected_ui_enc = "Shift_JIS"
                elif enc == "euc-jp":
                    detected_ui_enc = "EUC-JP"

                log.info("read_file_success", path=str(path), encoding=detected_ui_enc)
                return content, detected_ui_enc
            except UnicodeDecodeError:
                continue
            except OSError as e:
                log.error("read_file_error", path=str(path), error=str(e))
                raise

        log.error("read_file_unsupported_encoding", path=str(path))
        raise UnicodeDecodeError("utf-8", b"", 0, 1, "Unsupported text encoding")

    @staticmethod
    def write_file(filepath: str | Path, content: str, encoding_label: str) -> None:
        """Write string content to disk using the mapped character encoding.

        Args:
            filepath: Destination file path.
            content: Text content to persist.
            encoding_label: Target encoding key ('UTF-8', 'Shift_JIS', or 'EUC-JP').

        Raises:
            OSError: If writing to the file fails due to filesystem or permission error.
        """
        path = Path(filepath)
        target_enc = ENCODING_MAP.get(encoding_label, "utf-8")
        log.info(
            "write_file_start",
            path=str(path),
            encoding=encoding_label,
            target_enc=target_enc,
        )

        try:
            with open(path, "w", encoding=target_enc, newline="") as f:
                f.write(content)
            log.info("write_file_success", path=str(path))
        except OSError as e:
            log.error("write_file_error", path=str(path), error=str(e))
            raise
