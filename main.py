"""Application entry point for T_E desktop text editor."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Deterministic module resolution prior to local imports
_ROOT_DIR = str(Path(__file__).resolve().parent)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

_SRC_DIR = str(Path(__file__).resolve().parent / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Redirect stdout/stderr if None (PyInstaller --noconsole mode)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115

import structlog

from simple_notepad import SimpleNotepad

log = structlog.get_logger()


def main() -> None:
    """Launch the T_E desktop GUI application."""
    log.info("application_starting")
    app = SimpleNotepad()
    app.mainloop()


if __name__ == "__main__":
    main()
