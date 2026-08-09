# Kuaishuo - Claude Development Guide

> **Project Context:** Local-first speech-to-text CLI application using NVIDIA's Parakeet TDT 0.6B v3 model, optimized for Apple Neural Engine via MLX framework.

---

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Install pre-commit hooks (one-time)
pip install pre-commit && pre-commit install

# Run tests (install test deps first if needed)
pip install pytest pytest-cov pytest-mock
pytest

# Transcribe audio
parakeet-stt transcribe audio.wav

# fn-key push-to-talk (Python daemon)
parakeet-stt fn-ptt start

# Build & run the native Swift menu-bar app (source-first; no public DMG)
./scripts/build-swift.sh          # debug
./swift/.build/debug/kuaishuo
./scripts/build-swift.sh release  # release
```

---

## Project Structure

```
kuaishuo/
├── src/                         # Python application package
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── model.py                 # Model wrapper with backend selection
│   ├── output.py                # Output formatting
│   ├── cli.py                   # Click-based CLI
│   ├── backends/                # Backend implementations
│   │   ├── base.py              # Abstract base backend
│   │   ├── nemo_backend.py      # NeMo/PyTorch backend
│   │   ├── mlx_backend.py       # MLX/ANE backend (Apple Silicon)
│   │   └── factory.py           # Automatic backend selection
│   ├── daemon/                  # Background recording daemon
│   │   ├── app.py               # Daemon application
│   │   ├── controller.py        # Recording controller
│   │   ├── ipc.py               # Unix socket IPC server/client (0o600)
│   │   ├── manager.py           # Process lifecycle (PID-based)
│   │   └── run_daemon.py        # Subprocess entry point
│   └── fn_ptt/                  # Python fn-key push-to-talk
│       ├── app.py               # Event tap, recording, transcription, paste
│       ├── manager.py           # Process lifecycle (PID-based)
│       └── run.py               # Subprocess entry point
│
├── swift/                       # Native macOS menu-bar app (Kuaishuo)
│   └── Sources/Kuaishuo/
│       ├── AppDelegate.swift        # App lifecycle + fn-key handling
│       ├── AudioRecorder.swift      # AVFoundation audio capture
│       ├── FnKeyMonitor.swift       # Global fn-key event tap
│       ├── MenuBarView.swift        # Menu bar UI
│       ├── TranscriptionService.swift  # CoreML inference
│       └── PasteService.swift       # Accessibility paste
│
├── scripts/
│   ├── build-swift.sh           # Build Swift app (debug/release)
│   └── package-dmg.sh           # Optional local .app/DMG only (not public releases)
│
├── tests/                       # Python test suite
│   ├── conftest.py              # Shared fixtures
│   ├── test_config.py
│   ├── test_model.py
│   ├── test_backends.py
│   ├── test_backend_factory.py
│   ├── test_mlx_backend.py
│   └── fixtures/
│       └── sample_audio.wav     # Test audio
│
├── docs/                        # Documentation
│   ├── knowledge/               # Model specs, development phases
│   ├── plans/                   # Implementation plans
│   └── research/                # MLX research notes
│
├── .github/workflows/ci.yml     # GitHub Actions CI pipeline
├── .pre-commit-config.yaml      # Pre-commit hooks (Black + Ruff)
├── requirements.txt             # Runtime Python dependencies
├── requirements-mlx.txt         # MLX dependencies (Apple Silicon)
├── pyproject.toml               # Project metadata and tool config
├── .python-version              # Python 3.10+
├── README.md
└── CLAUDE.md                    # This file
```

---

## Architecture

### Three-Phase Development

#### Phase 1: Basic NeMo Implementation ✅ **COMPLETE**
**Status:** ✅ Complete - All tests passing (86% coverage)
**Deliverable:** Python library for programmatic transcription

**Completed:**
- ✅ Task 1: Project structure and dependencies
- ✅ Task 2: Core module structure (config.py)
- ✅ Task 3: Model wrapper (model.py)
- ✅ All unit tests passing (7/7)
- ✅ Test coverage: 86%

**What Works:**
```python
from src.model import ModelWrapper
from src.config import Config

config = Config()
model = ModelWrapper(config)
result = model.transcribe("audio.wav", timestamps=True)
print(result["text"])
```

**Components:**
```python
# src/config.py - Configuration management
Config:
  - model_name: "nvidia/parakeet-tdt-0.6b-v3"
  - device: mps/cuda/cpu
  - output_dir: Path
  - include_timestamps: bool

