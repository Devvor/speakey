"""Tests for push-to-talk configuration."""

import pytest
import platform
from unittest.mock import patch
from src.config import Config, PTTConfig


def test_ptt_config_defaults():
    """Test PTT configuration defaults."""
    ptt = PTTConfig()

    assert ptt.hold_threshold == 2.0
    assert ptt.sample_rate == 16000
    assert ptt.channels == 1
    assert ptt.overlay_position == "top-right"
    assert ptt.auto_copy is True


def test_ptt_default_hotkey_mac():
    """Test default hotkey on macOS."""
    with patch("platform.system", return_value="Darwin"):
        ptt = PTTConfig()
        assert ptt.hotkey == "option"


def test_ptt_default_hotkey_windows():
    """Test default hotkey on Windows."""
    with patch("platform.system", return_value="Windows"):
        ptt = PTTConfig()
        assert ptt.hotkey == "alt"


def test_config_includes_ptt():
    """Test main config includes PTT settings."""
    config = Config()

    assert hasattr(config, "ptt")
    assert isinstance(config.ptt, PTTConfig)


def test_ptt_custom_settings():
    """Test custom PTT settings."""
    ptt = PTTConfig(
        hotkey="ctrl",
        hold_threshold=3.0,
        overlay_position="bottom-right",
    )

    assert ptt.hotkey == "ctrl"
    assert ptt.hold_threshold == 3.0
    assert ptt.overlay_position == "bottom-right"
