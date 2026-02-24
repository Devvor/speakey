"""Tests for CLI application."""

from unittest.mock import Mock, patch
from click.testing import CliRunner


def test_cli_help():
    """Test CLI help output."""
    from src.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Transcribe audio file" in result.output


def test_cli_transcribe_success(tmp_path):
    """Test successful transcription via CLI."""
    from src.cli import main

    audio_file = tmp_path / "test.wav"
    audio_file.touch()
    output_dir = tmp_path / "output"

    runner = CliRunner()

    with patch("src.cli.ModelWrapper") as mock_model:
        with patch("src.cli.OutputHandler"):
            mock_instance = Mock()
            mock_instance.transcribe.return_value = {
                "text": "test transcription",
                "timestamps": {"word": [], "segment": []},
            }
            mock_model.return_value = mock_instance

            result = runner.invoke(
                main,
                [
                    "transcribe",
                    str(audio_file),
                    "--output-dir",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0
            mock_instance.transcribe.assert_called_once()


def test_cli_transcribe_file_not_found():
    """Test CLI with non-existent file."""
    from src.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["transcribe", "nonexistent.wav"])

    assert result.exit_code != 0
    assert "does not exist" in result.output.lower()
