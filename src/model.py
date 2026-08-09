"""Model wrapper for Parakeet TDT ASR."""

from pathlib import Path

from .backends.factory import BackendFactory
from .config import Config


class ModelWrapper:
    """Wrapper for Parakeet TDT ASR model with automatic backend selection."""

    def __init__(self, config: Config):
        """Initialize model wrapper.

        Args:
            config: Application configuration
        """
        self.config = config
        self.backend = BackendFactory.create_backend(config)

    def transcribe(self, audio_path: str | Path, timestamps: bool = True) -> dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results
        """
        return self.backend.transcribe(audio_path, timestamps=timestamps)
