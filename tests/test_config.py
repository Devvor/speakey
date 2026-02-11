"""Tests for configuration module."""

import pytest
from pathlib import Path
from src.config import Config


def test_config_defaults():
    """Test default configuration values."""
    config = Config()

    assert config.model_name == "nvidia/parakeet-tdt-0.6b-v2"
    assert config.sample_rate == 16000
    assert config.include_timestamps is True
    assert ".wav" in config.supported_formats
    assert ".flac" in config.supported_formats


def test_config_output_dir_creation(tmp_path):
    """Test output directory is created."""
    output_dir = tmp_path / "output"
    config = Config(output_dir=output_dir)

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_config_is_mac():
    """Test macOS detection."""
    import platform

    config = Config()
    expected = platform.system() == "Darwin"

    assert config.is_mac == expected


def test_config_get_device(config):
    """Test device selection logic."""
    device = config.get_device()

    assert device in ["mps", "cuda", "cpu"]
