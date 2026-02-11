"""Configuration management for Parakeet STT."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Application configuration."""

    # Model settings
    model_name: str = "nvidia/parakeet-tdt-0.6b-v2"
    device: str = "mps"  # mps for Mac, cuda for NVIDIA, cpu for fallback

    # Audio settings
    sample_rate: int = 16000
    supported_formats: tuple = (".wav", ".flac")

    # Output settings
    output_dir: Path = Path("output")
    include_timestamps: bool = True

    # Environment overrides
    enable_mps_fallback: bool = os.getenv("PYTORCH_ENABLE_MPS_FALLBACK", "1") == "1"

    def __post_init__(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(exist_ok=True)

    @property
    def is_mac(self) -> bool:
        """Check if running on macOS."""
        import platform

        return platform.system() == "Darwin"

    def get_device(self) -> str:
        """Get appropriate device based on platform."""
        if self.is_mac:
            return "mps"
        return "cuda" if self._cuda_available() else "cpu"

    @staticmethod
    def _cuda_available() -> bool:
        """Check if CUDA is available."""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False
