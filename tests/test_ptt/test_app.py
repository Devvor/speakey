"""Tests for PTT application."""

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


def test_ptt_app_initialization():
    """Test PTT app initializes all components."""
    from src.ptt.app import PTTApp
    from src.config import Config

    config = Config()

    with patch("src.ptt.app.PTTController"):
        with patch("src.ptt.app.StatusOverlay"):
            app = PTTApp(config)

            assert app.config == config


def test_ptt_app_start_stop():
    """Test app start and stop."""
    from src.ptt.app import PTTApp
    from src.config import Config

    config = Config()

    with patch("src.ptt.app.PTTController") as mock_controller:
        with patch("src.ptt.app.StatusOverlay") as mock_overlay:
            app = PTTApp(config)

            app.stop()
            mock_controller.return_value.stop.assert_called_once()
            mock_overlay.return_value.stop.assert_called_once()
