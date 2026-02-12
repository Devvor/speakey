"""Inter-process communication for daemon."""

import socket
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import threading


class IPCServer:
    """Unix socket server for daemon communication."""

    def __init__(self, socket_path: Path):
        """Initialize IPC server.

        Args:
            socket_path: Path to Unix socket file
        """
        self.socket_path = socket_path
        self.server: Optional[socket.socket] = None
        self.running = False
        self.on_message: Optional[callable] = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the IPC server."""
        # Remove existing socket file
        if self.socket_path.exists():
            self.socket_path.unlink()

        # Create Unix socket
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.socket_path))
        self.server.listen(5)
        self.running = True

        # Start listening in background thread
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop the IPC server."""
        self.running = False
        if self.server:
            self.server.close()
        if self.socket_path.exists():
            self.socket_path.unlink()

    def _listen(self) -> None:
        """Listen for incoming connections."""
        while self.running:
            try:
                self.server.settimeout(1.0)
                conn, _ = self.server.accept()
                threading.Thread(
                    target=self._handle_connection,
                    args=(conn,),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"IPC server error: {e}")
                break

    def _handle_connection(self, conn: socket.socket) -> None:
        """Handle incoming connection.

        Args:
            conn: Client connection
        """
        try:
            # Receive message
            data = conn.recv(4096)
            if data:
                message = json.loads(data.decode())

                # Process message
                response = {"status": "ok"}
                if self.on_message:
                    try:
                        response = self.on_message(message)
                    except Exception as e:
                        response = {"status": "error", "message": str(e)}

                # Send response
                conn.sendall(json.dumps(response).encode())
        except Exception as e:
            error_response = {"status": "error", "message": str(e)}
            conn.sendall(json.dumps(error_response).encode())
        finally:
            conn.close()


class IPCClient:
    """Unix socket client for daemon communication."""

    def __init__(self, socket_path: Path):
        """Initialize IPC client.

        Args:
            socket_path: Path to Unix socket file
        """
        self.socket_path = socket_path

    def send_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Send command to daemon.

        Args:
            command: Command name
            **kwargs: Additional command parameters

        Returns:
            Response from daemon

        Raises:
            ConnectionError: If daemon is not running
        """
        if not self.socket_path.exists():
            raise ConnectionError("Daemon is not running")

        # Create socket and connect
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(str(self.socket_path))

            # Set longer timeout for model loading (60 seconds)
            client.settimeout(60.0)

            # Send message
            message = {"command": command, **kwargs}
            client.sendall(json.dumps(message).encode())

            # Receive response (may take time for model loading)
            data = client.recv(8192)  # Increased buffer size
            if not data:
                raise ConnectionError("Daemon closed connection without response")
            return json.loads(data.decode())
        finally:
            client.close()
