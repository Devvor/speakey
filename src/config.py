"""Configuration management for Parakeet STT."""

import os
import platform
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PTTConfig:
    """Push-to-talk configuration."""

    # Hotkey settings
    hotkey: str = field(default_factory=lambda: PTTConfig._default_hotkey())
    hold_threshold: float = 2.0  # seconds to hold before recording starts

    # Audio settings
    sample_rate: int = 16000
    channels: int = 1  # mono
    chunk_size: int = 1024

    # UI settings
    overlay_position: str = "top-right"  # top-right, top-left, bottom-right, bottom-left
    overlay_opacity: float = 0.9
    show_waveform: bool = True

    # Clipboard settings
    auto_copy: bool = True

    @staticmethod
    def _default_hotkey() -> str:
        """Get default hotkey based on platform."""
        if platform.system() == "Darwin":
            return "option"  # Mac
        return "alt"  # Windows/Linux


@dataclass
class Config:
    """Application configuration."""

    # Model settings
    model_name: str = "nvidia/parakeet-tdt-0.6b-v3"
    device: str = "mps"  # mps for Mac, cuda for NVIDIA, cpu for fallback

    # Audio settings
    sample_rate: int = 16000
    supported_formats: tuple = (".wav", ".flac")

    # Output settings
    output_dir: Path = Path("output")
    include_timestamps: bool = True

    # Push-to-talk settings
    ptt: PTTConfig = field(default_factory=PTTConfig)

    # Environment overrides
    enable_mps_fallback: bool = os.getenv("PYTORCH_ENABLE_MPS_FALLBACK", "1") == "1"

    def __post_init__(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(exist_ok=True)

    @property
    def is_mac(self) -> bool:
        """Check if running on macOS."""
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
