"""Real-time audio recorder for push-to-talk."""

import sounddevice as sd
import numpy as np
from pathlib import Path
from typing import Optional
import wave

from ..config import Config


class AudioRecorder:
    """Records audio from microphone in real-time."""

    def __init__(self, config: Config):
        """Initialize audio recorder.

        Args:
            config: Application configuration
        """
        self.config = config
        self.is_recording = False
        self.audio_buffer = []
        self.stream: Optional[sd.InputStream] = None

    def start(self) -> None:
        """Start recording audio from microphone."""
        if self.is_recording:
            return

        self.audio_buffer = []
        self.is_recording = True

        # Create audio stream
        self.stream = sd.InputStream(
            samplerate=self.config.ptt.sample_rate,
            channels=self.config.ptt.channels,
            dtype=np.float32,
            blocksize=self.config.ptt.chunk_size,
            callback=self._audio_callback,
        )
        self.stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return audio data.

        Returns:
            Audio data as numpy array
        """
        if not self.is_recording:
            return np.array([])

        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Concatenate all audio chunks
        if self.audio_buffer:
            audio_data = np.concatenate(self.audio_buffer, axis=0)
        else:
            audio_data = np.array([])

        return audio_data

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream.

        Args:
            indata: Input audio data
            frames: Number of frames
            time: Time info
            status: Status flags
        """
        if status:
            print(f"Audio callback status: {status}")

        if self.is_recording:
            self.audio_buffer.append(indata.copy())

    def save_audio(self, output_path: Path) -> None:
        """Save recorded audio to WAV file.

        Args:
            output_path: Path to save audio file
        """
        if not self.audio_buffer:
            return

        audio_data = np.concatenate(self.audio_buffer, axis=0)

        # Convert float32 to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Save as WAV
        with wave.open(str(output_path), 'w') as wf:
            wf.setnchannels(self.config.ptt.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.config.ptt.sample_rate)
            wf.writeframes(audio_int16.tobytes())

    def get_duration(self) -> float:
        """Get duration of recorded audio in seconds.

        Returns:
            Duration in seconds
        """
        if not self.audio_buffer:
            return 0.0

        total_frames = sum(len(chunk) for chunk in self.audio_buffer)
        return total_frames / self.config.ptt.sample_rate
