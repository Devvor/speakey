"""Main push-to-talk application."""

import threading
from typing import Optional

from ..config import Config
from .controller import PTTController
from .ui.overlay import StatusOverlay


class PTTApp:
    """Main push-to-talk application."""

    def __init__(self, config: Config):
        """Initialize PTT application.

        Args:
            config: Application configuration
        """
        self.config = config

        # Components
        self.controller = PTTController(config)
        self.overlay = StatusOverlay(config)

        # Connect controller state changes to overlay
        self.controller.on_state_change = self.overlay.update_state

    def start(self) -> None:
        """Start the PTT application."""
        print("Starting Parakeet STT Push-to-Talk...")
        print(f"Hotkey: {self.config.ptt.hotkey}")
        print(f"Hold threshold: {self.config.ptt.hold_threshold}s")
        print("Press Ctrl+C to quit\n")

        # Start controller in background thread
        controller_thread = threading.Thread(target=self.controller.start, daemon=True)
        controller_thread.start()

        # Start overlay (blocking - runs main loop)
        try:
            self.overlay.start()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop the PTT application."""
        print("\nStopping Parakeet STT...")
        self.controller.stop()
        self.overlay.stop()


def main():
    """Main entry point for PTT app."""
    from ..config import Config

    config = Config()
    app = PTTApp(config)

    try:
        app.start()
    except KeyboardInterrupt:
        app.stop()


if __name__ == "__main__":
    main()