# src/model.py - Model wrapper
ModelWrapper:
  - load_model() -> ASRModel
  - transcribe(audio_path, timestamps) -> Dict
```

#### Phase 2: CLI Interface ✅ **COMPLETE**
**Status:** ✅ Complete
**Deliverable:** End-user command-line tool + background daemon + fn-ptt

**Completed:**
- ✅ `src/output.py` - Output formatting
- ✅ `src/cli.py` - Click-based CLI
- ✅ `src/daemon/` - Background recording daemon with Unix socket IPC
- ✅ `src/fn_ptt/` - Python fn-key push-to-talk with transcription + paste
- ✅ Security hardening: runtime dir `0o700`, IPC socket `0o600`, no transcription text in logs

```bash
parakeet-stt transcribe audio.wav
parakeet-stt fn-ptt start
parakeet-stt daemon start
```

#### Phase 3: ANE Optimization 🚀 **IN PROGRESS**
**Deliverable:** Native macOS app using CoreML for on-device inference

**Completed:**
- ✅ Backend abstraction layer (`src/backends/`)
- ✅ MLX backend for Apple Silicon
- ✅ Swift macOS menu-bar app (Kuaishuo) using CoreML + parakeet-mlx
- ✅ Optional local DMG packaging script (not public distribution)
- ✅ GitHub Actions CI pipeline
- ✅ Pre-commit hooks
- ✅ Source-first install path (clone → build → run)

**Distribution:** source-first (clone → `./scripts/build-swift.sh` → run). No public DMG, notarization, or Sparkle.

**In progress / next:**
- [ ] Keep build-from-source / agent-friendly docs accurate
- [ ] Performance benchmarking vs Python daemon

---

## Testing

### Test Environment Setup

```bash
# Activate venv (always do this first)
source venv/bin/activate

# Dependencies are already installed (one-time setup was done)
# Only reinstall if adding new packages
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_config.py -v
pytest tests/test_model.py -v

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run only fast tests (skip integration)
pytest -m "not slow"

# Run integration tests (requires model download)
pytest -m slow
```

### Test Structure

```python
# tests/conftest.py - Shared fixtures
@pytest.fixture
def config():
    """Test configuration with CPU device"""

@pytest.fixture
def temp_audio_file(tmp_path):
    """Temporary audio file for testing"""

@pytest.fixture
def sample_transcription():
    """Mock transcription output"""

@pytest.fixture
def real_audio_file():
    """Path to real test audio"""
```

### Writing Tests

Follow TDD approach:
1. Write failing test first
2. Run test to confirm it fails
3. Implement minimal code to pass
4. Run test to confirm it passes
5. Refactor if needed
6. Commit

Example:
```python
# tests/test_output.py (to be created)
def test_save_transcription_simple(tmp_path):
    """Test saving transcription to file."""
    from src.output import OutputHandler

    handler = OutputHandler()
    handler.save_transcription(
        transcription={"text": "test"},
        output_path=tmp_path / "output.txt",
    )

    assert (tmp_path / "output.txt").exists()
```

---

## Development Workflow

### Virtual Environment

```bash
# Activate (every time you start work)
source venv/bin/activate

# Deactivate (when done)
deactivate

# Verify it's activated (should see (venv) in prompt)
which python  # Should point to venv/bin/python
```

### Pre-commit Hooks

Pre-commit runs Black and Ruff automatically before each commit:

```bash
# One-time setup
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Common Commands

```bash
# Format code
black --line-length 100 src/ tests/

# Lint code
ruff check --line-length 100 src/ tests/

# Install new dependency
pip install <package>
# Update requirements.txt manually (do NOT use pip freeze - it captures the full env)

# Run specific test with debugging
pytest tests/test_model.py::test_model_wrapper_initialization -v -s

# Build Swift app
./scripts/build-swift.sh          # debug (default)
./scripts/build-swift.sh release  # optimised binary

# Optional local DMG only (not for public distribution)
./scripts/package-dmg.sh
```

### Git Workflow

Simple main branch workflow:

```bash
# Check status
git status

# Commit changes
git add <files>
git commit -m "feat: description"

# Push to remote
git push origin main
```

**Commit Message Convention:**
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Add or modify tests
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### CI Pipeline

GitHub Actions runs on every push and PR to `main`:

