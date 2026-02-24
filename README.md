# Parakeet STT

Local speech-to-text for Mac — hold **fn**, speak, release, and your words appear wherever your cursor is. Runs entirely on-device using the Apple Neural Engine. No internet required, no subscriptions.

---

## For Users — Install the App

### Download & Install

1. Download the latest `ParakeetPTT.dmg` from the [Releases](../../releases) page
2. Open the DMG and drag **ParakeetPTT** into your Applications folder
3. Launch the app — a microphone icon appears in your menu bar

> **Gatekeeper warning:** The app is not yet notarized. If macOS blocks it, right-click (or Control-click) the app in Applications and choose **Open**, then click **Open** in the dialog. You only need to do this once.

### Grant Permissions (one-time)

The app needs three permissions. macOS will prompt for most of them automatically on first use, but you can also grant them manually:

**System Settings → Privacy & Security**

| Permission | Why it's needed |
|---|---|
| **Input Monitoring** | Detect when you hold the fn key |
| **Microphone** | Record your voice |
| **Accessibility** | Paste transcribed text into any app |

After granting permissions, restart the app.

### How to Use

1. Click into any text field (email, Slack, Notes, terminal — anything)
2. Hold **fn** for at least half a second and speak
3. Release **fn**
4. Your words appear in the text field within 1–2 seconds

The model loads once when you start the app (~10–30 seconds). After that, each dictation is near-instant.

### Menu Bar

Click the microphone icon in the menu bar to:
- See the current status (loading / ready / recording)
- Quit the app

### Troubleshooting

**Nothing happens when I hold fn**
→ Check that **Input Monitoring** is granted in System Settings → Privacy & Security → Input Monitoring. The app must be listed there.

**Audio records but text doesn't appear**
→ Check that **Accessibility** is granted in System Settings → Privacy & Security → Accessibility.

**No audio is captured**
→ Check that **Microphone** is granted in System Settings → Privacy & Security → Microphone.

**macOS says the app is damaged or can't be opened**
→ Right-click the app → Open → Open. If that doesn't work, run: `xattr -dr com.apple.quarantine /Applications/ParakeetPTT.app`

**The app is slow on first dictation**
→ The model is still loading. Wait for the menu bar icon to show "Ready" before dictating.

---

## For Developers

The repo contains both the native Swift menu-bar app (`swift/`) and a Python CLI / daemon (`src/`) that can be used independently.

### Project Structure

```
parakeet-stt/
├── src/                    # Python CLI and daemon
│   ├── backends/           # Backend implementations (NeMo, MLX)
│   ├── daemon/             # Background recording daemon (Unix socket IPC)
│   ├── fn_ptt/             # Python fn-key push-to-talk
│   ├── cli.py              # Click-based CLI
│   ├── config.py           # Configuration management
│   ├── model.py            # Model wrapper
│   └── output.py           # Output formatting
├── swift/                  # Native macOS menu-bar app (ParakeetPTT)
│   └── Sources/ParakeetPTT/
│       ├── AppDelegate.swift
│       ├── AudioRecorder.swift
│       ├── FnKeyMonitor.swift
│       ├── MenuBarView.swift
│       ├── TranscriptionService.swift
│       └── PasteService.swift
├── scripts/
│   ├── build-swift.sh      # Build the Swift app (debug or release)
│   └── package-dmg.sh      # Package into a distributable DMG
└── tests/                  # Python test suite
```

### Quick Start

```bash
source venv/bin/activate

# Build Swift app
./scripts/build-swift.sh          # debug
./scripts/build-swift.sh release  # optimised

# Package as DMG
./scripts/package-dmg.sh

# Run Python CLI
parakeet-stt transcribe audio.wav
parakeet-stt fn-ptt start
```

### Python Installation

```bash
git clone <repository-url>
cd parakeet-stt

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Apple Silicon — also install MLX dependencies
pip install -r requirements-mlx.txt
```

### Python CLI Usage

```bash
# Transcribe a file
parakeet-stt transcribe audio.wav
parakeet-stt transcribe audio.wav --output-dir results/
parakeet-stt transcribe audio.wav --no-timestamps
parakeet-stt transcribe audio.wav --device cpu

# fn-key push-to-talk (Python daemon)
parakeet-stt fn-ptt start
parakeet-stt fn-ptt status
parakeet-stt fn-ptt stop

# Background recording daemon
parakeet-stt daemon start
parakeet-stt daemon status
parakeet-stt daemon stop
parakeet-stt record start
parakeet-stt record stop
```

### Backend Selection

The Python CLI automatically picks the best available backend:

| Platform | Backend | Hardware | Performance |
|---|---|---|---|
| Mac (Apple Silicon) | MLX | Apple Neural Engine | 10x faster |
| Mac (Intel) | NeMo | CPU | Baseline |
| Linux/Windows (NVIDIA) | NeMo | CUDA | 3–5x faster |
| Other | NeMo | CPU | Baseline |

### Building the Swift App

```bash
# Debug build
./scripts/build-swift.sh

# Release build
./scripts/build-swift.sh release

# Ad-hoc signed DMG (local use)
./scripts/package-dmg.sh

# Developer ID signed DMG (distribution-ready)
CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)" ./scripts/package-dmg.sh
```

The build script prefers the swift.org toolchain (`swift-6.2.3-RELEASE`) over Xcode Command Line Tools to avoid a known `PackageDescription` ABI mismatch.

### Testing

```bash
source venv/bin/activate

pip install pytest pytest-cov pytest-mock

pytest                        # all tests
pytest -m "not slow"          # skip integration tests
pytest --cov=src              # with coverage
```

### Code Quality

```bash
# Format
black --line-length 100 src/ tests/

# Lint
ruff check --line-length 100 src/ tests/

# Pre-commit hooks (one-time setup)
pip install pre-commit
pre-commit install
```

### CI Pipeline

GitHub Actions runs on every push and PR to `main`:

| Job | What it does |
|---|---|
| `python-lint` | Black + Ruff |
| `python-test` | Unit tests (skips slow/integration) |
| `swift-build` | Swift debug build |
| `dependency-audit` | `pip-audit` on requirements.txt |

---

## Model

- **Model:** [nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Parameters:** 600 million
- **Architecture:** FastConformer-TDT
- **Word Error Rate:** 6.05% average
- **License:** CC-BY-4.0

## License

This project follows the model's CC-BY-4.0 license.
