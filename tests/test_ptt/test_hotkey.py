"""Tests for global hotkey listener."""

import pytest
from unittest.mock import Mock, patch
import time


def test_hotkey_listener_initialization():
    """Test hotkey listener initializes."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    assert listener.config == config
    assert listener.is_pressed is False


def test_hotkey_listener_press_callback():
    """Test press callback is called."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    press_called = False

    def on_press():
        nonlocal press_called
        press_called = True

    listener.on_press = on_press
    listener._handle_press()

    assert press_called is True


def test_hotkey_listener_release_callback():
    """Test release callback is called."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    release_called = False

    def on_release():
        nonlocal release_called
        release_called = True

    listener.on_release = on_release
    listener._handle_release()

    assert release_called is True


def test_hotkey_listener_hold_duration():
    """Test hold duration tracking."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    listener._handle_press()
    time.sleep(0.1)
    duration = listener.get_hold_duration()

    assert duration >= 0.1
