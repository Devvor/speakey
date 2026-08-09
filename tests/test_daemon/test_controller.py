"""Tests for daemon recording controller."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.config import Config
from src.daemon.controller import DaemonRecordingController


@pytest.fixture
def config():
    """Test configuration."""
    return Config()


@pytest.fixture
def controller(config):
    """Test controller with mocked recorder/model dependencies."""
    mock_recorder = MagicMock()
    mock_model = MagicMock()

    with (
        patch("src.daemon.controller.ModelWrapper", return_value=mock_model),
        patch("src.daemon.controller.AudioRecorder", return_value=mock_recorder),
    ):
        ctrl = DaemonRecordingController(config)
        ctrl._mock_recorder = mock_recorder
        ctrl._mock_model = mock_model
        yield ctrl


def test_controller_initialization(controller):
    """Test controller initialization (recorder/model are lazy)."""
    assert controller.state == "idle"
    assert controller.recorder is None
    assert controller.model is None


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
    controller.start_recording()
    controller._mock_recorder.stop.return_value = np.array([[0.1], [0.2], [0.3]])
    controller._mock_model.transcribe.return_value = {"text": "test transcription"}

    response = controller.stop_recording()

    assert response["status"] == "ok"
    assert response["message"] == "Transcription complete"
    assert response["text"] == "test transcription"


def test_stop_recording_no_audio(controller):
    """Test stopping recording with no audio."""
    controller.start_recording()
    controller._mock_recorder.stop.return_value = np.array([])

    response = controller.stop_recording()

    assert response["status"] == "error"
    assert "No audio recorded" in response["message"]
    assert controller.state == "idle"


def test_toggle_recording(controller):
    """Test toggling recording."""
    response = controller.toggle_recording()
    assert response["status"] == "ok"
    assert controller.state == "recording"

    controller._mock_recorder.stop.return_value = np.array([[0.1], [0.2]])
    controller._mock_model.transcribe.return_value = {"text": "test"}

    response = controller.toggle_recording()
    assert response["status"] == "ok"


def test_get_state(controller):
    """Test getting current state."""
    response = controller.get_state()

    assert response["status"] == "ok"
    assert response["state"] == "idle"
