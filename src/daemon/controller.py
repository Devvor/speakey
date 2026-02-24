"""Recording controller for daemon mode."""

import tempfile
from pathlib import Path
from typing import Optional, Callable

from ..config import Config
from ..model import ModelWrapper
from ..ptt.recorder import AudioRecorder


class DaemonRecordingController:
    """Controls recording and transcription in daemon mode."""

    # States: idle → recording → transcribing → done
    def __init__(self, config: Config):
        """Initialize recording controller.

        Args:
            config: Application configuration
        """
        self.config = config
        self.state = "idle"

        # Components (lazy initialization)
        self.recorder: Optional[AudioRecorder] = None
        self.model: Optional[ModelWrapper] = None

        # Callbacks
        self.on_state_change: Optional[Callable[[str], None]] = None
        self.on_transcription_complete: Optional[Callable[[str], None]] = None

    def _ensure_recorder(self) -> None:
        """Ensure recorder is initialized."""
        if self.recorder is None:
            print("Initializing audio recorder...")
            self.recorder = AudioRecorder(self.config)

    def _ensure_model(self) -> None:
        """Ensure model is initialized."""
        if self.model is None:
            print("Loading transcription model (this may take a moment)...")
            self.model = ModelWrapper(self.config)
            print("Model loaded!")

    def start_recording(self) -> dict:
        """Start audio recording.

        Returns:
            Response dictionary
        """
        try:
            if self.state != "idle":
                return {
                    "status": "error",
                    "message": f"Cannot start recording in state: {self.state}",
                }

            # Only need recorder for recording (model loaded later during transcription)
            self._ensure_recorder()

            self._update_state("recording")
            self.recorder.start()

            return {"status": "ok", "message": "Recording started"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to start recording: {e}"}

    def stop_recording(self) -> dict:
        """Stop recording and transcribe.

        Returns:
            Response dictionary
        """
        try:
            if self.state != "recording":
                return {
                    "status": "error",
                    "message": f"Cannot stop recording in state: {self.state}",
                }

            # Stop recording
            audio_data = self.recorder.stop()

            if len(audio_data) == 0:
                self._update_state("idle")
                return {"status": "error", "message": "No audio recorded"}

            # Start transcription
            self._update_state("transcribing")

            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = Path(tmp.name)

            self.recorder.save_audio(tmp_path)

            # Ensure model is loaded (may take time on first call)
            self._ensure_model()

            # Transcribe
            result = self.model.transcribe(tmp_path, timestamps=False)
            transcription = result["text"]

            # Handle transcription result
            self._handle_transcription_complete(transcription)

            # Clean up temp file
            if tmp_path.exists():
                tmp_path.unlink()

            return {"status": "ok", "message": "Transcription complete", "text": transcription}

        except Exception as e:
            self._update_state("idle")
            return {"status": "error", "message": f"Transcription failed: {e}"}

    def toggle_recording(self) -> dict:
        """Toggle recording on/off.

        Returns:
            Response dictionary
        """
        if self.state == "idle":
            return self.start_recording()
        elif self.state == "recording":
            return self.stop_recording()
        else:
            return {
                "status": "error",
                "message": f"Cannot toggle in state: {self.state}",
            }

    def get_state(self) -> dict:
        """Get current state.

        Returns:
            State dictionary
        """
        return {"status": "ok", "state": self.state}

    def _update_state(self, new_state: str) -> None:
        """Update state and notify callback.

        Args:
            new_state: New state name
        """
        self.state = new_state

        if self.on_state_change:
            self.on_state_change(new_state)

    def _handle_transcription_complete(self, text: str) -> None:
        """Handle completed transcription.

        Args:
            text: Transcribed text
        """
        # Copy to clipboard if enabled
        if self.config.ptt.auto_copy:
            self._copy_to_clipboard(text)

        # Notify callback
        if self.on_transcription_complete:
            self.on_transcription_complete(text)

        # Update state
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
