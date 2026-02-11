"""Backend implementations for different platforms."""

from .base import BaseBackend
from .nemo_backend import NeMoBackend

__all__ = ["BaseBackend", "NeMoBackend"]

# Conditionally import MLX backend
try:
    from .mlx_backend import MLXBackend

    __all__.append("MLXBackend")
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
