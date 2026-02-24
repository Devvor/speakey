"""Tests for daemon manager."""


from src.daemon.manager import DaemonManager


def test_daemon_manager_initialization(tmp_path):
    """Test daemon manager initialization."""
    manager = DaemonManager(runtime_dir=tmp_path)

    assert manager.runtime_dir == tmp_path
    assert manager.pid_file == tmp_path / "daemon.pid"
    assert manager.socket_path == tmp_path / "daemon.sock"
    assert tmp_path.exists()


def test_daemon_manager_is_running_false(tmp_path):
    """Test daemon manager reports not running when no PID file."""
    manager = DaemonManager(runtime_dir=tmp_path)

    assert manager.is_running() is False
    assert manager.get_pid() is None


def test_daemon_manager_is_running_stale_pid(tmp_path):
    """Test daemon manager handles stale PID file."""
    manager = DaemonManager(runtime_dir=tmp_path)

    # Write stale PID (process that doesn't exist)
    with open(manager.pid_file, "w") as f:
        f.write("999999")

    assert manager.is_running() is False
    assert not manager.pid_file.exists()


def test_daemon_manager_get_status(tmp_path):
    """Test getting daemon status."""
    import os

    manager = DaemonManager(runtime_dir=tmp_path)

    # Not running
    status = manager.get_status()
    assert status["running"] is False

    # Simulate running (use current process PID)
    current_pid = os.getpid()
    with open(manager.pid_file, "w") as f:
        f.write(str(current_pid))

    status = manager.get_status()
    assert status["running"] is True
    assert status["pid"] == current_pid
    assert "socket" in status
    assert "log" in status
