"""Tests for real-time audio recorder."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np


def test_recorder_initialization():
    """Test recorder initializes correctly."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    assert recorder.config == config
    assert recorder.is_recording is False
    assert recorder.audio_buffer == []


def test_recorder_start():
    """Test starting audio recording."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    with patch("src.ptt.recorder.sd.InputStream") as mock_stream:
        recorder.start()

        assert recorder.is_recording is True
        mock_stream.assert_called_once()


def test_recorder_stop():
    """Test stopping audio recording."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    with patch("src.ptt.recorder.sd.InputStream"):
        recorder.start()
        audio_data = recorder.stop()

        assert recorder.is_recording is False
        assert isinstance(audio_data, np.ndarray)


def test_recorder_get_audio_file(tmp_path):
    """Test saving recorded audio to file."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    # Simulate recording
    recorder.audio_buffer = [np.array([[0.1], [0.2], [0.3]])]

    output_file = tmp_path / "recording.wav"
    recorder.save_audio(output_file)

    assert output_file.exists()
