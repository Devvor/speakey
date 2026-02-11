"""Base backend interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Union


class BaseBackend(ABC):
    """Abstract base class for ASR backends."""

    @abstractmethod
    def load_model(self):
        """Load the ASR model.

        Returns:
            Loaded model instance
        """
        pass

    @abstractmethod
    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results containing:
                - text: Transcribed text
                - timestamps: Optional timestamp data
        """
        pass