| Job | What it does |
|-----|-------------|
| `python-lint` | Black + Ruff check (ubuntu-latest) |
| `python-test` | `pytest -m "not slow"` (macos-latest) |
| `swift-build` | `swift build` debug (macos-14) |
| `dependency-audit` | `pip-audit` on requirements.txt |

The pipeline is defined in `.github/workflows/ci.yml`.

---

## Model Information

**Current Model:** nvidia/parakeet-tdt-0.6b-v3

**Key Details:**
- **Parameters:** 600 million
- **Architecture:** FastConformer-TDT with full attention
- **Languages:** 25 European languages with automatic detection
- **Audio Format:** 16kHz monochannel (WAV, FLAC)
- **Output:** Text with punctuation, capitalization, timestamps
- **WER:** 6.05% average
- **License:** CC-BY-4.0

**Usage:**
```python
import nemo.collections.asr as nemo_asr

# Load model
model = nemo_asr.models.ASRModel.from_pretrained(
    "nvidia/parakeet-tdt-0.6b-v3"
)

# Transcribe
output = model.transcribe(["audio.wav"], timestamps=True)
print(output[0].text)
```

---

## Backend Architecture (Phase 3)

### Design Pattern: Strategy + Factory

```
┌─────────────────────────────────────────────┐
│          CLI / Python API                    │
│         (src/cli.py, src/model.py)          │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │  Backend Factory  │
         │  (Auto-detection) │
         └─────────┬─────────┘
                   │
        ┏━━━━━━━━━━┻━━━━━━━━━━┓
        ┃                     ┃
  ┌─────▼─────┐        ┌─────▼─────┐
  │    MLX    │        │   NeMo    │
  │  Backend  │        │  Backend  │
  │           │        │           │
  │  (Apple   │        │  (CUDA/   │
  │   ANE)    │        │  CPU/MPS) │
  └───────────┘        └───────────┘
```

### Backend Selection Logic

1. **macOS + Apple Silicon + MLX available** → MLX Backend (10x faster)
2. **NVIDIA GPU available** → NeMo CUDA Backend (3-5x faster)
3. **macOS + MPS available** → NeMo MPS Backend (2-3x faster)
4. **Fallback** → NeMo CPU Backend (baseline)

---

## Dependencies

### Core (requirements.txt)
```txt
nemo-toolkit[asr]>=2.2.0  # ASR model framework
torch>=2.0.0               # Deep learning
torchaudio>=2.0.0          # Audio processing
pyobjc-framework-Quartz>=10.0  # macOS event tap (fn-ptt)
click>=8.1.0               # CLI framework
colorama>=0.4.6            # Terminal colors
```

Testing and development tools are **not** in `requirements.txt` — install them separately:

```bash
pip install pytest pytest-cov pytest-mock  # tests
pip install black ruff pre-commit          # dev tools
```

### MLX (requirements-mlx.txt)
```txt
mlx>=0.20.0                # Apple Silicon ML framework
parakeet-mlx>=0.1.0        # MLX Parakeet implementation
librosa>=0.10.0            # Audio processing
soundfile>=0.12.0          # Audio I/O
```

---

## Troubleshooting

### Tests Failing

```bash
# Check venv is activated
which python  # Should be in venv/bin/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear pytest cache
rm -rf .pytest_cache
pytest --cache-clear
```

### Import Errors

```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:."

# Or use pytest with pythonpath configured in pyproject.toml
pytest  # Should work automatically
```

### Model Download Issues

```bash
# NeMo downloads models to cache on first use
# Location: ~/.cache/nemo/

# If download fails, check internet connection
# Model size: ~2.4GB

# Manual download (if needed)
huggingface-cli download nvidia/parakeet-tdt-0.6b-v3
```

### macOS MPS Issues

```bash
# Enable MPS fallback if getting errors
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Force CPU if MPS causes issues
# In src/config.py, set device="cpu"
```

---

## Performance Targets

| Platform | Backend | Expected Performance |
|----------|---------|---------------------|
| Mac M1/M2/M3 | MLX (ANE) | 10x faster than CPU |
| Mac M1/M2/M3 | NeMo (MPS) | 2-3x faster than CPU |
| Windows/Linux NVIDIA | NeMo (CUDA) | 3-5x faster than CPU |
| Any | NeMo (CPU) | Baseline |

