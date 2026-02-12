"""Tests for push-to-talk controller."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import numpy as np


def test_controller_initialization():
    """Test controller initializes correctly."""
    from src.ptt.controller import PTTController
    from src.config import Config

    config = Config()

    with patch("src.ptt.controller.HotkeyListener"):
        with patch("src.ptt.controller.AudioRecorder"):
            with patch("src.ptt.controller.ModelWrapper"):
                controller = PTTController(config)

                assert controller.config == config
                assert controller.state == "idle"


def test_controller_state_transitions():
    """Test state transitions: idle → holding → recording → transcribing → done."""
    from src.ptt.controller import PTTController
    from src.config import Config

    config = Config()
    config.ptt.hold_threshold = 0.1  # Short threshold for testing

    with patch("src.ptt.controller.HotkeyListener") as mock_hotkey:
        with patch("src.ptt.controller.AudioRecorder") as mock_recorder:
            with patch("src.ptt.controller.ModelWrapper") as mock_model:
                # Setup mocks
                mock_recorder_instance = Mock()
                mock_recorder_instance.stop.return_value = np.array([[0.1], [0.2], [0.3]])
                mock_recorder_instance.save_audio = Mock()
                mock_recorder.return_value = mock_recorder_instance

                mock_model_instance = Mock()
                mock_model_instance.transcribe.return_value = {"text": "test"}
                mock_model.return_value = mock_model_instance

                controller = PTTController(config)

                # Idle → Holding
                controller._on_hotkey_press()
                assert controller.state == "holding"

                # Wait for threshold to pass (with some buffer)
                time.sleep(0.2)
                assert controller.state == "recording"

                # Recording → Transcribing
                controller._on_hotkey_release()
                time.sleep(0.1)  # Allow async operations to complete
                assert controller.state in ["transcribing", "done"]


def test_controller_hold_threshold_not_met():
    """Test that recording doesn't start if threshold not met."""
    from src.ptt.controller import PTTController
    from src.config import Config

    config = Config()
    config.ptt.hold_threshold = 2.0

    with patch("src.ptt.controller.HotkeyListener"):
        with patch("src.ptt.controller.AudioRecorder") as mock_recorder:
            with patch("src.ptt.controller.ModelWrapper"):
                mock_recorder_instance = Mock()
                mock_recorder.return_value = mock_recorder_instance

                controller = PTTController(config)

                controller._on_hotkey_press()
                time.sleep(0.1)  # Less than threshold
                controller._on_hotkey_release()

                # Should not have started recording
                assert controller.state == "idle"
                mock_recorder_instance.start.assert_not_called()
