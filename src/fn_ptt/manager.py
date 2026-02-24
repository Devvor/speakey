"""Process lifecycle management for fn-ptt daemon."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


class FnPttManager:
    def __init__(self, runtime_dir: Path | None = None):
        self.runtime_dir = Path(runtime_dir or (Path.home() / ".parakeet-stt"))
        self.runtime_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.pid_file = self.runtime_dir / "fn-ptt.pid"

    def is_running(self) -> bool:
        if not self.pid_file.exists():
            return False
        try:
            pid = int(self.pid_file.read_text().strip())
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            self.pid_file.unlink(missing_ok=True)
            return False

    def start(self) -> bool:
        if self.is_running():
            return False
        import src.fn_ptt.run as _run_module

        run_script = Path(_run_module.__file__)
        log = open(self.runtime_dir / "fn-ptt.log", "a")
        proc = subprocess.Popen(
            [sys.executable, str(run_script), str(self.runtime_dir)],
            stdout=log,
            stderr=log,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        self.pid_file.write_text(str(proc.pid))
        return True

    def stop(self) -> bool:
        if not self.is_running():
            return False
        pid = int(self.pid_file.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        for _ in range(20):
            try:
                os.kill(pid, 0)
                time.sleep(0.1)
            except ProcessLookupError:
                break
        else:
            os.kill(pid, signal.SIGKILL)
        self.pid_file.unlink(missing_ok=True)
        return True

    def get_status(self) -> dict:
        if not self.is_running():
            return {"running": False}
        return {"running": True, "pid": int(self.pid_file.read_text().strip())}
