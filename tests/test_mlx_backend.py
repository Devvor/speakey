"""Tests for MLX backend with real model."""

from pathlib import Path

import pytest


def test_mlx_backend_transcription():
    """Test MLX backend with real audio file."""
    pytest.importorskip("parakeet_mlx", reason="parakeet-mlx not installed")

    from src.backends.mlx_backend import MLXBackend
    from src.config import Config

    # Use the test audio file
    audio_file = Path("tests/fixtures/sample_audio.wav")
    if not audio_file.exists():
        pytest.skip("Test audio file not available")

    config = Config()
    backend = MLXBackend(config)

    # Transcribe
    result = backend.transcribe(audio_file, timestamps=True)

    # Verify output format
    assert "text" in result
    assert len(result["text"]) > 0
    assert "timestamps" in result
    assert "word" in result["timestamps"]
    assert "segment" in result["timestamps"]


def test_mlx_backend_matches_nemo_format():
    """Test that MLX backend output matches NeMo format."""
    pytest.importorskip("parakeet_mlx", reason="parakeet-mlx not installed")

    from src.backends.mlx_backend import MLXBackend
    from src.config import Config

    audio_file = Path("tests/fixtures/sample_audio.wav")
    if not audio_file.exists():
        pytest.skip("Test audio file not available")

    config = Config()

    # Test MLX backend produces compatible output
    mlx_backend = MLXBackend(config)
    mlx_result = mlx_backend.transcribe(audio_file, timestamps=False)

    # Check structure matches NeMo backend
    assert isinstance(mlx_result, dict)
    assert "text" in mlx_result
    assert isinstance(mlx_result["text"], str)


def test_mlx_backend_with_timestamps():
    """Test MLX backend timestamp output structure."""
    pytest.importorskip("parakeet_mlx", reason="parakeet-mlx not installed")

    from src.backends.mlx_backend import MLXBackend
    from src.config import Config

    audio_file = Path("tests/fixtures/sample_audio.wav")
    if not audio_file.exists():
        pytest.skip("Test audio file not available")

    config = Config()
    backend = MLXBackend(config)

    result = backend.transcribe(audio_file, timestamps=True)

    # Verify timestamp structure
    assert "timestamps" in result
    assert "word" in result["timestamps"]
    assert "segment" in result["timestamps"]

    # Verify word timestamps
    if len(result["timestamps"]["word"]) > 0:
        word = result["timestamps"]["word"][0]
        assert "start" in word
        assert "end" in word
        assert "word" in word
        assert isinstance(word["start"], (int, float))
        assert isinstance(word["end"], (int, float))

    # Verify segment timestamps
    if len(result["timestamps"]["segment"]) > 0:
        segment = result["timestamps"]["segment"][0]
        assert "start" in segment
        assert "end" in segment
        assert "segment" in segment
        assert isinstance(segment["start"], (int, float))
        assert isinstance(segment["end"], (int, float))
