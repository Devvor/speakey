"""Real-time audio recorder for the optional Python daemon."""

from __future__ import annotations

import wave
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from ..config import Config

if TYPE_CHECKING:
    import sounddevice as sd


class AudioRecorder:
    """Records audio from microphone in real-time."""

    def __init__(self, config: Config):
        self.config = config
        self.is_recording = False
        self.audio_buffer: list[np.ndarray] = []
        self.stream: sd.InputStream | None = None

    def start(self) -> None:
        """Start recording audio from microphone."""
        import sounddevice as sd

        if self.is_recording:
            return

        self.audio_buffer = []
        self.is_recording = True

        self.stream = sd.InputStream(
            samplerate=self.config.ptt.sample_rate,
            channels=self.config.ptt.channels,
            dtype=np.float32,
            blocksize=self.config.ptt.chunk_size,
            callback=self._audio_callback,
        )
        self.stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return audio data."""
        if not self.is_recording:
            return np.array([])

        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if self.audio_buffer:
            return np.concatenate(self.audio_buffer, axis=0)
        return np.array([])

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")

        if self.is_recording:
            self.audio_buffer.append(indata.copy())

    def save_audio(self, output_path: Path) -> None:
        """Save recorded audio to WAV file."""
        if not self.audio_buffer:
            return

        audio_data = np.concatenate(self.audio_buffer, axis=0)
        audio_int16 = (audio_data * 32767).astype(np.int16)

        with wave.open(str(output_path), "w") as wf:
            wf.setnchannels(self.config.ptt.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.config.ptt.sample_rate)
            wf.writeframes(audio_int16.tobytes())

    def get_duration(self) -> float:
        """Get duration of recorded audio in seconds."""
        if not self.audio_buffer:
            return 0.0

        total_frames = sum(len(chunk) for chunk in self.audio_buffer)
        return total_frames / self.config.ptt.sample_rate
