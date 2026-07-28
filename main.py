import os
import sys
from pathlib import Path

# Redirect stdout/stderr if None (PyInstaller --noconsole mode)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")  # noqa: SIM115

# Ensure src module resolution
src_dir = str(Path(__file__).parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import structlog

from simple_notepad import SimpleNotepad

log = structlog.get_logger()


def main() -> None:
    log.info("application_starting")
    app = SimpleNotepad()
    app.mainloop()


if __name__ == "__main__":
    main()
