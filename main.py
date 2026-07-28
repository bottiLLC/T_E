import sys
from pathlib import Path

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
