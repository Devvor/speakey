"""Base backend interface."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseBackend(ABC):
    """Abstract base class for ASR backends."""

    @abstractmethod
    def load_model(self):
        """Load the ASR model.

        Returns:
            Loaded model instance
        """

    @abstractmethod
    def transcribe(self, audio_path: str | Path, timestamps: bool = True) -> dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results containing:
                - text: Transcribed text
                - timestamps: Optional timestamp data
        """
