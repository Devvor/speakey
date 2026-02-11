"""Integration tests with real model (slow)."""

import pytest
from pathlib import Path


@pytest.mark.slow
@pytest.mark.skipif(
    not Path("tests/fixtures/sample_audio.wav").exists(),
    reason="Sample audio file not available",
)
def test_full_transcription_pipeline():
    """Test complete transcription pipeline with real audio."""
    from src.config import Config
    from src.model import ModelWrapper
    from src.output import OutputHandler

    # Setup
    audio_file = Path("tests/fixtures/sample_audio.wav")
    output_dir = Path("output/test")
    config = Config(output_dir=output_dir, device="cpu")

    # Load model
    model = ModelWrapper(config)

    # Transcribe
    transcription = model.transcribe(audio_file, timestamps=True)

    # Validate results
    assert "text" in transcription
    assert len(transcription["text"]) > 0
    assert "timestamps" in transcription

    # Save output
    handler = OutputHandler()
    output_path = handler.generate_output_filename(audio_file, output_dir)
    handler.save_transcription(transcription, output_path, include_timestamps=True)

    # Verify file
    assert output_path.exists()
    content = output_path.read_text()
    assert transcription["text"] in content
