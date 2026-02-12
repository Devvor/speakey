"""Tests for daemon recording controller."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.config import Config
from src.daemon.controller import DaemonRecordingController


@pytest.fixture
def config():
    """Test configuration."""
    return Config()


@pytest.fixture
def controller(config):
    """Test controller."""
    with patch("src.daemon.controller.ModelWrapper"):
        with patch("src.daemon.controller.AudioRecorder"):
            return DaemonRecordingController(config)


def test_controller_initialization(controller):
    """Test controller initialization."""
    assert controller.state == "idle"
    assert controller.recorder is not None
    assert controller.model is not None


def test_start_recording_from_idle(controller):
    """Test starting recording from idle state."""
    response = controller.start_recording()

    assert response["status"] == "ok"
    assert response["message"] == "Recording started"
    assert controller.state == "recording"
    controller.recorder.start.assert_called_once()


def test_start_recording_invalid_state(controller):
    """Test starting recording from non-idle state."""
    controller.state = "recording"

    response = controller.start_recording()

    assert response["status"] == "error"
    assert "Cannot start recording" in response["message"]


def test_stop_recording_success(controller):
    """Test stopping recording successfully."""
    # Setup
    controller.state = "recording"
    controller.recorder.stop.return_value = np.array([[0.1], [0.2], [0.3]])
    controller.model.transcribe.return_value = {"text": "test transcription"}

    response = controller.stop_recording()

    assert response["status"] == "ok"
    assert response["message"] == "Transcription complete"
    assert response["text"] == "test transcription"


def test_stop_recording_no_audio(controller):
    """Test stopping recording with no audio."""
    controller.state = "recording"
    controller.recorder.stop.return_value = np.array([])

    response = controller.stop_recording()

    assert response["status"] == "error"
    assert "No audio recorded" in response["message"]
    assert controller.state == "idle"


def test_toggle_recording(controller):
    """Test toggling recording."""
    # Toggle from idle (start)
    response = controller.toggle_recording()
    assert response["status"] == "ok"
    assert controller.state == "recording"

    # Toggle from recording (stop)
    controller.recorder.stop.return_value = np.array([[0.1], [0.2]])
    controller.model.transcribe.return_value = {"text": "test"}

    response = controller.toggle_recording()
    assert response["status"] == "ok"


def test_get_state(controller):
    """Test getting current state."""
    response = controller.get_state()

    assert response["status"] == "ok"
    assert response["state"] == "idle"
