from pathlib import Path

import structlog

log = structlog.get_logger()

ENCODING_MAP = {
    "UTF-8": "utf-8",
    "Shift_JIS": "cp932",
    "EUC-JP": "euc-jp",
}


class FileService:
    @staticmethod
    def read_file(filepath: str | Path) -> tuple[str, str]:
        path = Path(filepath)
        log.info("read_file_start", path=str(path))

        if not path.is_file():
            log.error("read_file_not_found", path=str(path))
            raise FileNotFoundError(f"File not found: {path}")

        encodings_to_try = ["utf-8", "cp932", "euc-jp"]
        for enc in encodings_to_try:
            try:
                with open(path, "r", encoding=enc, newline="") as f:
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
            except Exception as e:
                log.error("read_file_error", path=str(path), error=str(e))
                raise

        log.error("read_file_unsupported_encoding", path=str(path))
        raise UnicodeDecodeError("utf-8", b"", 0, 1, "Unsupported text encoding")

    @staticmethod
    def write_file(filepath: str | Path, content: str, encoding_label: str) -> None:
        path = Path(filepath)
        target_enc = ENCODING_MAP.get(encoding_label, "utf-8")
        log.info("write_file_start", path=str(path), encoding=encoding_label, target_enc=target_enc)

        try:
            with open(path, "w", encoding=target_enc, newline="") as f:
                f.write(content)
            log.info("write_file_success", path=str(path))
        except Exception as e:
            log.error("write_file_error", path=str(path), error=str(e))
            raise
