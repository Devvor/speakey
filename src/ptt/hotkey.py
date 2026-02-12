"""Global hotkey listener for push-to-talk."""

from pynput import keyboard
from typing import Callable, Optional
import time

from ..config import Config


class HotkeyListener:
    """Listens for global hotkey press/release events."""

    def __init__(self, config: Config):
        """Initialize hotkey listener.

        Args:
            config: Application configuration
        """
        self.config = config
        self.is_pressed = False
        self.press_time: Optional[float] = None
        self.listener: Optional[keyboard.Listener] = None

        # Callbacks
        self.on_press: Optional[Callable] = None
        self.on_release: Optional[Callable] = None

        # Parse hotkey
        self.target_key = self._parse_hotkey(config.ptt.hotkey)

    def _parse_hotkey(self, hotkey: str) -> keyboard.Key:
        """Parse hotkey string to keyboard.Key.

        Args:
            hotkey: Hotkey name (e.g., 'option', 'alt', 'ctrl')

        Returns:
            Parsed keyboard.Key
        """
        hotkey_map = {
            "option": keyboard.Key.alt,  # Option key on Mac is alt
            "alt": keyboard.Key.alt,
            "ctrl": keyboard.Key.ctrl,
            "shift": keyboard.Key.shift,
            "cmd": keyboard.Key.cmd,
            "command": keyboard.Key.cmd,
        }

        return hotkey_map.get(hotkey.lower(), keyboard.Key.alt)

    def start(self) -> None:
        """Start listening for hotkey events."""
        self.listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self.listener.start()

    def stop(self) -> None:
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None

    def _on_key_press(self, key):
        """Handle key press event.

        Args:
            key: Pressed key
        """
        if key == self.target_key and not self.is_pressed:
            self._handle_press()

    def _on_key_release(self, key):
        """Handle key release event.

        Args:
            key: Released key
        """
        if key == self.target_key and self.is_pressed:
            self._handle_release()

    def _handle_press(self) -> None:
        """Handle hotkey press."""
        self.is_pressed = True
        self.press_time = time.time()

        if self.on_press:
            self.on_press()

    def _handle_release(self) -> None:
        """Handle hotkey release."""
        self.is_pressed = False
        self.press_time = None

        if self.on_release:
            self.on_release()

    def get_hold_duration(self) -> float:
        """Get current hold duration in seconds.

        Returns:
            Hold duration in seconds (0 if not pressed)
        """
        if not self.is_pressed or not self.press_time:
            return 0.0

        return time.time() - self.press_time
