"""Tests for backend factory."""

from unittest.mock import patch


def test_backend_factory_selects_mlx_on_mac():
    """Test MLX backend selected on macOS with Apple Silicon."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.platform.system", return_value="Darwin"):
        with patch("src.backends.factory.platform.processor", return_value="arm"):
            with patch("src.backends.factory.MLX_AVAILABLE", True):
                backend_class = BackendFactory.get_backend_class(config)

                assert backend_class.__name__ == "MLXBackend"


def test_backend_factory_selects_nemo_on_linux():
    """Test NeMo backend selected on Linux."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.platform.system", return_value="Linux"):
        backend_class = BackendFactory.get_backend_class(config)

        assert backend_class.__name__ == "NeMoBackend"


def test_backend_factory_fallback_to_nemo():
    """Test fallback to NeMo when MLX unavailable."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.MLX_AVAILABLE", False):
        backend_class = BackendFactory.get_backend_class(config)

        assert backend_class.__name__ == "NeMoBackend"
