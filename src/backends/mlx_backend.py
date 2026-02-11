"""MLX backend implementation for Apple Silicon."""

from pathlib import Path
from typing import Dict, Union

from .base import BaseBackend
from ..config import Config


class MLXBackend(BaseBackend):
    """MLX-based ASR backend for Apple Neural Engine.

    This backend uses the parakeet-mlx implementation for optimized
    inference on Apple Silicon (M1/M2/M3) with direct ANE access.

    Provides 10x faster inference compared to CPU with 14x lower memory usage.
    """

    def __init__(self, config: Config):
        """Initialize MLX backend.

        Args:
            config: Application configuration

        Raises:
            RuntimeError: If parakeet-mlx package is not installed
        """
        self.config = config
        self.model = self.load_model()

    def load_model(self):
        """Load MLX ASR model.

        Returns:
            The parakeet-mlx transcribe_file function (no model preloading needed)

        Raises:
            RuntimeError: If parakeet-mlx package is not available
        """
        try:
            from parakeet_mlx import transcribe_file
            # Store the function for use in transcribe()
            # The actual model loading happens on first transcription call
            return transcribe_file
        except ImportError as e:
            raise RuntimeError(
                f"MLX backend not available: {e}\n"
                f"Install with: pip install -e .[mlx]\n"
                f"Then: pip install git+https://github.com/EliFuzz/parakeet-mlx.git"
            )

    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio using MLX.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results containing:
                - text: Transcribed text
                - timestamps: Optional word and segment timestamps

        Raises:
            RuntimeError: If transcription fails
        """
        audio_path = str(audio_path)

        try:
            # Call parakeet-mlx transcribe_file function
            result = self.model(audio_path)

            # Build response dict with transcribed text
            output = {"text": result.text}

            # Add timestamps if requested
            if timestamps:
                # Convert AlignedToken objects to our format
                word_timestamps = [
                    {
                        "start": token.start,
                        "end": token.end,
                        "word": token.text,
                    }
                    for token in result.tokens
                ]

                # Convert AlignedSentence objects to our format
                segment_timestamps = [
                    {
                        "start": sentence.start,
                        "end": sentence.end,
                        "segment": sentence.text,
                    }
                    for sentence in result.sentences
                ]

                output["timestamps"] = {
                    "word": word_timestamps,
                    "segment": segment_timestamps,
                }

            return output

        except Exception as e:
            raise RuntimeError(f"MLX transcription failed: {e}")
