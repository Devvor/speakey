# CoreML/ANE Backend via FluidAudio Swift Bridge

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Add a CoreML backend that runs Parakeet TDT on Apple Neural Engine (~110x RTF) by bridging to [FluidAudio](https://github.com/FluidInference/FluidAudio) (v0.12.1) via a thin Swift CLI binary called from Python subprocess.

**Architecture:** A ~60-line Swift executable imports FluidAudio, transcribes an audio file, and outputs JSON to stdout. A new `CoreMLBackend` in Python calls this binary via `subprocess.run`, parses the JSON, and normalizes it to the project's standard `{"text": ..., "timestamps": {...}}` dict. The `BackendFactory` gains CoreML as highest-priority on Apple Silicon, with graceful fallback to MLX → NeMo.

**Tech Stack:** [FluidAudio](https://github.com/FluidInference/FluidAudio) v0.12.1 (Swift Package, Apache 2.0), CoreML (Apple framework), Swift 5.10+, macOS 14+.

---

## Permissions Required (macOS)

Before the CoreML backend works, the system needs:
- **macOS 14+** (Sonoma or later)
- **Xcode Command Line Tools** — `xcode-select --install`
- **Swift 5.10+** — ships with Xcode 15.3+

---

### Task 1: Swift package manifest

**Files:**
- Create: `swift/Package.swift`

**Step 1: Create the Swift package directory**

```bash
mkdir -p swift/Sources/ParakeetCoreML
```

**Step 2: Write the Package.swift**

```swift
// swift/Package.swift
// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "ParakeetCoreML",
    platforms: [.macOS(.v14)],
    dependencies: [
        .package(
            url: "https://github.com/FluidInference/FluidAudio.git",
            from: "0.12.1"
        ),
    ],
    targets: [
        .executableTarget(
            name: "parakeet-coreml",
            dependencies: [
                .product(name: "FluidAudio", package: "FluidAudio"),
            ],
            path: "Sources/ParakeetCoreML"
        ),
    ]
)
```

**Step 3: Resolve dependencies (does NOT build yet — no source)**

```bash
cd swift && swift package resolve
```

Expected: Dependencies resolved successfully. `Package.resolved` created.

**Step 4: Commit**

```bash
git add swift/Package.swift
git commit -m "chore: add Swift package manifest for CoreML bridge"
```

---

### Task 2: Swift CLI binary

**Files:**
- Create: `swift/Sources/ParakeetCoreML/main.swift`

**IMPORTANT:** The exact `ASRResult` property names for token timings are not fully documented by FluidAudio. The documented properties are `result.text` and `result.confidence`. Token timing properties (likely `result.tokens` or `result.tokenTimings` with `.start`/`.end`/`.text` or `.startTime`/`.endTime`/`.token`) need to be discovered at build time.

**Step 1: Write the Swift binary**

Write a first version that outputs text + confidence. Token timings will be added in Step 3 after inspecting the actual types.

```swift
// swift/Sources/ParakeetCoreML/main.swift
import Foundation
import FluidAudio

@main
struct ParakeetCoreML {
    static func main() async {
        let args = CommandLine.arguments
        guard args.count >= 2 else {
            printError("Usage: parakeet-coreml <audio-file> [--no-timestamps]")
            exit(1)
        }

        let audioPath = args[1]
        let includeTimestamps = !args.contains("--no-timestamps")

        guard FileManager.default.fileExists(atPath: audioPath) else {
            printError("File not found: \(audioPath)")
            exit(1)
        }

        do {
            let models = try await AsrModels.downloadAndLoad(version: .v3)
            let asr = AsrManager(config: .default)
            try await asr.initialize(models: models)

            let url = URL(fileURLWithPath: audioPath)
            let result = try await asr.transcribe(url, source: .system)

            // Start with text + confidence
            var output: [String: Any] = [
                "text": result.text,
                "confidence": result.confidence,
            ]

            // TODO: Add token timings after inspecting ASRResult type
            // if includeTimestamps { ... }

            let jsonData = try JSONSerialization.data(
                withJSONObject: output, options: [.sortedKeys]
            )
            if let jsonString = String(data: jsonData, encoding: .utf8) {
                print(jsonString)
            }
        } catch {
            printError("Transcription failed: \(error.localizedDescription)")
            exit(1)
        }
    }

    static func printError(_ message: String) {
        let json: [String: Any] = ["error": message]
        if let data = try? JSONSerialization.data(withJSONObject: json),
           let str = String(data: data, encoding: .utf8) {
            FileHandle.standardError.write(Data(str.utf8))
            FileHandle.standardError.write(Data("\n".utf8))
        }
    }
}
```

**Step 2: Build (release)**

```bash
cd swift && swift build -c release 2>&1
```

Expected: Build succeeds. Binary at `swift/.build/release/parakeet-coreml`.

**Step 3: Inspect ASRResult type and add token timings**

Once the build succeeds, open the project in Xcode or use `swift build` error messages to discover the actual token timing properties on `ASRResult`:

```bash
cd swift
# Temporarily add a line that tries to access result.tokens or result.tokenTimings
# The compiler error will reveal the actual property names
swift build 2>&1 | grep -i "token\|timing"
```

Then update `main.swift` to include the actual token timing output in the JSON. The expected structure is:

```json
{
  "text": "Hello world.",
  "confidence": 0.95,
  "tokenTimings": [
    {"word": "Hello", "start": 0.0, "end": 0.45},
    {"word": "world.", "start": 0.46, "end": 0.89}
  ]
}
```

Adjust the JSON key names (`word`/`start`/`end`) to match whatever FluidAudio actually provides.

**Step 4: Test with real audio**

```bash
swift/.build/release/parakeet-coreml 2086-149220-0033.wav
```

Expected: First run downloads ~2.5GB model. Then outputs JSON with transcription to stdout.

```bash
swift/.build/release/parakeet-coreml 2086-149220-0033.wav --no-timestamps
```

Expected: JSON with text only (no tokenTimings key).

**Step 5: Rebuild release**

```bash
cd swift && swift build -c release
```

**Step 6: Commit**

```bash
git add swift/Sources/ParakeetCoreML/main.swift
git commit -m "feat: add CoreML Swift bridge binary (audio → JSON via FluidAudio)"
```

---

### Task 3: Build script + gitignore

**Files:**
- Create: `scripts/build-swift.sh`
- Modify: `.gitignore`

**Step 1: Write the build script**

```bash
#!/usr/bin/env bash
# scripts/build-swift.sh — Build the parakeet-coreml Swift binary
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SWIFT_DIR="$(dirname "$SCRIPT_DIR")/swift"

echo "Building parakeet-coreml..."

# Check prerequisites
if ! command -v swift &> /dev/null; then
    echo "Error: Swift not found. Install Xcode Command Line Tools:"
    echo "  xcode-select --install"
    exit 1
fi

MACOS_VERSION=$(sw_vers -productVersion | cut -d. -f1)
if [ "$MACOS_VERSION" -lt 14 ]; then
    echo "Error: macOS 14+ required (you have $(sw_vers -productVersion))"
    exit 1
fi

cd "$SWIFT_DIR"
swift build -c release 2>&1

BINARY="$SWIFT_DIR/.build/release/parakeet-coreml"
if [ -f "$BINARY" ]; then
    echo ""
    echo "Build successful: $BINARY"
    echo "First run downloads the CoreML model (~2.5GB)."
else
    echo "Error: Build completed but binary not found"
    exit 1
fi
```

**Step 2: Make it executable**

```bash
chmod +x scripts/build-swift.sh
```

**Step 3: Add Swift build artifacts to .gitignore**

Add these lines to `.gitignore`:

```
# Swift build
swift/.build/
swift/Package.resolved
```

**Step 4: Commit**

```bash
git add scripts/build-swift.sh .gitignore
git commit -m "chore: add Swift build script and gitignore for swift artifacts"
```

---

### Task 4: Add `backend` field to Config

**Files:**
- Modify: `src/config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py (append to existing file)

def test_config_has_backend_field():
    """Test Config has backend field defaulting to empty string."""
    from src.config import Config
    config = Config()
    assert config.backend == ""


def test_config_backend_can_be_set():
    """Test Config backend can be set to a specific value."""
    from src.config import Config
    config = Config(backend="coreml")
    assert config.backend == "coreml"
```

**Step 2: Run to confirm failure**

```bash
pytest tests/test_config.py::test_config_has_backend_field -v
```

Expected: `TypeError: Config.__init__() got an unexpected keyword argument 'backend'`

**Step 3: Add backend field to Config**

In `src/config.py`, add this field to the `Config` dataclass after the `enable_mps_fallback` field (line 57):

```python
    # Backend selection (empty = auto-detect)
    backend: str = ""
```

**Step 4: Run tests**

```bash
pytest tests/test_config.py -v
```

Expected: All tests PASS (including existing ones).

**Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add backend field to Config for explicit backend selection"
```

---

### Task 5: CoreML backend Python module

**Files:**
- Create: `src/backends/coreml_backend.py`
- Create: `tests/test_coreml_backend.py`

**Step 1: Write the failing tests**

```python
# tests/test_coreml_backend.py
"""Tests for CoreML backend."""

import json
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.backends.coreml_backend import (
    find_coreml_binary,
    is_coreml_available,
    CoreMLBackend,
)
from src.config import Config


# ── Binary discovery ──────────────────────────────────────────────────────────


def test_find_binary_via_env_var(tmp_path):
    """Test binary found via PARAKEET_COREML_PATH env var."""
    binary = tmp_path / "parakeet-coreml"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)

    with patch.dict(os.environ, {"PARAKEET_COREML_PATH": str(binary)}):
        assert find_coreml_binary() == binary


def test_find_binary_env_var_missing_file():
    """Test None when env var points to nonexistent file."""
    with patch.dict(os.environ, {"PARAKEET_COREML_PATH": "/nonexistent/path"}):
        with patch("src.backends.coreml_backend._DEFAULT_BINARY_PATHS", []):
            with patch("shutil.which", return_value=None):
                assert find_coreml_binary() is None


def test_find_binary_default_path(tmp_path):
    """Test binary found at default build path."""
    binary = tmp_path / "parakeet-coreml"
    binary.write_text("#!/bin/sh\n")

    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("PARAKEET_COREML_PATH", None)
        with patch(
            "src.backends.coreml_backend._DEFAULT_BINARY_PATHS", [binary]
        ):
            assert find_coreml_binary() == binary


def test_find_binary_system_path():
    """Test binary found on system PATH."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("PARAKEET_COREML_PATH", None)
        with patch(
            "src.backends.coreml_backend._DEFAULT_BINARY_PATHS", []
        ):
            with patch("shutil.which", return_value="/usr/local/bin/parakeet-coreml"):
                result = find_coreml_binary()
                assert result == Path("/usr/local/bin/parakeet-coreml")


def test_find_binary_not_found():
    """Test None when binary not found anywhere."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("PARAKEET_COREML_PATH", None)
        with patch(
            "src.backends.coreml_backend._DEFAULT_BINARY_PATHS", []
        ):
            with patch("shutil.which", return_value=None):
                assert find_coreml_binary() is None


# ── Availability check ────────────────────────────────────────────────────────


def test_is_available_not_darwin():
    """Test returns False on non-macOS."""
    with patch("platform.system", return_value="Linux"):
        assert is_coreml_available() is False


def test_is_available_old_macos():
    """Test returns False on macOS < 14."""
    with patch("platform.system", return_value="Darwin"):
        with patch("platform.mac_ver", return_value=("13.6.1", ("", "", ""), "")):
            assert is_coreml_available() is False


def test_is_available_no_binary():
    """Test returns False when binary not found."""
    with patch("platform.system", return_value="Darwin"):
        with patch("platform.mac_ver", return_value=("15.0", ("", "", ""), "")):
            with patch(
                "src.backends.coreml_backend.find_coreml_binary", return_value=None
            ):
                assert is_coreml_available() is False


def test_is_available_all_conditions_met(tmp_path):
    """Test returns True when macOS 14+ and binary exists."""
    binary = tmp_path / "parakeet-coreml"
    binary.write_text("#!/bin/sh\n")

    with patch("platform.system", return_value="Darwin"):
        with patch("platform.mac_ver", return_value=("15.0", ("", "", ""), "")):
            with patch(
                "src.backends.coreml_backend.find_coreml_binary", return_value=binary
            ):
                assert is_coreml_available() is True


# ── Backend init ──────────────────────────────────────────────────────────────


def test_init_raises_when_no_binary():
    """Test RuntimeError when binary not found."""
    with patch(
        "src.backends.coreml_backend.find_coreml_binary", return_value=None
    ):
        with pytest.raises(RuntimeError, match="not found"):
            CoreMLBackend(Config())


# ── Output normalization ──────────────────────────────────────────────────────


def test_normalize_output_text_only():
    """Test normalization with text only (no timestamps)."""
    backend = _make_backend()
    raw = {"text": "Hello world.", "confidence": 0.95}
    result = backend._normalize_output(raw, timestamps=False)
    assert result == {"text": "Hello world."}


def test_normalize_output_with_timestamps():
    """Test normalization converts tokenTimings to standard format."""
    backend = _make_backend()
    raw = {
        "text": "Hello world.",
        "confidence": 0.95,
        "tokenTimings": [
            {"word": "Hello", "start": 0.0, "end": 0.45},
            {"word": "world.", "start": 0.46, "end": 0.89},
        ],
    }
    result = backend._normalize_output(raw, timestamps=True)
    assert result["text"] == "Hello world."
    assert len(result["timestamps"]["word"]) == 2
    assert result["timestamps"]["word"][0]["word"] == "Hello"
    assert len(result["timestamps"]["segment"]) == 1
    assert result["timestamps"]["segment"][0]["segment"] == "Hello world."


def test_normalize_output_no_timings_key():
    """Test normalization when tokenTimings key is absent."""
    backend = _make_backend()
    raw = {"text": "Hello.", "confidence": 0.9}
    result = backend._normalize_output(raw, timestamps=True)
    assert result == {"text": "Hello."}


# ── Segment building ─────────────────────────────────────────────────────────


def test_build_segments_single_sentence():
    """Test building segments from words ending in period."""
    backend = _make_backend()
    words = [
        {"word": "Hello", "start": 0.0, "end": 0.4},
        {"word": "world.", "start": 0.5, "end": 0.9},
    ]
    segments = backend._build_segments(words)
    assert len(segments) == 1
    assert segments[0]["segment"] == "Hello world."
    assert segments[0]["start"] == 0.0
    assert segments[0]["end"] == 0.9


def test_build_segments_multiple_sentences():
    """Test building segments splits on punctuation."""
    backend = _make_backend()
    words = [
        {"word": "Hi.", "start": 0.0, "end": 0.3},
        {"word": "Bye!", "start": 0.5, "end": 0.8},
    ]
    segments = backend._build_segments(words)
    assert len(segments) == 2


def test_build_segments_no_punctuation():
    """Test words without sentence-ending punctuation form one segment."""
    backend = _make_backend()
    words = [
        {"word": "Hello", "start": 0.0, "end": 0.4},
        {"word": "world", "start": 0.5, "end": 0.9},
    ]
    segments = backend._build_segments(words)
    assert len(segments) == 1
    assert segments[0]["segment"] == "Hello world"


def test_build_segments_empty():
    """Test empty input returns empty list."""
    backend = _make_backend()
    assert backend._build_segments([]) == []


# ── Transcription (mocked subprocess) ────────────────────────────────────────


def test_transcribe_calls_subprocess(tmp_path):
    """Test transcribe calls Swift binary with correct args."""
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"RIFF" + b"\x00" * 40)

    backend = _make_backend()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({"text": "Hello.", "confidence": 0.9})

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        result = backend.transcribe(audio, timestamps=False)

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert str(audio) in call_args
    assert "--no-timestamps" in call_args
    assert result["text"] == "Hello."


