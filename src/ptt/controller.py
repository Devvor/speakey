"""Push-to-talk controller coordinating hotkey, recording, and transcription."""

import time
from pathlib import Path
from typing import Optional, Callable
import tempfile

from ..config import Config
from ..model import ModelWrapper
from .hotkey import HotkeyListener
from .recorder import AudioRecorder


class PTTController:
    """Coordinates push-to-talk workflow."""

    # States: idle → holding → recording → transcribing → done

    def __init__(self, config: Config):
        """Initialize push-to-talk controller.

        Args:
            config: Application configuration
        """
        self.config = config
        self.state = "idle"

        # Components
        print("  - Creating hotkey listener...")
        self.hotkey_listener = HotkeyListener(config)
        print("  - Creating audio recorder...")
        self.recorder = AudioRecorder(config)
        print("  - Loading model (this may take a moment)...")
        self.model = ModelWrapper(config)
        print("  - Model loaded!")

        # Timing
        self.hold_start_time: Optional[float] = None
        self.threshold_timer: Optional[float] = None

        # Callbacks for UI updates
        self.on_state_change: Optional[Callable[[str], None]] = None

        # Setup hotkey callbacks
        self.hotkey_listener.on_press = self._on_hotkey_press
        self.hotkey_listener.on_release = self._on_hotkey_release

    def start(self) -> None:
        """Start the push-to-talk controller."""
        self.hotkey_listener.start()
        self._update_state("idle")

    def stop(self) -> None:
        """Stop the push-to-talk controller."""
        self.hotkey_listener.stop()
        if self.recorder.is_recording:
            self.recorder.stop()

    def _update_state(self, new_state: str) -> None:
        """Update state and notify callback.

        Args:
            new_state: New state name
        """
        self.state = new_state

        if self.on_state_change:
            self.on_state_change(new_state)

    def _on_hotkey_press(self) -> None:
        """Handle hotkey press event."""
        if self.state != "idle":
            return

        self.hold_start_time = time.time()
        self._update_state("holding")

        # Start threshold timer
        self._check_threshold()

    def _check_threshold(self) -> None:
        """Check if hold threshold is met and start recording."""
        if self.state != "holding":
            return

        if not self.hold_start_time:
            return

        hold_duration = time.time() - self.hold_start_time

        if hold_duration >= self.config.ptt.hold_threshold:
            # Threshold met, start recording
            self._start_recording()
        else:
            # Check again after a short delay
            import threading
            threading.Timer(0.1, self._check_threshold).start()

    def _start_recording(self) -> None:
        """Start audio recording."""
        self._update_state("recording")
        self.recorder.start()

    def _on_hotkey_release(self) -> None:
        """Handle hotkey release event."""
        if self.state == "holding":
            # Released before threshold - cancel
            self.hold_start_time = None
            self._update_state("idle")

        elif self.state == "recording":
            # Stop recording and transcribe
            self._stop_recording()

    def _stop_recording(self) -> None:
        """Stop recording and start transcription."""
        audio_data = self.recorder.stop()

        if len(audio_data) == 0:
            self._update_state("idle")
            return

        self._update_state("transcribing")

        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        self.recorder.save_audio(tmp_path)

        # Transcribe
        try:
            result = self.model.transcribe(tmp_path, timestamps=False)
            transcription = result["text"]

            # Handle transcription result
            self._on_transcription_complete(transcription)

        finally:
            # Clean up temp file
            tmp_path.unlink()

    def _on_transcription_complete(self, text: str) -> None:
        """Handle completed transcription.

        Args:
            text: Transcribed text
        """
        # Copy to clipboard if enabled
        if self.config.ptt.auto_copy:
            self._copy_to_clipboard(text)

        self._update_state("done")

        # Return to idle after brief delay
        import threading
        threading.Timer(2.0, lambda: self._update_state("idle")).start()

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard.

        Args:
            text: Text to copy
        """
        try:
            import pyperclip
            pyperclip.copy(text)
        except ImportError:
            print("Warning: pyperclip not installed, clipboard not available")
