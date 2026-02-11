"""Model wrapper for Parakeet TDT ASR."""

import os
from pathlib import Path
from typing import Dict, Union

from .config import Config

# Lazy import to allow mocking in tests
nemo_asr = None


class ModelWrapper:
    """Wrapper for Parakeet TDT ASR model."""

    def __init__(self, config: Config):
        """Initialize model wrapper.

        Args:
            config: Application configuration
        """
        self.config = config
        self._setup_environment()
        self.model = self._load_model()

    def _setup_environment(self) -> None:
        """Set up environment variables for Apple Silicon."""
        if self.config.is_mac and self.config.enable_mps_fallback:
            os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    def _load_model(self):
        """Load the ASR model.

        Returns:
            Loaded NeMo ASR model
        """
        global nemo_asr
        if nemo_asr is None:
            import nemo.collections.asr as nemo_asr_import
            nemo_asr = nemo_asr_import

        model = nemo_asr.models.ASRModel.from_pretrained(
            model_name=self.config.model_name
        )
        return model

    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results
        """
        audio_path = str(audio_path)

        # Transcribe with or without timestamps
        output = self.model.transcribe([audio_path], timestamps=timestamps)

        # Parse results
        result = {"text": output[0].text}

        if timestamps and hasattr(output[0], "timestamp"):
            result["timestamps"] = {
                "word": output[0].timestamp.get("word", []),
                "segment": output[0].timestamp.get("segment", []),
            }

        return result