def test_transcribe_subprocess_error(tmp_path):
    """Test RuntimeError when subprocess fails."""
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"RIFF" + b"\x00" * 40)

    backend = _make_backend()
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = json.dumps({"error": "Model failed"})

    with patch("subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="Model failed"):
            backend.transcribe(audio)


def test_transcribe_file_not_found():
    """Test FileNotFoundError for missing audio file."""
    backend = _make_backend()
    with pytest.raises(FileNotFoundError):
        backend.transcribe("/nonexistent/audio.wav")


def test_transcribe_timeout(tmp_path):
    """Test RuntimeError on subprocess timeout."""
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"RIFF" + b"\x00" * 40)

    backend = _make_backend()
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 300)):
        with pytest.raises(RuntimeError, match="timed out"):
            backend.transcribe(audio)


def test_transcribe_invalid_json(tmp_path):
    """Test RuntimeError on malformed JSON from subprocess."""
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"RIFF" + b"\x00" * 40)

    backend = _make_backend()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "not json"

    with patch("subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="parse"):
            backend.transcribe(audio)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_backend():
    """Create CoreMLBackend with mocked binary path."""
    with patch(
        "src.backends.coreml_backend.find_coreml_binary",
        return_value=Path("/usr/local/bin/parakeet-coreml"),
    ):
        return CoreMLBackend(Config())
```

**Step 2: Run to confirm failure**

```bash
pytest tests/test_coreml_backend.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.backends.coreml_backend'`

**Step 3: Write the CoreML backend**

```python
# src/backends/coreml_backend.py
"""CoreML backend for Apple Neural Engine via FluidAudio Swift bridge."""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Union

from .base import BaseBackend
from ..config import Config

_DEFAULT_BINARY_PATHS = [
    Path(__file__).parent.parent.parent / "swift" / ".build" / "release" / "parakeet-coreml",
    Path(__file__).parent.parent.parent / "swift" / ".build" / "debug" / "parakeet-coreml",
]


def find_coreml_binary() -> Optional[Path]:
    """Find the parakeet-coreml Swift binary.

    Checks in order:
    1. PARAKEET_COREML_PATH environment variable
    2. Default build paths (swift/.build/release and debug)
    3. System PATH
    """
    env_path = os.environ.get("PARAKEET_COREML_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists() and p.is_file():
            return p

    for path in _DEFAULT_BINARY_PATHS:
        if path.exists() and path.is_file():
            return path

    which = shutil.which("parakeet-coreml")
    if which:
        return Path(which)

    return None


def is_coreml_available() -> bool:
    """Check if CoreML backend can be used.

    Requires macOS 14+, and built parakeet-coreml binary.
    """
    import platform

    if platform.system() != "Darwin":
        return False

    mac_ver = platform.mac_ver()[0]
    if mac_ver:
        major = int(mac_ver.split(".")[0])
        if major < 14:
            return False

    return find_coreml_binary() is not None


class CoreMLBackend(BaseBackend):
    """CoreML backend using FluidAudio via Swift bridge.

    Calls a pre-built Swift CLI binary that runs the Parakeet TDT model
    on Apple Neural Engine. ~110x real-time on M4 Pro.
    """

    def __init__(self, config: Config):
        self.config = config
        self.binary_path = find_coreml_binary()
        if not self.binary_path:
            raise RuntimeError(
                "CoreML backend not available: parakeet-coreml binary not found.\n"
                "Build it with: scripts/build-swift.sh"
            )
        self.model = self.load_model()

    def load_model(self):
        """No-op — model lives in the Swift process. FluidAudio caches it."""
        return None

    def transcribe(self, audio_path: Union[str, Path], timestamps: bool = True) -> Dict:
        """Transcribe audio via CoreML/ANE Swift bridge."""
        audio_path = Path(audio_path).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        cmd = [str(self.binary_path), str(audio_path)]
        if not timestamps:
            cmd.append("--no-timestamps")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                try:
                    error_msg = json.loads(error_msg).get("error", error_msg)
                except json.JSONDecodeError:
                    pass
                raise RuntimeError(f"CoreML transcription failed: {error_msg}")

            raw = json.loads(result.stdout)
            return self._normalize_output(raw, timestamps)

        except subprocess.TimeoutExpired:
            raise RuntimeError("CoreML transcription timed out (>5 min)")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse CoreML output: {e}")

    def _normalize_output(self, raw: Dict, timestamps: bool) -> Dict:
        """Convert Swift JSON to standard backend format."""
        output = {"text": raw["text"]}

        if timestamps and "tokenTimings" in raw:
            word_timestamps = [
                {
                    "start": t.get("start", 0.0),
                    "end": t.get("end", 0.0),
                    "word": t.get("word", ""),
                }
                for t in raw["tokenTimings"]
            ]
            output["timestamps"] = {
                "word": word_timestamps,
                "segment": self._build_segments(word_timestamps),
            }

        return output

    def _build_segments(self, word_timestamps: list) -> list:
        """Group words into segments by sentence-ending punctuation."""
        if not word_timestamps:
            return []

        segments = []
        current_words = []
        current_start = word_timestamps[0]["start"]

        for wt in word_timestamps:
            current_words.append(wt["word"])
            word = wt["word"].strip()
            if word and word[-1] in ".?!":
                segments.append({
                    "start": current_start,
                    "end": wt["end"],
                    "segment": " ".join(current_words).strip(),
                })
                current_words = []
                current_start = wt["end"]

        if current_words:
            segments.append({
                "start": current_start,
                "end": word_timestamps[-1]["end"],
                "segment": " ".join(current_words).strip(),
            })

        return segments
```

**Step 4: Run tests**

```bash
pytest tests/test_coreml_backend.py -v
```

Expected: All tests PASS.

**Step 5: Commit**

```bash
git add src/backends/coreml_backend.py tests/test_coreml_backend.py
git commit -m "feat: add CoreML backend with FluidAudio Swift bridge"
```

---

### Task 6: Factory integration

**Files:**
- Modify: `src/backends/__init__.py`
- Modify: `src/backends/factory.py`
- Modify: `tests/test_backend_factory.py`

**Step 1: Write the failing tests**

Append to `tests/test_backend_factory.py`:

```python
def test_backend_factory_prefers_coreml_on_mac():
    """Test CoreML preferred over MLX on Apple Silicon."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.platform.system", return_value="Darwin"):
        with patch("src.backends.factory.platform.processor", return_value="arm"):
            with patch("src.backends.factory.COREML_AVAILABLE", True):
                with patch("src.backends.factory.MLX_AVAILABLE", True):
                    backend_class = BackendFactory.get_backend_class(config)
                    assert backend_class.__name__ == "CoreMLBackend"


def test_backend_factory_falls_back_to_mlx_when_no_coreml():
    """Test MLX used when CoreML unavailable on Apple Silicon."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.platform.system", return_value="Darwin"):
        with patch("src.backends.factory.platform.processor", return_value="arm"):
            with patch("src.backends.factory.COREML_AVAILABLE", False):
                with patch("src.backends.factory.MLX_AVAILABLE", True):
                    backend_class = BackendFactory.get_backend_class(config)
                    assert backend_class.__name__ == "MLXBackend"


def test_backend_factory_force_coreml():
    """Test explicit coreml backend selection."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config(backend="coreml")

    with patch("src.backends.factory.COREML_AVAILABLE", True):
        backend_class = BackendFactory.get_backend_class(config)
        assert backend_class.__name__ == "CoreMLBackend"


def test_backend_factory_force_coreml_unavailable():
    """Test error when coreml forced but unavailable."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config(backend="coreml")

    with patch("src.backends.factory.COREML_AVAILABLE", False):
        with pytest.raises(RuntimeError, match="not available"):
            BackendFactory.get_backend_class(config)
```

**Step 2: Run to confirm failure**

```bash
pytest tests/test_backend_factory.py -v
```

Expected: FAIL — `COREML_AVAILABLE` doesn't exist in factory module yet.

**Step 3: Update `src/backends/__init__.py`**

Add CoreML conditional import block after the MLX block (after line 24):

```python
# Conditionally import CoreML backend
try:
    from .coreml_backend import CoreMLBackend, is_coreml_available

    __all__.append("CoreMLBackend")
    COREML_AVAILABLE = is_coreml_available()
except (ImportError, RuntimeError):
    COREML_AVAILABLE = False
```

**Step 4: Update `src/backends/factory.py`**

Add CoreML availability check after the MLX block (after line 26):

```python
# Check CoreML availability
try:
    from .coreml_backend import CoreMLBackend, is_coreml_available

    COREML_AVAILABLE = is_coreml_available()
except Exception:
    COREML_AVAILABLE = False
    CoreMLBackend = None
```

Update `get_backend_class` — add `coreml` to the force-specific section (after the `nemo` elif, around line 54):

```python
            elif config.backend == "coreml":
                if COREML_AVAILABLE:
                    return CoreMLBackend
                raise RuntimeError("CoreML backend requested but not available")
```

Update the auto-select section (replace the existing Apple Silicon check around line 57):

```python
        # Auto-select based on platform
        if BackendFactory._is_apple_silicon():
            if COREML_AVAILABLE:
                return CoreMLBackend
            if MLX_AVAILABLE:
                return MLXBackend
```

Update the error message to mention CoreML (around line 65):

```python
        raise RuntimeError(
            "No backend available. Install one of:\n"
            "  CoreML: scripts/build-swift.sh\n"
            "  MLX: pip install -e .[mlx]\n"
            "  NeMo: pip install -e .[nemo]"
        )
```

**Step 5: Run all tests**

```bash
pytest tests/test_backend_factory.py -v
```

Expected: All tests PASS (old + new).

```bash
pytest -v
```

Expected: Full test suite PASS.

**Step 6: Commit**

```bash
git add src/backends/__init__.py src/backends/factory.py tests/test_backend_factory.py
git commit -m "feat: integrate CoreML backend into factory with highest priority on Apple Silicon"
```

---

### Task 7: CLI `--backend` option

**Files:**
- Modify: `src/cli.py`

**Step 1: Add `--backend` option to the `transcribe` command**

In `src/cli.py`, add this option to the `transcribe` command (after the `--device` option, around line 42):

```python
@click.option(
    "--backend",
    type=click.Choice(["auto", "coreml", "mlx", "nemo"]),
    default="auto",
    help="Backend for inference (auto, coreml, mlx, nemo)",
)
```

Update the `transcribe` function signature to accept `backend: str`:

```python
def transcribe(
    audio_file: Path,
    output_dir: Path,
    no_timestamps: bool,
    device: str,
    backend: str,
):
```

Add backend handling after the device handling (after the `if device != "auto":` block, around line 62):

```python
    if backend != "auto":
        config.backend = backend
```

**Step 2: Test manually**

```bash
parakeet-stt transcribe --help
```

Expected: Shows `--backend` option with choices `auto, coreml, mlx, nemo`.

**Step 3: Commit**

```bash
git add src/cli.py
git commit -m "feat: add --backend CLI option for explicit backend selection"
```

---

### Task 8: pyproject.toml + docs

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add `coreml` optional deps group**

In `pyproject.toml`, add after the `mlx` group (after line 31):

```toml
# CoreML backend for Apple Neural Engine (requires separate Swift build)
# No Python deps needed — uses a Swift binary bridge
coreml = []
```

**Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add coreml optional dependency group to pyproject.toml"
```

---

### Task 9: Manual integration test

**Prerequisites:**
- macOS 14+ with Apple Silicon
- Xcode Command Line Tools installed (`xcode-select --install`)
- Swift binary built (Task 2)

**Steps:**

```bash
source venv/bin/activate

# Build Swift binary if not already done
scripts/build-swift.sh

# Test direct Swift binary (first run downloads ~2.5GB model)
swift/.build/release/parakeet-coreml 2086-149220-0033.wav

# Test via CLI with explicit backend
parakeet-stt transcribe 2086-149220-0033.wav --backend coreml

# Test auto-detection (should pick CoreML if binary is built)
parakeet-stt transcribe 2086-149220-0033.wav

# Test fallback — temporarily rename binary
mv swift/.build/release/parakeet-coreml swift/.build/release/parakeet-coreml.bak
parakeet-stt transcribe 2086-149220-0033.wav  # should fall back to MLX or NeMo
mv swift/.build/release/parakeet-coreml.bak swift/.build/release/parakeet-coreml

# Run full test suite
pytest -v
```

**Step: Final commit if integration passes**

```bash
git commit --allow-empty -m "feat: CoreML/ANE backend complete via FluidAudio Swift bridge"
```

---

## File Summary

| Action | Path |
|--------|------|
| Create | `swift/Package.swift` |
| Create | `swift/Sources/ParakeetCoreML/main.swift` |
| Create | `scripts/build-swift.sh` |
| Create | `src/backends/coreml_backend.py` |
| Create | `tests/test_coreml_backend.py` |
| Modify | `src/config.py` (add `backend` field) |
| Modify | `src/backends/__init__.py` (add CoreML import) |
| Modify | `src/backends/factory.py` (add CoreML preference) |
| Modify | `src/cli.py` (add `--backend` option) |
| Modify | `tests/test_config.py` (add backend field tests) |
| Modify | `tests/test_backend_factory.py` (add CoreML factory tests) |
| Modify | `pyproject.toml` (add `[coreml]` group) |
| Modify | `.gitignore` (add `swift/.build/`) |

## Risk: FluidAudio ASRResult Token Timing API

The exact property names on `ASRResult` for token-level timestamps are underdocumented. Task 2 Step 3 explicitly handles this: build the Swift binary first, inspect the actual type, then wire up the JSON mapping. The Python-side `_normalize_output` method centralizes all field mapping in one place — easy to adjust once the actual JSON keys are known.
