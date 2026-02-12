"""Main daemon application."""

import os
import sys
import signal
from pathlib import Path
from typing import Dict, Any

from ..config import Config
from .ipc import IPCServer
from .controller import DaemonRecordingController
from ..ptt.ui.overlay import StatusOverlay


class DaemonApp:
    """Main daemon application."""

    def __init__(self, runtime_dir: Path):
        """Initialize daemon application.

        Args:
            runtime_dir: Directory for runtime files
        """
        self.runtime_dir = runtime_dir
        self.socket_path = runtime_dir / "daemon.sock"

        # Configuration
        self.config = Config()

        # Components
        self.ipc_server = IPCServer(self.socket_path)
        self.controller = DaemonRecordingController(self.config)
        self.overlay = None  # Will be created lazily

        # Connect callbacks
        self.ipc_server.on_message = self._handle_message
        self.controller.on_transcription_complete = self._handle_transcription

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def start(self) -> None:
        """Start the daemon."""
        print("Starting Parakeet STT Daemon...")
        print(f"Socket: {self.socket_path}")
        print(f"PID: {os.getpid()}")

        # Write PID to file
        pid_file = self.runtime_dir / "daemon.pid"
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
        print(f"PID file written: {pid_file}")

        # Start IPC server
        print("Starting IPC server...")
        self.ipc_server.start()
        print("IPC server started and listening")

        # Run headless (no overlay for now - causes issues as background daemon)
        print("Daemon running. Press Ctrl+C to quit.")
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop the daemon."""
        print("\nStopping Parakeet STT Daemon...")
        self.ipc_server.stop()
        if self.overlay:
            self.overlay.stop()

    def _signal_handler(self, signum, frame):
        """Handle termination signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.stop()
        sys.exit(0)

    def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IPC message.

        Args:
            message: Message dictionary

        Returns:
            Response dictionary
        """
        try:
            command = message.get("command")
            print(f"Received command: {command}")

            if command == "record_start":
                return self.controller.start_recording()
            elif command == "record_stop":
                return self.controller.stop_recording()
            elif command == "record_toggle":
                return self.controller.toggle_recording()
            elif command == "status":
                return self.controller.get_state()
            elif command == "ping":
                return {"status": "ok", "message": "pong"}
            else:
                return {"status": "error", "message": f"Unknown command: {command}"}
        except Exception as e:
            print(f"Error handling command: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def _handle_transcription(self, text: str) -> None:
        """Handle transcription completion.

        Args:
            text: Transcribed text
        """
        print(f"\nTranscription: {text}")


def main():
    """Main entry point for daemon."""
    if len(sys.argv) < 2:
        print("Usage: python -m parakeet_stt.daemon.app <runtime_dir>")
        sys.exit(1)

    runtime_dir = Path(sys.argv[1])
    app = DaemonApp(runtime_dir)

    try:
        app.start()
    except KeyboardInterrupt:
        app.stop()


if __name__ == "__main__":
    main()
