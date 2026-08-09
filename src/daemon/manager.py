"""Daemon process management."""

import os
import signal
import subprocess
import sys
from pathlib import Path


class DaemonManager:
    """Manages daemon lifecycle."""

    def __init__(self, runtime_dir: Path | None = None):
        """Initialize daemon manager.

        Args:
            runtime_dir: Directory for runtime files (PID, socket)
        """
        if runtime_dir is None:
            runtime_dir = Path.home() / ".parakeet-stt"

        self.runtime_dir = runtime_dir
        self.runtime_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

        self.pid_file = self.runtime_dir / "daemon.pid"
        self.socket_path = self.runtime_dir / "daemon.sock"
        self.log_file = self.runtime_dir / "daemon.log"

    def is_running(self) -> bool:
        """Check if daemon is running.

        Returns:
            True if daemon is running
        """
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            # PID file is stale
            self.pid_file.unlink()
            return False

    def get_pid(self) -> int | None:
        """Get daemon PID.

        Returns:
            PID if daemon is running, None otherwise
        """
        if not self.is_running():
            return None

        with open(self.pid_file, "r") as f:
            return int(f.read().strip())

    def start(self) -> bool:
        """Start daemon process.

        Returns:
            True if daemon was started, False if already running
        """
        if self.is_running():
            return False

        # Find the daemon runner script
        import src.daemon.run_daemon

        daemon_script = Path(src.daemon.run_daemon.__file__)

        # Start daemon as subprocess
        cmd = [
            sys.executable,
            str(daemon_script),
            str(self.runtime_dir),
        ]

        # Open log file
        log_file = open(self.log_file, "a")

        # Start daemon process
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

        # Write PID file
        with open(self.pid_file, "w") as f:
            f.write(str(process.pid))

        return True

    def stop(self) -> bool:
        """Stop daemon process.

        Returns:
            True if daemon was stopped, False if not running
        """
        if not self.is_running():
            return False

        pid = self.get_pid()
        if pid is None:
            return False

        try:
            # Send SIGTERM
            os.kill(pid, signal.SIGTERM)

            # Wait for process to exit
            import time

            for _ in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(0.1)
                except ProcessLookupError:
                    break

            # Force kill if still running
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()

            return True
        except ProcessLookupError:
            # Process already dead
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True

    def get_status(self) -> dict:
        """Get daemon status.

        Returns:
            Status dictionary
        """
        if self.is_running():
            return {
                "running": True,
                "pid": self.get_pid(),
                "socket": str(self.socket_path),
                "log": str(self.log_file),
            }
        else:
            return {"running": False}
