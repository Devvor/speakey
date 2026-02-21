"""Subprocess entry point — mirrors the pattern in src/daemon/run_daemon.py."""

import sys
from pathlib import Path

# Ensure project root is on the path when launched as a detached subprocess
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.fn_ptt.app import FnPTTApp  # noqa: E402

if __name__ == "__main__":
    FnPTTApp().run()
