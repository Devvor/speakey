"""Backend factory for automatic backend selection."""

import platform

from ..config import Config
from .base import BaseBackend

# Check NeMo availability
try:
    from .nemo_backend import NeMoBackend

    NEMO_AVAILABLE = True
except Exception:
    # Catch all exceptions since nemo dependencies may fail in various ways
    NEMO_AVAILABLE = False
    NeMoBackend = None

# Check MLX availability
try:
    from .mlx_backend import MLXBackend

    MLX_AVAILABLE = True
except Exception:
    MLX_AVAILABLE = False
    MLXBackend = None


class BackendFactory:
    """Factory for creating appropriate backend based on platform."""

    @staticmethod
    def get_backend_class(config: Config) -> type[BaseBackend]:
        """Select appropriate backend based on platform and configuration.

        Args:
            config: Application configuration

        Returns:
            Backend class to use

        Raises:
            RuntimeError: If no backend is available
        """
        # Force specific backend if requested
        if hasattr(config, "backend") and config.backend:
            if config.backend == "mlx":
                if MLX_AVAILABLE:
                    return MLXBackend
                raise RuntimeError("MLX backend requested but not available")
            elif config.backend == "nemo":
                if NEMO_AVAILABLE:
                    return NeMoBackend
                raise RuntimeError("NeMo backend requested but not available")

        # Auto-select based on platform
        if BackendFactory._is_apple_silicon() and MLX_AVAILABLE:
            return MLXBackend

        # Fallback to NeMo if available
        if NEMO_AVAILABLE:
            return NeMoBackend

        # If neither is available, raise error
        raise RuntimeError(
            "No backend available. Install either:\n"
            "  MLX: pip install -e .[mlx]\n"
            "  NeMo: pip install -e .[nemo]"
        )

    @staticmethod
    def _is_apple_silicon() -> bool:
        """Check if running on Apple Silicon.

        Returns:
            True if running on Apple Silicon (M1/M2/M3)
        """
        if platform.system() != "Darwin":
            return False

        # Check for ARM processor
        processor = platform.processor()
        return "arm" in processor.lower() or processor == ""

    @staticmethod
    def create_backend(config: Config) -> BaseBackend:
        """Create and initialize backend.

        Args:
            config: Application configuration

        Returns:
            Initialized backend instance
        """
        backend_class = BackendFactory.get_backend_class(config)
        return backend_class(config)
