"""Backend implementations for different platforms."""

from .base import BaseBackend

__all__ = ["BaseBackend"]

# Conditionally import NeMo backend
try:
    from .nemo_backend import NeMoBackend

    __all__.append("NeMoBackend")
    NEMO_AVAILABLE = True
except Exception:
    # Catch all exceptions since nemo dependencies may fail in various ways
    NEMO_AVAILABLE = False

# Conditionally import MLX backend
try:
    from .mlx_backend import MLXBackend

    __all__.append("MLXBackend")
    MLX_AVAILABLE = True
except (ImportError, RuntimeError):
    MLX_AVAILABLE = False
