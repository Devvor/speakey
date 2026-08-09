"""CLI application for Parakeet STT."""

import sys
from pathlib import Path

import click
from colorama import Fore, Style, init

from .config import Config
from .model import ModelWrapper
from .output import OutputHandler

# Initialize colorama for cross-platform colored output
init(autoreset=True)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Parakeet STT - Minimal speech-to-text CLI."""


@main.command()
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default="output",
    help="Output directory for transcription files",
)
@click.option(
    "--no-timestamps",
    is_flag=True,
    help="Disable timestamp output",
)
@click.option(
    "--device",
    type=click.Choice(["auto", "mps", "cuda", "cpu"]),
    default="auto",
    help="Device to use for inference",
)
def transcribe(
    audio_file: Path,
    output_dir: Path,
    no_timestamps: bool,
    device: str,
):
    """Transcribe audio file to text."""
    # Validate input
    if not audio_file.exists():
        click.echo(f"{Fore.RED}Error: Audio file does not exist: {audio_file}")
        sys.exit(1)

    # Create configuration
    config = Config(
        output_dir=output_dir,
        include_timestamps=not no_timestamps,
    )

    if device != "auto":
        config.device = device

    # Initialize components
    click.echo(f"{Fore.CYAN}Loading model...")
    try:
        model = ModelWrapper(config)
    except Exception as e:
        click.echo(f"{Fore.RED}Error loading model: {e}")
        sys.exit(1)

    # Transcribe
    click.echo(f"{Fore.CYAN}Transcribing: {audio_file.name}")
    try:
        transcription = model.transcribe(
            audio_file,
            timestamps=config.include_timestamps,
        )
    except Exception as e:
        click.echo(f"{Fore.RED}Error during transcription: {e}")
        sys.exit(1)

    # Save output
    output_handler = OutputHandler()
    output_path = output_handler.generate_output_filename(audio_file, config.output_dir)

    try:
        output_handler.save_transcription(
            transcription,
            output_path,
            include_timestamps=config.include_timestamps,
        )
    except Exception as e:
        click.echo(f"{Fore.RED}Error saving output: {e}")
        sys.exit(1)

    # Success message
    click.echo(f"{Fore.GREEN}✓ Transcription complete!")
    click.echo(f"{Fore.CYAN}Output saved to: {output_path}")
    click.echo(f"\n{Style.BRIGHT}Transcription:{Style.RESET_ALL}")
    click.echo(transcription["text"])


@main.group()
def daemon():
    """Manage background daemon service."""


@daemon.command("start")
def daemon_start():
    """Start the background daemon."""
    from .daemon.manager import DaemonManager

    manager = DaemonManager()

    if manager.is_running():
        click.echo(f"{Fore.YELLOW}Daemon is already running (PID: {manager.get_pid()})")
        sys.exit(0)

    if manager.start():
        click.echo(f"{Fore.GREEN}✓ Daemon started")
        click.echo(f"{Fore.CYAN}Socket: {manager.socket_path}")
        click.echo(f"{Fore.CYAN}Log: {manager.log_file}")
        click.echo(f"\n{Fore.CYAN}Control recording with:")
        click.echo("  parakeet-stt record")
    else:
        click.echo(f"{Fore.RED}Failed to start daemon")
        sys.exit(1)


@daemon.command("stop")
def daemon_stop():
    """Stop the background daemon."""
    from .daemon.manager import DaemonManager

    manager = DaemonManager()

    if not manager.is_running():
        click.echo(f"{Fore.YELLOW}Daemon is not running")
        sys.exit(0)

    if manager.stop():
        click.echo(f"{Fore.GREEN}✓ Daemon stopped")
    else:
        click.echo(f"{Fore.RED}Failed to stop daemon")
        sys.exit(1)


@daemon.command("status")
def daemon_status():
    """Check daemon status."""
    from .daemon.manager import DaemonManager

    manager = DaemonManager()
    status = manager.get_status()

    if status["running"]:
        click.echo(f"{Fore.GREEN}✓ Daemon is running")
        click.echo(f"{Fore.CYAN}PID: {status['pid']}")
        click.echo(f"{Fore.CYAN}Socket: {status['socket']}")
        click.echo(f"{Fore.CYAN}Log: {status['log']}")
    else:
        click.echo(f"{Fore.YELLOW}Daemon is not running")


@main.group("fn-ptt")
def fn_ptt():
    """fn-key push-to-talk: hold fn to record, release to paste."""


@fn_ptt.command("start")
def fn_ptt_start():
    """Start fn-ptt in the background."""
    from .fn_ptt.manager import FnPttManager

    manager = FnPttManager()
    if manager.is_running():
        click.echo(f"{Fore.YELLOW}fn-ptt is already running (PID: {manager.get_status()['pid']})")
        return
    if manager.start():
        click.echo(f"{Fore.GREEN}✓ fn-ptt started")
        click.echo(f"{Fore.CYAN}Hold fn for 0.5s to record. Release to transcribe and paste.")
    else:
        click.echo(f"{Fore.RED}Failed to start fn-ptt")
        sys.exit(1)


@fn_ptt.command("stop")
def fn_ptt_stop():
    """Stop fn-ptt."""
    from .fn_ptt.manager import FnPttManager

    manager = FnPttManager()
    if not manager.is_running():
        click.echo(f"{Fore.YELLOW}fn-ptt is not running")
        return
    if manager.stop():
        click.echo(f"{Fore.GREEN}✓ fn-ptt stopped")
    else:
        click.echo(f"{Fore.RED}Failed to stop fn-ptt")
        sys.exit(1)


@fn_ptt.command("status")
def fn_ptt_status():
    """Check fn-ptt status."""
    from .fn_ptt.manager import FnPttManager

    status = FnPttManager().get_status()
    if status["running"]:
        click.echo(f"{Fore.GREEN}✓ fn-ptt is running (PID: {status['pid']})")
    else:
        click.echo(f"{Fore.YELLOW}fn-ptt is not running")


@main.command()
@click.argument("action", type=click.Choice(["start", "stop"]), required=False)
def record(action: str):
    """Control recording (toggle, start, or stop).

    Examples:
        parakeet-stt record         # Toggle recording on/off
        parakeet-stt record start   # Start recording
        parakeet-stt record stop    # Stop recording
    """
    from .daemon.ipc import IPCClient
    from .daemon.manager import DaemonManager

    manager = DaemonManager()

    # Check if daemon is running
    if not manager.is_running():
        click.echo(f"{Fore.RED}Error: Daemon is not running")
        click.echo(f"{Fore.CYAN}Start daemon with: parakeet-stt daemon start")
        sys.exit(1)

    # Send command to daemon
    client = IPCClient(manager.socket_path)

    try:
        if action == "start":
            response = client.send_command("record_start")
        elif action == "stop":
            click.echo(
                f"{Fore.CYAN}Stopping recording and transcribing (this may take a moment for first use)..."
            )
            response = client.send_command("record_stop")
        else:
            # Toggle mode
            response = client.send_command("record_toggle")

        if response["status"] == "ok":
            click.echo(f"{Fore.GREEN}✓ {response['message']}")
            if "text" in response:
                click.echo(f"\n{Style.BRIGHT}Transcription:{Style.RESET_ALL}")
                click.echo(response["text"])
        else:
            click.echo(f"{Fore.RED}Error: {response.get('message', 'Unknown error')}")
            sys.exit(1)

    except ConnectionError as e:
        click.echo(f"{Fore.RED}Error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
