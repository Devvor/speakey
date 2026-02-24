import os
from unittest.mock import patch, MagicMock
import pytest
from src.fn_ptt.manager import FnPttManager


@pytest.fixture
def manager(tmp_path):
    return FnPttManager(runtime_dir=tmp_path)


def test_is_not_running_when_no_pid_file(manager):
    assert manager.is_running() is False


def test_is_not_running_when_pid_file_stale(manager):
    manager.pid_file.write_text("99999999")
    assert manager.is_running() is False
    assert not manager.pid_file.exists()  # stale file cleaned up


def test_is_running_when_pid_alive(manager):
    manager.pid_file.write_text(str(os.getpid()))
    assert manager.is_running() is True


def test_get_status_not_running(manager):
    assert manager.get_status() == {"running": False}


def test_get_status_running(manager):
    manager.pid_file.write_text(str(os.getpid()))
    status = manager.get_status()
    assert status["running"] is True
    assert status["pid"] == os.getpid()


def test_stop_returns_false_when_not_running(manager):
    assert manager.stop() is False


def test_start_writes_pid_file(manager):
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_popen.return_value = mock_proc
        manager.start()
    assert manager.pid_file.read_text() == "12345"