**Benchmark Command (Phase 3):**
```bash
time parakeet-stt transcribe 2086-149220-0033.wav --device cpu
time parakeet-stt transcribe 2086-149220-0033.wav  # Auto-detect
```

---

## Development Guidelines

### Code Style

- **Line length:** 100 characters
- **Formatter:** Black
- **Linter:** Ruff
- **Type hints:** Encouraged but not required
- **Docstrings:** Required for public functions/classes

### Test Requirements

- **Coverage target:** >80%
- **Test isolation:** Use fixtures, no shared state
- **Mock external calls:** Patch NeMo model loading in unit tests
- **Integration tests:** Mark with `@pytest.mark.slow`

### Adding New Features

1. Read relevant docs in `docs/knowledge/`
2. Update implementation plan if needed
3. Write tests first (TDD)
4. Implement minimal code
5. Run tests and ensure they pass
6. Update documentation
7. Commit with descriptive message

---

## Key Files Reference

### Configuration
- `src/config.py` - All settings (model, device, paths)
- `pyproject.toml` - Project metadata, tool configs
- `.python-version` - Python version (3.10+)

### Core Implementation
- `src/model.py` - Main model wrapper
- `src/output.py` - Output formatting
- `src/cli.py` - CLI interface
- `src/daemon/` - Background recording daemon
- `src/fn_ptt/` - Python fn-key push-to-talk
- `swift/` - Native macOS menu-bar app (Kuaishuo)

### Build & Packaging
- `scripts/build-swift.sh` - Build Swift app (`debug` or `release` arg)
- `scripts/package-dmg.sh` - Optional local .app/DMG helper (not public releases)

### CI & Quality
- `.github/workflows/ci.yml` - GitHub Actions (lint, test, Swift build, dep audit)
- `.pre-commit-config.yaml` - Pre-commit hooks (Black, Ruff, trailing whitespace, etc.)

### Testing
- `tests/conftest.py` - Shared fixtures
- `tests/test_*.py` - Test modules
- `tests/fixtures/sample_audio.wav` - Test audio

### Documentation
- `README.md` - Project overview and usage
- `docs/knowledge/development-phases.md` - Phase details
- `docs/plans/` - Implementation plans per feature
- `CLAUDE.md` - This file

---

## Next Steps

### ✅ Phase 1: COMPLETE
- [x] Project structure and dependencies
- [x] Core module structure (`config.py`, `model.py`)
- [x] All tests passing (86% coverage)

### ✅ Phase 2: CLI + Daemon + fn-ptt — COMPLETE
- [x] `src/output.py` — output formatting
- [x] `src/cli.py` — Click CLI
- [x] `src/daemon/` — background daemon with Unix socket IPC
- [x] `src/fn_ptt/` — Python fn-key push-to-talk
- [x] Security hardening (dir/socket permissions, no text in logs)

### 🚀 Phase 3: Native macOS App — IN PROGRESS
- [x] Backend abstraction layer (`src/backends/`)
- [x] MLX backend for Apple Silicon
- [x] Swift menu-bar app (Kuaishuo) — CoreML inference
- [x] Optional local DMG packaging script (not public distribution)
- [x] CI pipeline (GitHub Actions)
- [x] Pre-commit hooks
- [x] Source-first install docs (clone → build → run; agent-friendly)
- [ ] Performance benchmarking (Swift CoreML vs Python NeMo)

---

## Resources

- **Implementation Plan:** [docs/plans/2026-02-11-minimal-stt-cli.md](docs/plans/2026-02-11-minimal-stt-cli.md)
- **Development Phases:** [docs/knowledge/development-phases.md](docs/knowledge/development-phases.md)
- **Model Documentation:** [docs/knowledge/parakeet-tdt-model.md](docs/knowledge/parakeet-tdt-model.md)
- **HuggingFace Model:** https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- **NeMo Docs:** https://docs.nvidia.com/nemo-framework/
- **MLX Framework:** https://github.com/ml-explore/mlx

---

**Last Updated:** 2026-08-09
**Python Version:** 3.10+ (venv: 3.14)
**Current Phase:** Phase 3 (Native macOS App)
**Phase 1 Status:** ✅ Complete
**Phase 2 Status:** ✅ Complete (CLI + daemon + fn-ptt)
**Distribution:** Source-first (no public DMG / notarization / Sparkle)
**Next Task:** Keep build-from-source path solid; optional performance benchmarking
