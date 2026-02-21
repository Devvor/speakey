"""fn-key push-to-talk: hold fn to record, release to transcribe and paste."""

import signal
import sys
import tempfile
import threading
import time
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
import Quartz

from ..config import Config
from ..model import ModelWrapper

_FN_KEYCODE = 63
_FN_FLAG = 0x00800000       # kCGEventFlagMaskSecondaryFn
_HOLD_THRESHOLD = 0.5       # seconds of hold before recording activates
_SAMPLE_RATE = 16_000


class FnPTTApp:
    def __init__(self):
        print("Loading model...", flush=True)
        self.model = ModelWrapper(Config())
        print("Ready. Hold fn to record.", flush=True)

        self._press_time: float | None = None
        self._recording = False
        self._buffer: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def run(self) -> None:
        signal.signal(signal.SIGTERM, lambda *_: self._shutdown())
        signal.signal(signal.SIGINT, lambda *_: self._shutdown())

        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged),
            self._on_event,
            None,
        )
        if not tap:
            print(
                "ERROR: Could not create event tap.\n"
                "Grant Input Monitoring: System Settings → Privacy & Security → Input Monitoring",
                file=sys.stderr,
            )
            sys.exit(1)

        source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        loop = Quartz.CFRunLoopGetCurrent()
        Quartz.CFRunLoopAddSource(loop, source, Quartz.kCFRunLoopDefaultMode)
        Quartz.CGEventTapEnable(tap, True)
        Quartz.CFRunLoopRun()

    # ── event tap ─────────────────────────────────────────────────────────────

    def _on_event(self, proxy, event_type, event, refcon):
        if Quartz.CGEventGetIntegerValueField(
            event, Quartz.kCGKeyboardEventKeycode
        ) != _FN_KEYCODE:
            return event
        if Quartz.CGEventGetFlags(event) & _FN_FLAG:
            self._on_press()
        else:
            self._on_release()
        return event

    def _on_press(self) -> None:
        with self._lock:
            if self._press_time is None:
                self._press_time = time.monotonic()
                threading.Timer(_HOLD_THRESHOLD, self._check_threshold).start()

    def _check_threshold(self) -> None:
        with self._lock:
            if self._press_time is not None and not self._recording:
                self._recording = True
                self._buffer = []
                self._stream = sd.InputStream(
                    samplerate=_SAMPLE_RATE,
                    channels=1,
                    dtype=np.float32,
                    blocksize=1024,
                    callback=self._audio_cb,
                )
                self._stream.start()

    def _on_release(self) -> None:
        with self._lock:
            self._press_time = None
            if self._recording:
                self._recording = False
                stream, buf = self._stream, self._buffer
                self._stream, self._buffer = None, []
                threading.Thread(
                    target=_transcribe_and_paste,
                    args=(self.model, stream, buf),
                    daemon=True,
                ).start()

    # ── audio callback ─────────────────────────────────────────────────────────

    def _audio_cb(self, indata, frames, t, status) -> None:
        if self._recording:
            self._buffer.append(indata.copy())

    def _shutdown(self) -> None:
        Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())


# ── free functions (no self needed, easier to test in isolation) ───────────────

def _transcribe_and_paste(model: ModelWrapper, stream: sd.InputStream, buf: list) -> None:
    """Stop stream, transcribe buffered audio, paste result."""
    stream.stop()
    stream.close()

    if not buf:
        return

    audio = np.concatenate(buf)
    audio_i16 = (audio * 32767).astype(np.int16)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = Path(f.name)

    with wave.open(str(tmp), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(audio_i16.tobytes())

    try:
        result = model.transcribe(tmp, timestamps=False)
        text = result.get("text", "").strip()
        if text:
            _paste(text)
    finally:
        tmp.unlink(missing_ok=True)


def _paste(text: str) -> None:
    """Copy text to clipboard then simulate Cmd+V into the active field."""
    import subprocess
    subprocess.run(["pbcopy"], input=text.encode(), check=True)

    src = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateHIDSystemState)
    for down in (True, False):
        e = Quartz.CGEventCreateKeyboardEvent(src, 9, down)  # 9 = kVK_ANSI_V
        Quartz.CGEventSetFlags(e, Quartz.kCGEventFlagMaskCommand)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)
