"""CLI application for Parakeet STT."""

import sys
from pathlib import Path
import click
from colorama import init, Fore, Style

from .config import Config
from .model import ModelWrapper
from .output import OutputHandler

# Initialize colorama for cross-platform colored output
init(autoreset=True)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Parakeet STT - Minimal speech-to-text CLI."""
    pass


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


if __name__ == "__main__":
    main()
