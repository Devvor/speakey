"""Tests for output handler."""

import pytest
from pathlib import Path


def test_save_transcription_simple(tmp_path, sample_transcription):
    """Test saving simple transcription to file."""
    from src.output import OutputHandler

    output_file = tmp_path / "output.txt"
    handler = OutputHandler()

    handler.save_transcription(
        transcription={"text": sample_transcription["text"]},
        output_path=output_file,
        include_timestamps=False,
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert sample_transcription["text"] in content


def test_save_transcription_with_timestamps(tmp_path, sample_transcription):
    """Test saving transcription with timestamps."""
    from src.output import OutputHandler

    output_file = tmp_path / "output.txt"
    handler = OutputHandler()

    handler.save_transcription(
        transcription=sample_transcription,
        output_path=output_file,
        include_timestamps=True,
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert sample_transcription["text"] in content
    assert "Timestamps" in content or "0.0s" in content


def test_generate_output_filename():
    """Test automatic output filename generation."""
    from src.output import OutputHandler

    handler = OutputHandler()
    input_path = Path("audio/test_recording.wav")

    output_path = handler.generate_output_filename(input_path, output_dir=Path("output"))

    assert output_path.parent == Path("output")
    assert output_path.stem == "test_recording"
    assert output_path.suffix == ".txt"
