"""Tests for IPC communication."""

import tempfile
from pathlib import Path

import pytest

from src.daemon.ipc import IPCClient, IPCServer


@pytest.fixture
def short_socket_path():
    """Create a short socket path to avoid AF_UNIX path length limit."""
    # Use /tmp which is much shorter than pytest's tmp_path
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="pst_") as tmpdir:
        yield Path(tmpdir) / "test.sock"


def test_ipc_server_initialization(short_socket_path):
    """Test IPC server initialization."""
    socket_path = short_socket_path
    server = IPCServer(socket_path)

    assert server.socket_path == socket_path
    assert server.running is False
    assert server.server is None


def test_ipc_server_start_stop(short_socket_path):
    """Test starting and stopping IPC server."""
    socket_path = short_socket_path
    server = IPCServer(socket_path)

    # Start server
    server.start()
    assert server.running is True
    assert socket_path.exists()

    # Stop server
    server.stop()
    assert server.running is False
    assert not socket_path.exists()


def test_ipc_client_server_communication(short_socket_path):
    """Test client-server communication."""
    socket_path = short_socket_path
    server = IPCServer(socket_path)

    # Setup message handler
    received_messages = []

    def handle_message(message):
        received_messages.append(message)
        return {"status": "ok", "echo": message}

    server.on_message = handle_message

    # Start server
    server.start()

    # Wait for server to be ready
    import time

    time.sleep(0.1)

    # Send a valid command (unknown commands are rejected by the server)
    client = IPCClient(socket_path)
    response = client.send_command("ping", data="hello")

    assert response["status"] == "ok"
    assert response["echo"]["command"] == "ping"
    assert response["echo"]["data"] == "hello"

    # Clean up
    server.stop()


def test_ipc_client_connection_error(tmp_path):
    """Test client connection error when daemon not running."""
    socket_path = tmp_path / "nonexistent.sock"
    client = IPCClient(socket_path)

    with pytest.raises(ConnectionError, match="Daemon is not running"):
        client.send_command("test")
