"""Model wrapper for Parakeet TDT ASR."""

from pathlib import Path
from typing import Dict, Union

from .config import Config
from .backends.factory import BackendFactory


class ModelWrapper:
    """Wrapper for Parakeet TDT ASR model with automatic backend selection."""

    def __init__(self, config: Config):
        """Initialize model wrapper.

        Args:
            config: Application configuration
        """
        self.config = config
        self.backend = BackendFactory.create_backend(config)

    def transcribe(self, audio_path: Union[str, Path], timestamps: bool = True) -> Dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results
        """
        return self.backend.transcribe(audio_path, timestamps=timestamps)
