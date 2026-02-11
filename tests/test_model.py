"""Tests for model wrapper."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


def test_model_wrapper_initialization():
    """Test model wrapper initializes correctly."""
    from src.model import ModelWrapper
    from src.config import Config

    config = Config(device="cpu")

    with patch("src.model.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        wrapper = ModelWrapper(config)

        assert wrapper.config == config
        assert wrapper.model == mock_model
        mock_nemo.models.ASRModel.from_pretrained.assert_called_once_with(
            model_name=config.model_name
        )


def test_model_wrapper_transcribe_simple(config, temp_audio_file):
    """Test simple transcription without timestamps."""
    from src.model import ModelWrapper

    with patch("src.model.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_result = Mock()
        mock_result.text = "test transcription"
        mock_model.transcribe.return_value = [mock_result]
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        wrapper = ModelWrapper(config)
        result = wrapper.transcribe(temp_audio_file, timestamps=False)

        assert result["text"] == "test transcription"
        assert "timestamps" not in result
        mock_model.transcribe.assert_called_once()


def test_model_wrapper_transcribe_with_timestamps(config, temp_audio_file):
    """Test transcription with timestamps."""
    from src.model import ModelWrapper

    with patch("src.model.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_result = Mock()
        mock_result.text = "test transcription"
        mock_result.timestamp = {
            "word": [{"start": 0.0, "end": 0.5, "word": "test"}],
            "segment": [{"start": 0.0, "end": 1.0, "segment": "test transcription"}],
        }
        mock_model.transcribe.return_value = [mock_result]
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        wrapper = ModelWrapper(config)
        result = wrapper.transcribe(temp_audio_file, timestamps=True)

        assert result["text"] == "test transcription"
        assert "word" in result["timestamps"]
        assert "segment" in result["timestamps"]
