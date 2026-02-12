"""Status overlay window for push-to-talk."""

import tkinter as tk
from typing import Optional

from ...config import Config
from .styles import STATE_COLORS, STATE_MESSAGES, WINDOW_WIDTH, WINDOW_HEIGHT, PADDING


class StatusOverlay:
    """Floating status overlay window."""

    def __init__(self, config: Config):
        """Initialize status overlay.

        Args:
            config: Application configuration
        """
        self.config = config
        self.window: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None
        self.current_state = "idle"

        self._create_window()

    def _create_window(self) -> None:
        """Create overlay window."""
        self.window = tk.Tk()

        # Window properties
        self.window.title("Parakeet STT")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.attributes("-topmost", True)  # Always on top
        self.window.attributes("-alpha", self.config.ptt.overlay_opacity)

        # Position window
        self._position_window()

        # Create label
        self.label = tk.Label(
            self.window,
            text=STATE_MESSAGES["idle"],
            font=("SF Pro Display", 14, "bold"),
            fg="white",
            bg=STATE_COLORS["idle"],
            padx=PADDING,
            pady=PADDING,
        )
        self.label.pack(fill=tk.BOTH, expand=True)

        # Start hidden
        self.hide()

    def _position_window(self) -> None:
        """Position window based on configuration."""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        position = self.config.ptt.overlay_position
        margin = 20

        if position == "top-right":
            x = screen_width - WINDOW_WIDTH - margin
            y = margin
        elif position == "top-left":
            x = margin
            y = margin
        elif position == "bottom-right":
            x = screen_width - WINDOW_WIDTH - margin
            y = screen_height - WINDOW_HEIGHT - margin
        elif position == "bottom-left":
            x = margin
            y = screen_height - WINDOW_HEIGHT - margin
        else:
            # Default to top-right
            x = screen_width - WINDOW_WIDTH - margin
            y = margin

        self.window.geometry(f"+{x}+{y}")

    def update_state(self, state: str) -> None:
        """Update overlay to show new state.

        Args:
            state: New state name
        """
        self.current_state = state

        if state == "idle":
            self.hide()
        else:
            self.show()

            # Update label
            if self.label:
                self.label.config(
                    text=STATE_MESSAGES.get(state, state),
                    bg=STATE_COLORS.get(state, "#6c757d"),
                )

    def show(self) -> None:
        """Show overlay window."""
        if self.window:
            self.window.deiconify()
            self.window.update()

    def hide(self) -> None:
        """Hide overlay window."""
        if self.window:
            self.window.withdraw()

    def start(self) -> None:
        """Start overlay main loop."""
        if self.window:
            self.window.mainloop()

    def stop(self) -> None:
        """Stop overlay and close window."""
        if self.window:
            self.window.quit()
            self.window.destroy()
