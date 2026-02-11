# Parakeet STT - Claude Development Guide

> **Project Context:** Local-first speech-to-text CLI application using NVIDIA's Parakeet TDT 0.6B v3 model, optimized for Apple Neural Engine via MLX framework.

---

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run tests
pytest

# Run specific test file
pytest tests/test_config.py -v

# Transcribe audio (once CLI is implemented)
parakeet-stt transcribe audio.wav
```

---

## Project Structure

```
parakeet-stt/
├── src/                         # Main application package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── model.py                 # Model wrapper with backend selection
│   ├── output.py                # Output formatting (to be implemented)
│   ├── cli.py                   # CLI interface (to be implemented)
│   └── backends/                # Backend implementations (Phase 3)
│       ├── __init__.py
│       ├── base.py              # Abstract base backend
│       ├── nemo_backend.py      # NeMo/PyTorch backend
│       ├── mlx_backend.py       # MLX/ANE backend (Apple Silicon)
│       └── factory.py           # Automatic backend selection
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures and config
│   ├── test_config.py           # Configuration tests
│   ├── test_model.py            # Model wrapper tests
│   ├── test_output.py           # Output handler tests (to be created)
│   ├── test_cli.py              # CLI tests (to be created)
│   ├── test_backends.py         # Backend tests (Phase 3)
│   ├── test_backend_factory.py  # Factory tests (Phase 3)
│   ├── test_mlx_backend.py      # MLX tests (Phase 3)
│   ├── test_integration.py      # End-to-end tests (to be created)
│   └── fixtures/
│       └── sample_audio.wav     # Test audio (2086-149220-0033.wav)
│
├── docs/                        # Documentation
│   ├── knowledge/
│   │   ├── parakeet-tdt-model.md      # Model specifications
│   │   └── development-phases.md      # Incremental delivery plan
│   ├── plans/
│   │   └── 2026-02-11-minimal-stt-cli.md  # Implementation plan
│   └── research/
│       ├── mlx-integration.md         # MLX research
│       └── mlx-api-investigation.md   # MLX API details (Phase 3)
│
├── output/                      # Transcription outputs
│   └── test/                    # Test outputs
│
├── venv/                        # Virtual environment (not in git)
├── 2086-149220-0033.wav         # Test audio file
│
├── requirements.txt             # Core dependencies
├── requirements-mlx.txt         # MLX dependencies (Phase 3)
├── pyproject.toml               # Project configuration
├── .python-version              # Python 3.10+
├── .gitignore
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

#### Phase 2: CLI Interface ⏳ **NEXT**
**Status:** Ready to start
**Deliverable:** End-user command-line tool

**To implement:**
- Task 4: `src/output.py` - Format and save transcriptions
- Task 5: `src/cli.py` - Click-based CLI interface
- Task 6: Integration tests with real audio

**Expected outcome:**
```bash
parakeet-stt transcribe audio.wav
cat output/audio.txt  # Formatted transcription
```

#### Phase 3: ANE Optimization ⏳ (Not Started)
**Deliverable:** Production-ready optimized app

**To be implemented:**
- Backend abstraction layer (`src/backends/`)
- MLX backend for Apple Silicon
- Automatic platform detection
- Performance benchmarking

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

### Common Commands

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Install new dependency
pip install <package>
pip freeze > requirements.txt  # Update requirements

# Run specific test with debugging
pytest tests/test_model.py::test_model_wrapper_initialization -v -s
```

### Git Workflow

Currently using simple main branch workflow. Future phases will use feature branches:

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
click>=8.1.0               # CLI framework
colorama>=0.4.6            # Terminal colors
pytest>=7.4.0              # Testing
pytest-cov>=4.1.0          # Coverage
black>=23.0.0              # Formatting
ruff>=0.1.0                # Linting
```

### MLX (requirements-mlx.txt) - Phase 3
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
- `src/output.py` - Output formatting (to be created)
- `src/cli.py` - CLI interface (to be created)

### Testing
- `tests/conftest.py` - Shared fixtures
- `tests/test_*.py` - Test modules
- `tests/fixtures/sample_audio.wav` - Test audio

### Documentation
- `README.md` - Project overview
- `docs/knowledge/development-phases.md` - Phase details
- `docs/plans/2026-02-11-minimal-stt-cli.md` - Implementation plan
- `CLAUDE.md` - This file

---

## Next Steps

### ✅ Phase 1: COMPLETE
- [x] Task 1: Project structure and dependencies
- [x] Task 2: Core module structure
- [x] Task 3: Model wrapper with MPS backend
- [x] All tests passing (86% coverage)

### 🚀 Phase 2: CLI Interface (CURRENT)
1. [ ] **Task 4:** Implement `src/output.py` - Output handler
2. [ ] **Task 5:** Implement `src/cli.py` - CLI application
3. [ ] **Task 6:** Create integration tests with real audio
4. [ ] Install as package: `pip install -e .`
5. [ ] Test CLI: `parakeet-stt transcribe 2086-149220-0033.wav`
6. [ ] Verify output file generation

### Phase 3 (MLX Optimization)
8. [ ] Research parakeet-mlx API
9. [ ] Implement backend abstraction
10. [ ] Implement MLX backend
11. [ ] Benchmark performance

---

## Resources

- **Implementation Plan:** [docs/plans/2026-02-11-minimal-stt-cli.md](docs/plans/2026-02-11-minimal-stt-cli.md)
- **Development Phases:** [docs/knowledge/development-phases.md](docs/knowledge/development-phases.md)
- **Model Documentation:** [docs/knowledge/parakeet-tdt-model.md](docs/knowledge/parakeet-tdt-model.md)
- **HuggingFace Model:** https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- **NeMo Docs:** https://docs.nvidia.com/nemo-framework/
- **MLX Framework:** https://github.com/ml-explore/mlx

---

**Last Updated:** 2026-02-11
**Python Version:** 3.10+ (venv: 3.14)
**Current Phase:** Phase 2 (CLI Interface)
**Phase 1 Status:** ✅ Complete (7/7 tests passing, 86% coverage)
**Next Task:** Implement `src/output.py` (Task 4)
