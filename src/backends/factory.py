"""Backend factory for automatic backend selection."""

import platform
from typing import Type

from .base import BaseBackend
from .nemo_backend import NeMoBackend
from ..config import Config

# Check MLX availability
try:
    from .mlx_backend import MLXBackend

    MLX_AVAILABLE = True
except (ImportError, RuntimeError):
    MLX_AVAILABLE = False


class BackendFactory:
    """Factory for creating appropriate backend based on platform."""

    @staticmethod
    def get_backend_class(config: Config) -> Type[BaseBackend]:
        """Select appropriate backend based on platform and configuration.

        Args:
            config: Application configuration

        Returns:
            Backend class to use
        """
        # Force specific backend if requested
        if hasattr(config, "backend") and config.backend:
            if config.backend == "mlx" and MLX_AVAILABLE:
                return MLXBackend
            elif config.backend == "nemo":
                return NeMoBackend

        # Auto-select based on platform
        if BackendFactory._is_apple_silicon() and MLX_AVAILABLE:
            return MLXBackend

        # Default to NeMo
        return NeMoBackend

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
