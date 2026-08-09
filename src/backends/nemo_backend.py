"""NeMo backend implementation."""

import os
from pathlib import Path

import nemo.collections.asr as nemo_asr

from ..config import Config
from .base import BaseBackend


class NeMoBackend(BaseBackend):
    """NeMo-based ASR backend."""

    def __init__(self, config: Config):
        """Initialize NeMo backend.

        Args:
            config: Application configuration
        """
        self.config = config
        self._setup_environment()
        self.model = self.load_model()

    def _setup_environment(self) -> None:
        """Set up environment variables."""
        if self.config.is_mac and self.config.enable_mps_fallback:
            os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    def load_model(self):
        """Load NeMo ASR model."""
        return nemo_asr.models.ASRModel.from_pretrained(model_name=self.config.model_name)

    def transcribe(self, audio_path: str | Path, timestamps: bool = True) -> dict:
        """Transcribe audio using NeMo."""
        audio_path = str(audio_path)
        output = self.model.transcribe([audio_path], timestamps=timestamps)

        result = {"text": output[0].text}

        if timestamps and hasattr(output[0], "timestamp"):
            result["timestamps"] = {
                "word": output[0].timestamp.get("word", []),
                "segment": output[0].timestamp.get("segment", []),
            }

        return result
