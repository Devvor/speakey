"""Tests for backend abstraction."""

import pytest
from unittest.mock import Mock, patch


def test_base_backend_interface():
    """Test base backend interface."""
    from src.backends.base import BaseBackend

    class TestBackend(BaseBackend):
        def load_model(self):
            return Mock()

        def transcribe(self, audio_path, timestamps=True):
            return {"text": "test"}

    backend = TestBackend()
    assert hasattr(backend, "load_model")
    assert hasattr(backend, "transcribe")


def test_nemo_backend_initialization():
    """Test NeMo backend initialization."""
    from src.backends.nemo_backend import NeMoBackend
    from src.config import Config

    config = Config(device="cpu")

    with patch("src.backends.nemo_backend.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        backend = NeMoBackend(config)

        assert backend.model == mock_model


def test_mlx_backend_initialization():
    """Test MLX backend initialization."""
    pytest.importorskip("mlx", reason="MLX not installed")

    from src.backends.mlx_backend import MLXBackend
    from src.config import Config

    config = Config()

    with patch("src.backends.mlx_backend.mlx"):
        backend = MLXBackend(config)

        assert hasattr(backend, "model")
