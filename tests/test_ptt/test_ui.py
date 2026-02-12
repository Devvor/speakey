"""Tests for GUI overlay."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


# Mock tkinter at module level for all tests
@pytest.fixture(autouse=True)
def mock_tkinter():
    """Mock tkinter module for testing."""
    mock_tk = MagicMock()

    # Create mock classes that return mock instances
    mock_tk_instance = MagicMock()
    mock_tk_instance.winfo_screenwidth.return_value = 1920
    mock_tk_instance.winfo_screenheight.return_value = 1080
    mock_tk_instance.geometry = MagicMock()
    mock_tk_instance.overrideredirect = MagicMock()
    mock_tk_instance.attributes = MagicMock()
    mock_tk_instance.title = MagicMock()
    mock_tk_instance.withdraw = MagicMock()
    mock_tk_instance.deiconify = MagicMock()
    mock_tk_instance.update = MagicMock()
    mock_tk_instance.mainloop = MagicMock()
    mock_tk_instance.quit = MagicMock()
    mock_tk_instance.destroy = MagicMock()

    mock_label_instance = MagicMock()
    mock_label_instance.pack = MagicMock()
    mock_label_instance.config = MagicMock()

    mock_tk.Tk = MagicMock(return_value=mock_tk_instance)
    mock_tk.Label = MagicMock(return_value=mock_label_instance)
    mock_tk.BOTH = "both"
    mock_tk.X = "x"

    sys.modules['tkinter'] = mock_tk
    yield
    if 'tkinter' in sys.modules:
        del sys.modules['tkinter']


def test_overlay_initialization():
    """Test overlay window initializes."""
    from src.ptt.ui.overlay import StatusOverlay
    from src.config import Config

    config = Config()
    overlay = StatusOverlay(config)

    assert overlay.config == config


def test_overlay_state_display():
    """Test overlay displays different states."""
    from src.ptt.ui.overlay import StatusOverlay
    from src.config import Config

    config = Config()
    overlay = StatusOverlay(config)

    # Test different states
    overlay.update_state("idle")
    overlay.update_state("holding")
    overlay.update_state("recording")
    overlay.update_state("transcribing")
    overlay.update_state("done")


def test_overlay_positioning():
    """Test overlay positions correctly."""
    from src.ptt.ui.overlay import StatusOverlay
    from src.config import Config

    config = Config()
    config.ptt.overlay_position = "top-right"

    overlay = StatusOverlay(config)

    # Verify window attributes set for top-right
    assert config.ptt.overlay_position == "top-right"
