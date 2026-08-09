"""Tests for model wrapper."""

from unittest.mock import Mock, patch


def test_model_wrapper_initialization():
    """Test model wrapper initializes correctly."""
    from src.config import Config
    from src.model import ModelWrapper

    config = Config(device="cpu")

    with patch("src.backends.factory.BackendFactory.create_backend") as mock_create:
        mock_backend = Mock()
        mock_create.return_value = mock_backend

        wrapper = ModelWrapper(config)

        assert wrapper.config == config
        assert wrapper.backend == mock_backend
        mock_create.assert_called_once_with(config)


def test_model_wrapper_transcribe_simple(config, temp_audio_file):
    """Test simple transcription without timestamps."""
    from src.model import ModelWrapper

    with patch("src.backends.factory.BackendFactory.create_backend") as mock_create:
        mock_backend = Mock()
        mock_backend.transcribe.return_value = {"text": "test transcription"}
        mock_create.return_value = mock_backend

        wrapper = ModelWrapper(config)
        result = wrapper.transcribe(temp_audio_file, timestamps=False)

        assert result["text"] == "test transcription"
        assert "timestamps" not in result
        mock_backend.transcribe.assert_called_once_with(temp_audio_file, timestamps=False)


def test_model_wrapper_transcribe_with_timestamps(config, temp_audio_file):
    """Test transcription with timestamps."""
    from src.model import ModelWrapper

    with patch("src.backends.factory.BackendFactory.create_backend") as mock_create:
        mock_backend = Mock()
        mock_backend.transcribe.return_value = {
            "text": "test transcription",
            "timestamps": {
                "word": [{"start": 0.0, "end": 0.5, "word": "test"}],
                "segment": [{"start": 0.0, "end": 1.0, "segment": "test transcription"}],
            },
        }
        mock_create.return_value = mock_backend

        wrapper = ModelWrapper(config)
        result = wrapper.transcribe(temp_audio_file, timestamps=True)

        assert result["text"] == "test transcription"
        assert "word" in result["timestamps"]
        assert "segment" in result["timestamps"]
        mock_backend.transcribe.assert_called_once_with(temp_audio_file, timestamps=True)
