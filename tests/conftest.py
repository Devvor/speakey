"""Shared pytest fixtures."""

import pytest
from pathlib import Path
from src.config import Config


@pytest.fixture
def config():
    """Create test configuration."""
    return Config(
        output_dir=Path("output/test"),
        device="cpu",  # Use CPU for tests
    )


@pytest.fixture
def temp_audio_file(tmp_path):
    """Create temporary audio file for testing."""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.touch()
    return audio_file


@pytest.fixture
def sample_transcription():
    """Sample transcription output."""
    return {
        "text": "This is a test transcription.",
        "timestamps": {
            "word": [
                {"start": 0.0, "end": 0.5, "word": "This"},
                {"start": 0.5, "end": 0.8, "word": "is"},
            ]
        },
    }


@pytest.fixture
def real_audio_file():
    """Path to real audio file for integration tests."""
    return Path("tests/fixtures/sample_audio.wav")
