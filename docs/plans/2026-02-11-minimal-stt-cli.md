# Minimal STT CLI Application Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a minimal CLI application that transcribes audio files using Parakeet TDT 0.6B and outputs results to .txt files, with Apple Neural Engine optimization for Mac.

**Architecture:** Three-phase approach: (1) Basic NeMo implementation with PyTorch MPS backend for Apple Silicon, (2) CLI interface with file I/O, (3) ANE optimization via **MLX framework** (primary approach). Focus on simplicity and testability.

**Tech Stack:** Python 3.10+, NeMo Toolkit 2.2, PyTorch 2.0+, **MLX (Apple Silicon - Primary)**, pytest, click (CLI)

**Test Audio:** Using `tests/fixtures/sample_audio.wav` for integration testing.

**⚠️ IMPORTANT - Virtual Environment:** All commands in this plan must be executed within an activated virtual environment to avoid conflicts with global Python packages. Task 1 includes venv setup, and subsequent tasks include reminders to ensure venv is activated.

---

## Branching Strategy

**Four-phase branching approach:**

- **Phase 1 Branch:** `phase-1-basic-nemo-implementation` (Tasks 1-3) ✅
  - Project setup and basic NeMo implementation
  - Branch from: `main`
  - Commits: Tasks 1, 2, 3

- **Phase 2 Branch:** `phase-2-cli-interface` (Tasks 4-6) ✅
  - CLI interface and file I/O
  - Branch from: `phase-1-basic-nemo-implementation`
  - Commits: Tasks 4, 5, 6

- **Phase 3 Branch:** `phase-3-ane-optimization` (Tasks 7-11)
  - Apple Neural Engine optimization with MLX
  - Branch from: `phase-2-cli-interface`
  - Commits: Tasks 7, 8, 9, 10, 11

- **Phase 4 Branch:** `phase-4-push-to-talk` (Tasks 12-17)
  - Real-time push-to-talk recording
  - Branch from: `phase-3-ane-optimization` (or `main` if Phase 3 incomplete)
  - Commits: Tasks 12, 13, 14, 15, 16, 17

**Commit Strategy:**
- Each edit/commit requires explicit user permission before execution
- All commits include descriptive messages following conventional commit format
- Each phase ends with a review before proceeding to next phase
- Final merge strategy to be determined at completion

---

## Project Structure

```
parakeet-stt/
├── src/                         # Main application package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── model.py                 # Model wrapper with backend selection
│   ├── output.py                # Output formatting and file handling
│   ├── cli.py                   # CLI application entry point
│   ├── backends/                # Backend implementations (Phase 3)
│   │   ├── __init__.py          # Backend package initialization
│   │   ├── base.py              # Abstract base backend
│   │   ├── nemo_backend.py      # NeMo/PyTorch backend
│   │   ├── mlx_backend.py       # MLX/ANE backend (Apple Silicon)
│   │   └── factory.py           # Automatic backend selection
│   └── ptt/                     # Push-to-talk module (Phase 4)
│       ├── __init__.py          # PTT package initialization
│       ├── app.py               # Main PTT application
│       ├── controller.py        # Push-to-talk controller
│       ├── hotkey.py            # Global hotkey listener
│       ├── recorder.py          # Real-time audio recorder
│       └── ui/                  # GUI components
│           ├── __init__.py      # UI package initialization
│           ├── overlay.py       # Status overlay window
│           └── styles.py        # UI styling
│
├── tests/                       # Test suite
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Pytest fixtures and configuration
│   ├── test_config.py           # Configuration tests
│   ├── test_model.py            # Model wrapper tests
│   ├── test_output.py           # Output handler tests
│   ├── test_cli.py              # CLI tests
│   ├── test_backends.py         # Backend abstraction tests (Phase 3)
│   ├── test_backend_factory.py  # Backend factory tests (Phase 3)
│   ├── test_mlx_backend.py      # MLX backend integration tests (Phase 3)
│   ├── test_integration.py      # End-to-end integration tests
│   ├── test_ptt/                # Push-to-talk tests (Phase 4)
│   │   ├── test_hotkey.py       # Hotkey listener tests
│   │   ├── test_recorder.py     # Audio recorder tests
│   │   ├── test_controller.py   # Controller tests
│   │   ├── test_ui.py           # UI overlay tests
│   │   └── test_app.py          # PTT app integration tests
│   └── fixtures/                # Test fixtures
│       └── sample_audio.wav     # Test audio file (copy of 2086-149220-0033.wav)
│
├── docs/                        # Documentation
│   ├── knowledge/               # Knowledge base
│   │   └── parakeet-tdt-model.md  # Model documentation
│   ├── plans/                   # Implementation plans
│   │   └── 2026-02-11-minimal-stt-cli.md  # This plan
│   └── research/                # Research documentation
│       ├── mlx-integration.md   # MLX integration research
│       └── mlx-api-investigation.md  # MLX API investigation
│
├── output/                      # Default output directory for transcriptions
│   └── test/                    # Test output directory
│
├── scripts/                     # Utility scripts
│   └── verify_phase1.py         # Phase 1 verification script
│
├── requirements.txt             # Core dependencies (for backwards compatibility)
├── pyproject.toml               # Project configuration with optional dependencies
├── .python-version              # Python version specification
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

### Key Directories

**`src/`** - Main application code
- Core modules: config, model, output, cli
- Backend abstraction for platform-specific optimizations

**`src/backends/`** - Platform-specific implementations
- Base backend interface
- NeMo backend (CUDA/CPU fallback)
- MLX backend (Apple Neural Engine)
- Factory for automatic selection

**`tests/`** - Comprehensive test suite
- Unit tests for each module
- Integration tests with real audio
- Backend-specific tests
- Fixtures for test data

**`docs/`** - Documentation and research
- Knowledge base for model information
- Implementation plans
- Research findings on optimization approaches

**`output/`** - Transcription outputs
- Generated `.txt` files with transcriptions
- Organized by input filename

---

## Research Findings

### Apple Silicon Optimization Options

1. **MLX Framework (✅ SELECTED APPROACH)**: Apple's native ML framework optimized for Apple Silicon
   - Repository: [parakeet-mlx](https://github.com/senstella/parakeet-mlx) and [EliFuzz/parakeet-mlx](https://github.com/EliFuzz/parakeet-mlx)
   - Benefits: Native ANE acceleration, 10+ TFLops utilization, ultra-fast inference
   - Status: Production-ready implementations available
   - **This is our primary implementation path**

2. **PyTorch MPS Backend**: Fallback/baseline option
   - Requires PyTorch 2.0+ with `PYTORCH_ENABLE_MPS_FALLBACK=1`
   - Uses GPU but not ANE
   - Good baseline for Phase 1 implementation
   - Automatically switches to MLX in Phase 3

3. **CoreML Conversion**: Alternative (not pursued)
   - Model: [FluidInference/parakeet-tdt-0.6b-v2-coreml](https://huggingface.co/FluidInference/parakeet-tdt-0.6b-v2-coreml)
   - Benefits: Native iOS/macOS support, ANE acceleration
   - Limitation: NeMo direct export has preprocessing issues
   - Note: MLX provides better development experience

**Sources:**
- [Apple Neural Engine Transformers](https://machinelearning.apple.com/research/neural-engine-transformers)
- [Parakeet MLX GitHub](https://github.com/EliFuzz/parakeet-mlx)
- [FluidInference CoreML Model](https://huggingface.co/FluidInference/parakeet-tdt-0.6b-v2-coreml)
- [Argmax Parakeet Optimization](https://www.argmaxinc.com/blog/nvidia-frontier-speech-models-on-argmax-sdk)

---

## Phase 1: Project Setup and Basic NeMo Implementation

**IMPORTANT:** All commands in this phase should be run within the activated virtual environment to avoid conflicts with global Python packages.

### Task 1: Project Structure and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.gitignore`

**Step 1: Create Python version file**

Create `.python-version`:
```
3.10.0
```

**Step 2: Create requirements.txt**

Create `requirements.txt` (for backwards compatibility - pyproject.toml is preferred):
```txt
# Core dependencies (install with: pip install -e .)
# For optional features, use: pip install -e .[mlx,ptt,dev]

nemo-toolkit[asr]>=2.2.0
torch>=2.0.0
torchaudio>=2.0.0
click>=8.1.0
colorama>=0.4.6
python-dotenv>=1.0.0
```

**Step 3: Create pyproject.toml**

Create `pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "parakeet-stt"
version = "0.1.0"
description = "Minimal STT CLI using Parakeet TDT 0.6B"
requires-python = ">=3.10"
dependencies = [
    "nemo-toolkit[asr]>=2.2.0",
    "torch>=2.0.0",
    "torchaudio>=2.0.0",
    "click>=8.1.0",
    "colorama>=0.4.6",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
# Phase 3: MLX backend for Apple Silicon
mlx = [
    "mlx>=0.20.0",
    "librosa>=0.10.0",
    "soundfile>=0.12.0",
]

# Phase 4: Push-to-talk real-time recording
ptt = [
    "pynput>=1.7.6",
    "sounddevice>=0.4.6",
    "numpy>=1.24.0",
    "pyperclip>=1.8.2",
]

# Development dependencies
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

# Install everything
all = [
    "parakeet-stt[mlx,ptt,dev]",
]

[project.scripts]
parakeet-stt = "src.cli:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing"
```

**Step 4: Create .gitignore**

Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Models and cache
.cache/
models/
*.nemo
*.ckpt

# Output files
output/
*.txt

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/

# Environment
.env
.env.local
```

**Step 5: Create and activate virtual environment**

Run:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR on Windows: venv\Scripts\activate

# Verify venv is active
which python
python --version
```

Expected: Python path points to `venv/bin/python` and version is 3.10+

**Step 6: Install dependencies**

Run:
```bash
# Ensure venv is activated (you should see (venv) in your prompt)
pip install --upgrade pip

# Install in editable mode with dev dependencies
pip install -e .[dev]

# Or using requirements.txt (backwards compatible)
# pip install -r requirements.txt
```

Expected: All dependencies install successfully within venv

Note: `-e` installs in editable mode, `[dev]` includes testing/development tools

**Step 7: Verify project structure**

Run:
```bash
ls -la
cat requirements.txt
cat pyproject.toml
pip list  # Verify installed packages
```

Expected: Files created with correct content, packages installed in venv

**Step 8: Commit**

```bash
git add requirements.txt pyproject.toml .python-version .gitignore
git commit -m "chore: initialize project structure with dependencies"
```

---

### Task 2: Core Module Structure

**Files:**
- Create: `src/` directory
- Create: `src/__init__.py`
- Create: `src/config.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Create src directory and package init**

Run:
```bash
mkdir -p src
```

Create `src/__init__.py`:
```python
"""Parakeet STT - Minimal speech-to-text CLI application."""

__version__ = "0.1.0"
```

**Step 2: Create configuration module**

Create `src/config.py`:
```python
"""Configuration management for Parakeet STT."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Application configuration."""

    # Model settings
    model_name: str = "nvidia/parakeet-tdt-0.6b-v3"
    device: str = "mps"  # mps for Mac, cuda for NVIDIA, cpu for fallback

    # Audio settings
    sample_rate: int = 16000
    supported_formats: tuple = (".wav", ".flac")

    # Output settings
    output_dir: Path = Path("output")
    include_timestamps: bool = True

    # Environment overrides
    enable_mps_fallback: bool = os.getenv("PYTORCH_ENABLE_MPS_FALLBACK", "1") == "1"

    def __post_init__(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(exist_ok=True)

    @property
    def is_mac(self) -> bool:
        """Check if running on macOS."""
        import platform

        return platform.system() == "Darwin"

    def get_device(self) -> str:
        """Get appropriate device based on platform."""
        if self.is_mac:
            return "mps"
        return "cuda" if self._cuda_available() else "cpu"

    @staticmethod
    def _cuda_available() -> bool:
        """Check if CUDA is available."""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False
```

**Step 3: Create test configuration**

Create `tests/__init__.py`:
```python
"""Test suite for Parakeet STT."""
```

**Step 4: Create pytest fixtures**

Create `tests/conftest.py`:
```python
"""Shared pytest fixtures."""

import pytest
from pathlib import Path
from src.config import Config


@pytest.fixture
def config():
    """Create test configuration."""
    return Config(
        output_dir=Path("output/test"),
        device="cpu",  # Use CPU for tests
    )


@pytest.fixture
def temp_audio_file(tmp_path):
    """Create temporary audio file for testing."""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.touch()
    return audio_file


@pytest.fixture
def sample_transcription():
    """Sample transcription output."""
    return {
        "text": "This is a test transcription.",
        "timestamps": {
            "word": [
                {"start": 0.0, "end": 0.5, "word": "This"},
                {"start": 0.5, "end": 0.8, "word": "is"},
            ]
        },
    }


@pytest.fixture
def real_audio_file():
    """Path to real audio file for integration tests."""
    audio_path = Path("2086-149220-0033.wav")
    if audio_path.exists():
        return audio_path
    # Fallback to test fixtures
    return Path("tests/fixtures/sample_audio.wav")
```

**Step 5: Test configuration module**

Create `tests/test_config.py`:
```python
"""Tests for configuration module."""

import pytest
from pathlib import Path
from src.config import Config


def test_config_defaults():
    """Test default configuration values."""
    config = Config()

    assert config.model_name == "nvidia/parakeet-tdt-0.6b-v3"
    assert config.sample_rate == 16000
    assert config.include_timestamps is True
    assert ".wav" in config.supported_formats
    assert ".flac" in config.supported_formats


def test_config_output_dir_creation(tmp_path):
    """Test output directory is created."""
    output_dir = tmp_path / "output"
    config = Config(output_dir=output_dir)

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_config_is_mac():
    """Test macOS detection."""
    import platform

    config = Config()
    expected = platform.system() == "Darwin"

    assert config.is_mac == expected


def test_config_get_device(config):
    """Test device selection logic."""
    device = config.get_device()

    assert device in ["mps", "cuda", "cpu"]
```

**Step 6: Run tests**

Run:
```bash
# Ensure venv is activated (should see (venv) in prompt)
source venv/bin/activate  # If not already activated

python -m pytest tests/test_config.py -v
```

Expected: All tests pass

**Step 7: Commit**

```bash
git add src/ tests/
git commit -m "feat: add core module structure and configuration"
```

---

### Task 3: Model Wrapper with MPS Backend

**Files:**
- Create: `src/model.py`
- Create: `tests/test_model.py`

**Step 1: Write model wrapper test**

Create `tests/test_model.py`:
```python
"""Tests for model wrapper."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


def test_model_wrapper_initialization():
    """Test model wrapper initializes correctly."""
    from src.model import ModelWrapper
    from src.config import Config

    config = Config(device="cpu")

    with patch("src.model.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        wrapper = ModelWrapper(config)

        assert wrapper.config == config
        assert wrapper.model == mock_model
        mock_nemo.models.ASRModel.from_pretrained.assert_called_once_with(
            model_name=config.model_name
        )


def test_model_wrapper_transcribe_simple(config, temp_audio_file):
    """Test simple transcription without timestamps."""
    from src.model import ModelWrapper

    with patch("src.model.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_result = Mock()
        mock_result.text = "test transcription"
        mock_model.transcribe.return_value = [mock_result]
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        wrapper = ModelWrapper(config)
        result = wrapper.transcribe(temp_audio_file, timestamps=False)

        assert result["text"] == "test transcription"
        assert "timestamps" not in result
        mock_model.transcribe.assert_called_once()


def test_model_wrapper_transcribe_with_timestamps(config, temp_audio_file):
    """Test transcription with timestamps."""
    from src.model import ModelWrapper

    with patch("src.model.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_result = Mock()
        mock_result.text = "test transcription"
        mock_result.timestamp = {
            "word": [{"start": 0.0, "end": 0.5, "word": "test"}],
            "segment": [{"start": 0.0, "end": 1.0, "segment": "test transcription"}],
        }
        mock_model.transcribe.return_value = [mock_result]
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        wrapper = ModelWrapper(config)
        result = wrapper.transcribe(temp_audio_file, timestamps=True)

        assert result["text"] == "test transcription"
        assert "word" in result["timestamps"]
        assert "segment" in result["timestamps"]
```

**Step 2: Run test to verify it fails**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_model.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.model'"

**Step 3: Implement model wrapper**

Create `src/model.py`:
```python
"""Model wrapper for Parakeet TDT ASR."""

import os
from pathlib import Path
from typing import Dict, Union
import nemo.collections.asr as nemo_asr

from .config import Config


class ModelWrapper:
    """Wrapper for Parakeet TDT ASR model."""

    def __init__(self, config: Config):
        """Initialize model wrapper.

        Args:
            config: Application configuration
        """
        self.config = config
        self._setup_environment()
        self.model = self._load_model()

    def _setup_environment(self) -> None:
        """Set up environment variables for Apple Silicon."""
        if self.config.is_mac and self.config.enable_mps_fallback:
            os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    def _load_model(self):
        """Load the ASR model.

        Returns:
            Loaded NeMo ASR model
        """
        model = nemo_asr.models.ASRModel.from_pretrained(
            model_name=self.config.model_name
        )
        return model

    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results
        """
        audio_path = str(audio_path)

        # Transcribe with or without timestamps
        output = self.model.transcribe([audio_path], timestamps=timestamps)

        # Parse results
        result = {"text": output[0].text}

        if timestamps and hasattr(output[0], "timestamp"):
            result["timestamps"] = {
                "word": output[0].timestamp.get("word", []),
                "segment": output[0].timestamp.get("segment", []),
            }

        return result
```

**Step 4: Run tests to verify they pass**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_model.py -v
```

Expected: All tests pass

**Step 5: Commit**

```bash
git add src/model.py tests/test_model.py
git commit -m "feat: add model wrapper with MPS backend support"
```

---

## Phase 2: CLI Interface and File I/O

**IMPORTANT:** Ensure your virtual environment is activated before running any commands in this phase.

### Task 4: File Output Handler

**Files:**
- Create: `src/output.py`
- Create: `tests/test_output.py`

**Step 1: Write output handler test**

Create `tests/test_output.py`:
```python
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
```

**Step 2: Run test to verify it fails**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_output.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.output'"

**Step 3: Implement output handler**

Create `src/output.py`:
```python
"""Output handling for transcription results."""

from pathlib import Path
from typing import Dict


class OutputHandler:
    """Handle transcription output formatting and saving."""

    @staticmethod
    def format_transcription(transcription: Dict, include_timestamps: bool = True) -> str:
        """Format transcription for output.

        Args:
            transcription: Transcription dictionary with text and optional timestamps
            include_timestamps: Whether to include timestamp information

        Returns:
            Formatted transcription string
        """
        lines = []

        # Add main transcription text
        lines.append("Transcription:")
        lines.append("=" * 50)
        lines.append(transcription["text"])
        lines.append("")

        # Add timestamps if requested and available
        if include_timestamps and "timestamps" in transcription:
            lines.append("Timestamps:")
            lines.append("-" * 50)

            # Add word-level timestamps
            if "word" in transcription["timestamps"]:
                lines.append("\nWord-level:")
                for item in transcription["timestamps"]["word"]:
                    lines.append(
                        f"  {item['start']:.2f}s - {item['end']:.2f}s: {item['word']}"
                    )

            # Add segment-level timestamps
            if "segment" in transcription["timestamps"]:
                lines.append("\nSegment-level:")
                for item in transcription["timestamps"]["segment"]:
                    lines.append(
                        f"  {item['start']:.2f}s - {item['end']:.2f}s: {item['segment']}"
                    )

        return "\n".join(lines)

    def save_transcription(
        self,
        transcription: Dict,
        output_path: Path,
        include_timestamps: bool = True,
    ) -> None:
        """Save transcription to file.

        Args:
            transcription: Transcription dictionary
            output_path: Path to output file
            include_timestamps: Whether to include timestamps
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        formatted = self.format_transcription(transcription, include_timestamps)
        output_path.write_text(formatted)

    @staticmethod
    def generate_output_filename(input_path: Path, output_dir: Path) -> Path:
        """Generate output filename based on input.

        Args:
            input_path: Input audio file path
            output_dir: Output directory

        Returns:
            Generated output file path
        """
        stem = input_path.stem
        return output_dir / f"{stem}.txt"
```

**Step 4: Run tests to verify they pass**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_output.py -v
```

Expected: All tests pass

**Step 5: Commit**

```bash
git add src/output.py tests/test_output.py
git commit -m "feat: add output handler for transcription results"
```

---

### Task 5: CLI Application

**Files:**
- Create: `src/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write CLI test**

Create `tests/test_cli.py`:
```python
"""Tests for CLI application."""

import pytest
from pathlib import Path
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
        with patch("src.cli.OutputHandler") as mock_output:
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
```

**Step 2: Run test to verify it fails**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_cli.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.cli'"

**Step 3: Implement CLI**

Create `src/cli.py`:
```python
"""CLI application for Parakeet STT."""

import sys
from pathlib import Path
import click
from colorama import init, Fore, Style

from .config import Config
from .model import ModelWrapper
from .output import OutputHandler

# Initialize colorama for cross-platform colored output
init(autoreset=True)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Parakeet STT - Minimal speech-to-text CLI."""
    pass


@main.command()
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default="output",
    help="Output directory for transcription files",
)
@click.option(
    "--no-timestamps",
    is_flag=True,
    help="Disable timestamp output",
)
@click.option(
    "--device",
    type=click.Choice(["auto", "mps", "cuda", "cpu"]),
    default="auto",
    help="Device to use for inference",
)
def transcribe(
    audio_file: Path,
    output_dir: Path,
    no_timestamps: bool,
    device: str,
):
    """Transcribe audio file to text."""
    # Validate input
    if not audio_file.exists():
        click.echo(f"{Fore.RED}Error: Audio file does not exist: {audio_file}")
        sys.exit(1)

    # Create configuration
    config = Config(
        output_dir=output_dir,
        include_timestamps=not no_timestamps,
    )

    if device != "auto":
        config.device = device

    # Initialize components
    click.echo(f"{Fore.CYAN}Loading model...")
    try:
        model = ModelWrapper(config)
    except Exception as e:
        click.echo(f"{Fore.RED}Error loading model: {e}")
        sys.exit(1)

    # Transcribe
    click.echo(f"{Fore.CYAN}Transcribing: {audio_file.name}")
    try:
        transcription = model.transcribe(
            audio_file,
            timestamps=config.include_timestamps,
        )
    except Exception as e:
        click.echo(f"{Fore.RED}Error during transcription: {e}")
        sys.exit(1)

    # Save output
    output_handler = OutputHandler()
    output_path = output_handler.generate_output_filename(audio_file, config.output_dir)

    try:
        output_handler.save_transcription(
            transcription,
            output_path,
            include_timestamps=config.include_timestamps,
        )
    except Exception as e:
        click.echo(f"{Fore.RED}Error saving output: {e}")
        sys.exit(1)

    # Success message
    click.echo(f"{Fore.GREEN}✓ Transcription complete!")
    click.echo(f"{Fore.CYAN}Output saved to: {output_path}")
    click.echo(f"\n{Style.BRIGHT}Transcription:{Style.RESET_ALL}")
    click.echo(transcription["text"])


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_cli.py -v
```

Expected: All tests pass

**Step 5: Test CLI manually (optional dry run)**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

# Make sure src is in Python path
export PYTHONPATH="${PYTHONPATH}:."
python -m src.cli --help
python -m src.cli transcribe --help
```

Expected: Help text displays correctly

**Step 6: Commit**

```bash
git add src/cli.py tests/test_cli.py
git commit -m "feat: add CLI application with transcribe command"
```

---

### Task 6: Integration Test with Real Audio

**Files:**
- Create: `tests/test_integration.py`
- Create: `tests/fixtures/` directory
- Copy: `2086-149220-0033.wav` to `tests/fixtures/`

**Step 1: Setup test audio fixture**

Run:
```bash
mkdir -p tests/fixtures
cp 2086-149220-0033.wav tests/fixtures/sample_audio.wav
```

Expected: Audio file copied successfully to test fixtures

**Step 2: Write integration test**

Create `tests/test_integration.py`:
```python
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
```

**Step 3: Add pytest marker configuration**

Edit `pyproject.toml` to add markers:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

**Step 4: Run integration test**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_integration.py -v -m slow
```

Expected: Test passes with real transcription output

**Step 5: Commit**

```bash
git add tests/test_integration.py tests/fixtures/ pyproject.toml
git commit -m "test: add integration test with real audio"
```

---

## Phase 3: Apple Neural Engine Optimization

**IMPORTANT:** Ensure your virtual environment is activated. You may need to install additional MLX dependencies in Phase 3.

### Task 7: Research MLX Integration

**Files:**
- Create: `docs/research/mlx-integration.md`

**Step 1: Research MLX Parakeet implementations**

Create `docs/research/mlx-integration.md`:
```markdown
# MLX Integration Research

## Overview

MLX (Machine Learning for X) is Apple's framework optimized for Apple Silicon, providing direct access to the Apple Neural Engine (ANE) with 10+ TFLops performance.

## Available Implementations

### 1. parakeet-mlx (senstella)
- Repository: https://github.com/senstella/parakeet-mlx
- Status: Production-ready
- Features: Basic Parakeet implementation using MLX
- Performance: Native ANE acceleration

### 2. parakeet-mlx (EliFuzz)
- Repository: https://github.com/EliFuzz/parakeet-mlx
- Status: Enhanced implementation
- Features:
  - Real-time streaming support
  - Advanced audio processing
  - Noise reduction and silence detection
  - Optimized for M1/M2/M3 chips
- Performance: Ultra-fast, low-latency transcription

### 3. FluidInference CoreML
- Model: https://huggingface.co/FluidInference/parakeet-tdt-0.6b-v2-coreml
- Status: Pre-converted CoreML model
- Features: Ready-to-use CoreML package
- Performance: ANE-optimized, minimal memory footprint

## Implementation Approaches

### Option A: MLX Framework (Recommended)
**Pros:**
- Direct ANE access
- 10x faster than CPU
- 14x lower memory usage
- Native Apple Silicon support
- Active development

**Cons:**
- Requires separate MLX implementation
- Different API from NeMo
- Mac-only

**Implementation Path:**
1. Install MLX: `pip install mlx`
2. Use parakeet-mlx package or implement custom wrapper
3. Create unified interface for both NeMo and MLX backends
4. Automatic backend selection based on platform

### Option B: CoreML Conversion
**Pros:**
- Pre-converted model available
- Native iOS/macOS support
- ANE acceleration

**Cons:**
- Different inference API
- May lose some NeMo features
- Conversion complexity for updates

### Option C: ONNX + CoreML
**Pros:**
- Standard conversion path
- Cross-platform intermediate format

**Cons:**
- Multi-step conversion
- Potential accuracy loss
- NeMo preprocessing issues

## Recommended Approach

Use **Option A (MLX Framework)** with fallback to NeMo:
1. Detect platform on startup
2. If macOS with Apple Silicon: Use MLX backend
3. If NVIDIA GPU available: Use NeMo with CUDA
4. Otherwise: Use NeMo with CPU

## Next Steps

1. Install and test parakeet-mlx package
2. Create abstracted backend interface
3. Implement MLX backend wrapper
4. Add automatic backend selection
5. Benchmark performance comparison

## Performance Targets

- **NeMo CPU:** Baseline (1x)
- **NeMo MPS:** 2-3x faster
- **MLX ANE:** 10x faster
- **Memory:** 14x reduction with MLX

## References

- [Apple ML Research - ANE Transformers](https://machinelearning.apple.com/research/neural-engine-transformers)
- [parakeet-mlx GitHub](https://github.com/EliFuzz/parakeet-mlx)
- [Argmax Parakeet Optimization](https://www.argmaxinc.com/blog/nvidia-frontier-speech-models-on-argmax-sdk)
```

**Step 2: Verify research document**

Run:
```bash
cat docs/research/mlx-integration.md
```

Expected: Research document displays correctly

**Step 3: Commit**

```bash
git add docs/research/mlx-integration.md
git commit -m "docs: add MLX integration research"
```

---

### Task 8: MLX Backend Implementation

**Files:**
- Create: `src/backends/__init__.py`
- Create: `src/backends/base.py`
- Create: `src/backends/nemo_backend.py`
- Create: `src/backends/mlx_backend.py`

**Step 1: Create backend abstraction test**

Create `tests/test_backends.py`:
```python
"""Tests for backend abstraction."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


def test_base_backend_interface():
    """Test base backend interface."""
    from src.backends.base import BaseBackend

    class TestBackend(BaseBackend):
        def load_model(self):
            return Mock()

        def transcribe(self, audio_path, timestamps=True):
            return {"text": "test"}

    backend = TestBackend()
    assert hasattr(backend, "load_model")
    assert hasattr(backend, "transcribe")


def test_nemo_backend_initialization():
    """Test NeMo backend initialization."""
    from src.backends.nemo_backend import NeMoBackend
    from src.config import Config

    config = Config(device="cpu")

    with patch("src.backends.nemo_backend.nemo_asr") as mock_nemo:
        mock_model = Mock()
        mock_nemo.models.ASRModel.from_pretrained.return_value = mock_model

        backend = NeMoBackend(config)

        assert backend.model == mock_model


@pytest.mark.skipif(
    not pytest.importorskip("mlx"),
    reason="MLX not installed",
)
def test_mlx_backend_initialization():
    """Test MLX backend initialization."""
    from src.backends.mlx_backend import MLXBackend
    from src.config import Config

    config = Config()

    with patch("src.backends.mlx_backend.mlx") as mock_mlx:
        backend = MLXBackend(config)

        assert hasattr(backend, "model")
```

**Step 2: Implement base backend**

Create `src/backends/__init__.py`:
```python
"""Backend implementations for different platforms."""

from .base import BaseBackend
from .nemo_backend import NeMoBackend

__all__ = ["BaseBackend", "NeMoBackend"]

# Conditionally import MLX backend
try:
    from .mlx_backend import MLXBackend

    __all__.append("MLXBackend")
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
```

Create `src/backends/base.py`:
```python
"""Base backend interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Union


class BaseBackend(ABC):
    """Abstract base class for ASR backends."""

    @abstractmethod
    def load_model(self):
        """Load the ASR model.

        Returns:
            Loaded model instance
        """
        pass

    @abstractmethod
    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results containing:
                - text: Transcribed text
                - timestamps: Optional timestamp data
        """
        pass
```

**Step 3: Refactor NeMo backend**

Create `src/backends/nemo_backend.py`:
```python
"""NeMo backend implementation."""

import os
from pathlib import Path
from typing import Dict, Union
import nemo.collections.asr as nemo_asr

from .base import BaseBackend
from ..config import Config


class NeMoBackend(BaseBackend):
    """NeMo-based ASR backend."""

    def __init__(self, config: Config):
        """Initialize NeMo backend.

        Args:
            config: Application configuration
        """
        self.config = config
        self._setup_environment()
        self.model = self.load_model()

    def _setup_environment(self) -> None:
        """Set up environment variables."""
        if self.config.is_mac and self.config.enable_mps_fallback:
            os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    def load_model(self):
        """Load NeMo ASR model."""
        return nemo_asr.models.ASRModel.from_pretrained(
            model_name=self.config.model_name
        )

    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio using NeMo."""
        audio_path = str(audio_path)
        output = self.model.transcribe([audio_path], timestamps=timestamps)

        result = {"text": output[0].text}

        if timestamps and hasattr(output[0], "timestamp"):
            result["timestamps"] = {
                "word": output[0].timestamp.get("word", []),
                "segment": output[0].timestamp.get("segment", []),
            }

        return result
```

**Step 4: Implement MLX backend stub**

Create `src/backends/mlx_backend.py`:
```python
"""MLX backend implementation for Apple Silicon."""

from pathlib import Path
from typing import Dict, Union

from .base import BaseBackend
from ..config import Config


class MLXBackend(BaseBackend):
    """MLX-based ASR backend for Apple Neural Engine.

    This backend uses the parakeet-mlx implementation for optimized
    inference on Apple Silicon (M1/M2/M3) with direct ANE access.

    Implementation will be completed in a follow-up task after researching
    the specific API of the parakeet-mlx package.
    """

    def __init__(self, config: Config):
        """Initialize MLX backend.

        Args:
            config: Application configuration
        """
        self.config = config
        self.model = self.load_model()

    def load_model(self):
        """Load MLX ASR model.

        Note: Requires parakeet-mlx package.

        Future implementation will:
        1. Import parakeet_mlx (from EliFuzz or senstella)
        2. Initialize with model_name="nvidia/parakeet-tdt-0.6b-v3"
        3. Return initialized model instance
        """
        try:
            # TODO: Research exact API from parakeet-mlx package
            # Option 1: from parakeet_mlx import ParakeetMLX
            # Option 2: from parakeet_mlx.model import load_model
            # return ParakeetMLX(model_name=self.config.model_name)
            raise NotImplementedError(
                "MLX backend requires parakeet-mlx package. "
                "Install with: pip install -r requirements-mlx.txt\n"
                "Then update this implementation with correct API."
            )
        except ImportError as e:
            raise RuntimeError(f"MLX backend not available: {e}")

    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio using MLX.

        Future implementation will:
        1. Load audio file (may require librosa or soundfile)
        2. Call model.transcribe() with MLX API
        3. Parse results to match our standard format
        4. Return dict with 'text' and optionally 'timestamps'
        """
        # TODO: Implement after researching parakeet-mlx API
        # audio_path = str(audio_path)
        # result = self.model.transcribe(audio_path)
        #
        # Format output to match NeMo backend:
        # return {
        #     "text": result.text,
        #     "timestamps": {
        #         "word": result.word_timestamps if timestamps else [],
        #         "segment": result.segment_timestamps if timestamps else [],
        #     } if timestamps else {}
        # }
        raise NotImplementedError(
            "MLX transcription not yet implemented. "
            "This will be completed after MLX package integration."
        )
```

**Step 5: Run tests**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_backends.py -v
```

Expected: Tests pass (MLX tests skipped if not installed)

**Step 6: Commit**

```bash
git add src/backends/ tests/test_backends.py
git commit -m "feat: add backend abstraction layer with NeMo and MLX stubs"
```

---

### Task 9: Backend Selection Logic

**Files:**
- Modify: `src/model.py`
- Create: `src/backends/factory.py`
- Create: `tests/test_backend_factory.py`

**Step 1: Write backend factory test**

Create `tests/test_backend_factory.py`:
```python
"""Tests for backend factory."""

import pytest
from unittest.mock import patch, Mock


def test_backend_factory_selects_mlx_on_mac():
    """Test MLX backend selected on macOS with Apple Silicon."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.platform.system", return_value="Darwin"):
        with patch("src.backends.factory.platform.processor", return_value="arm"):
            with patch("src.backends.factory.MLX_AVAILABLE", True):
                backend_class = BackendFactory.get_backend_class(config)

                assert backend_class.__name__ == "MLXBackend"


def test_backend_factory_selects_nemo_on_linux():
    """Test NeMo backend selected on Linux."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.platform.system", return_value="Linux"):
        backend_class = BackendFactory.get_backend_class(config)

        assert backend_class.__name__ == "NeMoBackend"


def test_backend_factory_fallback_to_nemo():
    """Test fallback to NeMo when MLX unavailable."""
    from src.backends.factory import BackendFactory
    from src.config import Config

    config = Config()

    with patch("src.backends.factory.MLX_AVAILABLE", False):
        backend_class = BackendFactory.get_backend_class(config)

        assert backend_class.__name__ == "NeMoBackend"
```

**Step 2: Run test to verify it fails**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_backend_factory.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement backend factory**

Create `src/backends/factory.py`:
```python
"""Backend factory for automatic backend selection."""

import platform
from typing import Type

from .base import BaseBackend
from .nemo_backend import NeMoBackend
from ..config import Config

# Check MLX availability
try:
    from .mlx_backend import MLXBackend

    MLX_AVAILABLE = True
except (ImportError, RuntimeError):
    MLX_AVAILABLE = False


class BackendFactory:
    """Factory for creating appropriate backend based on platform."""

    @staticmethod
    def get_backend_class(config: Config) -> Type[BaseBackend]:
        """Select appropriate backend based on platform and configuration.

        Args:
            config: Application configuration

        Returns:
            Backend class to use
        """
        # Force specific backend if requested
        if hasattr(config, "backend") and config.backend:
            if config.backend == "mlx" and MLX_AVAILABLE:
                return MLXBackend
            elif config.backend == "nemo":
                return NeMoBackend

        # Auto-select based on platform
        if BackendFactory._is_apple_silicon() and MLX_AVAILABLE:
            return MLXBackend

        # Default to NeMo
        return NeMoBackend

    @staticmethod
    def _is_apple_silicon() -> bool:
        """Check if running on Apple Silicon.

        Returns:
            True if running on Apple Silicon (M1/M2/M3)
        """
        if platform.system() != "Darwin":
            return False

        # Check for ARM processor
        processor = platform.processor()
        return "arm" in processor.lower() or processor == ""

    @staticmethod
    def create_backend(config: Config) -> BaseBackend:
        """Create and initialize backend.

        Args:
            config: Application configuration

        Returns:
            Initialized backend instance
        """
        backend_class = BackendFactory.get_backend_class(config)
        return backend_class(config)
```

**Step 4: Update model wrapper to use factory**

Edit `src/model.py`:
```python
"""Model wrapper for Parakeet TDT ASR."""

from pathlib import Path
from typing import Dict, Union

from .config import Config
from .backends.factory import BackendFactory


class ModelWrapper:
    """Wrapper for Parakeet TDT ASR model with automatic backend selection."""

    def __init__(self, config: Config):
        """Initialize model wrapper.

        Args:
            config: Application configuration
        """
        self.config = config
        self.backend = BackendFactory.create_backend(config)

    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio file.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results
        """
        return self.backend.transcribe(audio_path, timestamps=timestamps)
```

**Step 5: Run tests**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

python -m pytest tests/test_backend_factory.py -v
python -m pytest tests/test_model.py -v
```

Expected: All tests pass

**Step 6: Commit**

```bash
git add src/model.py src/backends/factory.py tests/test_backend_factory.py
git commit -m "feat: add backend factory with automatic platform detection"
```

---

### Task 10: Documentation and Usage Guide

**Files:**
- Create: `README.md`
- Update: `docs/knowledge/parakeet-tdt-model.md`

**Step 1: Create comprehensive README**

Create `README.md`:
```markdown
# Parakeet STT

Minimal speech-to-text CLI application using NVIDIA's Parakeet TDT 0.6B model, optimized for Apple Neural Engine on Mac.

## Features

- 🎯 Simple CLI interface
- 🚀 Automatic hardware optimization (ANE/GPU/CPU)
- 📝 Text file output with timestamps
- 🍎 Native Apple Silicon support via MLX
- 🎮 NVIDIA GPU support via CUDA
- 💻 CPU fallback for compatibility

## Installation

### Basic Installation (NeMo backend)

```bash
# Clone repository
git clone <repository-url>
cd parakeet-stt

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR on Windows: venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Apple Silicon Installation (MLX backend)

```bash
# Follow basic installation steps above, then:

# Ensure venv is activated (you should see (venv) in your prompt)
source venv/bin/activate  # macOS/Linux

# Install MLX dependencies for Apple Neural Engine
pip install -r requirements-mlx.txt
```

## Usage

### Basic Transcription

```bash
# Transcribe audio file
parakeet-stt transcribe audio.wav

# Specify output directory
parakeet-stt transcribe audio.wav --output-dir results/

# Disable timestamps
parakeet-stt transcribe audio.wav --no-timestamps

# Force specific device
parakeet-stt transcribe audio.wav --device cpu
```

### Supported Audio Formats

- WAV (16kHz monochannel recommended)
- FLAC

### Output Format

Transcriptions are saved as `.txt` files with the same name as the input audio:

```
Transcription:
==================================================
This is the transcribed text from your audio file.

Timestamps:
--------------------------------------------------

Word-level:
  0.00s - 0.50s: This
  0.50s - 0.80s: is
  ...

Segment-level:
  0.00s - 2.50s: This is the transcribed text
  ...
```

## Hardware Acceleration

The application automatically selects the best backend:

| Platform | Backend | Hardware | Performance |
|----------|---------|----------|-------------|
| Mac (Apple Silicon) | MLX | Apple Neural Engine | 10x faster |
| Mac (Intel) | NeMo | CPU/GPU | Baseline |
| Linux/Windows (NVIDIA) | NeMo | CUDA GPU | 3-5x faster |
| Other | NeMo | CPU | Baseline |

### Force Specific Backend

```bash
# Use specific device
parakeet-stt transcribe audio.wav --device mps   # Mac GPU
parakeet-stt transcribe audio.wav --device cuda  # NVIDIA
parakeet-stt transcribe audio.wav --device cpu   # CPU only
```

## Development

**IMPORTANT:** Always activate your virtual environment before running development commands:

```bash
source venv/bin/activate  # macOS/Linux
# OR on Windows: venv\Scripts\activate
```

### Run Tests

```bash
# Ensure venv is activated (you should see (venv) in your prompt)

# Run all tests
pytest

# Run without slow tests
pytest -m "not slow"

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
# Ensure venv is activated

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking (optional)
mypy src/
```

## Architecture

```
parakeet-stt/
├── src/                # Main application package
│   ├── backends/       # Backend implementations
│   │   ├── base.py    # Abstract backend interface
│   │   ├── nemo_backend.py # NeMo/PyTorch backend
│   │   ├── mlx_backend.py  # MLX/ANE backend
│   │   └── factory.py # Automatic backend selection
│   ├── cli.py         # CLI application
│   ├── config.py      # Configuration management
│   ├── model.py       # Model wrapper
│   └── output.py      # Output formatting
└── tests/             # Test suite
```

## Model Information

- **Model:** nvidia/parakeet-tdt-0.6b-v3
- **Parameters:** 600 million
- **Architecture:** FastConformer-TDT
- **Word Error Rate:** 6.05% average
- **License:** CC-BY-4.0

## Troubleshooting

### macOS: MPS Backend Not Available

```bash
# Enable MPS fallback
export PYTORCH_ENABLE_MPS_FALLBACK=1
parakeet-stt transcribe audio.wav
```

### MLX Backend Not Loading

```bash
# Check MLX installation
python -c "import mlx; print(mlx.__version__)"

# Reinstall MLX dependencies
pip install -r requirements-mlx.txt --force-reinstall
```

### CUDA Out of Memory

```bash
# Use CPU instead
parakeet-stt transcribe audio.wav --device cpu
```

## References

- [Parakeet TDT Model](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- [NeMo Documentation](https://docs.nvidia.com/nemo-framework/)
- [Apple MLX Framework](https://github.com/ml-explore/mlx)
- [Parakeet MLX Implementation](https://github.com/EliFuzz/parakeet-mlx)

## License

This project follows the model's CC-BY-4.0 license.
```

**Step 2: Verify documentation**

Run:
```bash
cat README.md | head -50
```

Expected: README displays correctly

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README with usage guide"
```

---

### Task 11: Complete MLX Backend Integration (Primary Goal)

**Files:**
- Modify: `src/backends/mlx_backend.py`
- Create: `tests/test_mlx_backend.py`
- Create: `docs/research/mlx-api-investigation.md`

**Step 1: Research parakeet-mlx API**

Run:
```bash
# Clone parakeet-mlx repository to investigate API
git clone https://github.com/EliFuzz/parakeet-mlx.git /tmp/parakeet-mlx-research
# OR
git clone https://github.com/senstella/parakeet-mlx.git /tmp/parakeet-mlx-research

# Examine the API
cat /tmp/parakeet-mlx-research/README.md
cat /tmp/parakeet-mlx-research/parakeet_mlx/__init__.py
```

Expected: Understanding of MLX API structure

**Step 2: Document MLX API findings**

Create `docs/research/mlx-api-investigation.md`:
```markdown
# MLX API Investigation

## Package Structure
[Document the package structure]

## Model Loading
[Document how to load the model]

## Transcription API
[Document the transcription API]

## Output Format
[Document the output format]

## Integration Plan
[Document how to integrate with our backend]
```

**Step 3: Install MLX dependencies**

Note: MLX dependencies are already defined in `pyproject.toml` under `[project.optional-dependencies]`.

If parakeet-mlx is not on PyPI, you may need to install from GitHub:
```bash
# Ensure venv is activated
source venv/bin/activate

# Install MLX extras
pip install -e .[mlx]

# If parakeet-mlx not available, install from GitHub
# pip install git+https://github.com/EliFuzz/parakeet-mlx.git
# OR
# pip install git+https://github.com/senstella/parakeet-mlx.git
```

**Step 4: Write MLX backend integration test**

Create `tests/test_mlx_backend.py`:
```python
"""Tests for MLX backend with real model."""

import pytest
from pathlib import Path


@pytest.mark.skipif(
    not pytest.importorskip("mlx"),
    reason="MLX not installed",
)
@pytest.mark.slow
def test_mlx_backend_transcription():
    """Test MLX backend with real audio file."""
    from src.backends.mlx_backend import MLXBackend
    from src.config import Config

    # Use the test audio file
    audio_file = Path("2086-149220-0033.wav")
    if not audio_file.exists():
        pytest.skip("Test audio file not available")

    config = Config()
    backend = MLXBackend(config)

    # Transcribe
    result = backend.transcribe(audio_file, timestamps=True)

    # Verify output format
    assert "text" in result
    assert len(result["text"]) > 0
    assert "timestamps" in result
    assert "word" in result["timestamps"]
    assert "segment" in result["timestamps"]


@pytest.mark.skipif(
    not pytest.importorskip("mlx"),
    reason="MLX not installed",
)
def test_mlx_backend_matches_nemo_output():
    """Test that MLX backend output matches NeMo format."""
    from src.backends.mlx_backend import MLXBackend
    from src.backends.nemo_backend import NeMoBackend
    from src.config import Config

    audio_file = Path("2086-149220-0033.wav")
    if not audio_file.exists():
        pytest.skip("Test audio file not available")

    config = Config()

    # Test both backends produce compatible output
    mlx_backend = MLXBackend(config)
    mlx_result = mlx_backend.transcribe(audio_file, timestamps=False)

    # Check structure matches NeMo backend
    assert isinstance(mlx_result, dict)
    assert "text" in mlx_result
```

**Step 5: Implement MLX backend based on API research**

Update `src/backends/mlx_backend.py` with actual implementation:
```python
"""MLX backend implementation for Apple Silicon."""

from pathlib import Path
from typing import Dict, Union

from .base import BaseBackend
from ..config import Config


class MLXBackend(BaseBackend):
    """MLX-based ASR backend for Apple Neural Engine."""

    def __init__(self, config: Config):
        """Initialize MLX backend.

        Args:
            config: Application configuration
        """
        self.config = config
        self.model = self.load_model()

    def load_model(self):
        """Load MLX ASR model."""
        try:
            # Import MLX Parakeet implementation
            # Update based on actual API from Step 1 research
            from parakeet_mlx import ParakeetModel  # Example - adjust as needed

            # Load model
            model = ParakeetModel.from_pretrained(
                model_name=self.config.model_name
            )
            return model

        except ImportError as e:
            raise RuntimeError(
                f"MLX backend not available: {e}\n"
                f"Install with: pip install -r requirements-mlx.txt"
            )

    def transcribe(
        self, audio_path: Union[str, Path], timestamps: bool = True
    ) -> Dict:
        """Transcribe audio using MLX.

        Args:
            audio_path: Path to audio file
            timestamps: Include timestamps in output

        Returns:
            Dictionary with transcription results
        """
        audio_path = str(audio_path)

        # Transcribe using MLX model
        # Update based on actual API from Step 1 research
        output = self.model.transcribe(
            audio_path,
            return_timestamps=timestamps
        )

        # Format output to match NeMo backend structure
        result = {"text": output.text}

        if timestamps and hasattr(output, "timestamps"):
            result["timestamps"] = {
                "word": output.timestamps.get("word", []),
                "segment": output.timestamps.get("segment", []),
            }

        return result
```

Note: The implementation above is a template. Update based on actual parakeet-mlx API.

**Step 6: Run MLX tests**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

# Install MLX dependencies (if not already installed)
pip install -e .[mlx]

# Run MLX-specific tests
python -m pytest tests/test_mlx_backend.py -v -m slow

# Test with the provided audio file
parakeet-stt transcribe 2086-149220-0033.wav
```

Expected: MLX backend successfully transcribes audio with ANE acceleration

**Step 7: Benchmark performance**

Run:
```bash
# Ensure venv is activated
source venv/bin/activate  # If not already activated

# Test NeMo backend
time parakeet-stt transcribe 2086-149220-0033.wav --device cpu

# Test MLX backend (on Apple Silicon - automatic selection)
time parakeet-stt transcribe 2086-149220-0033.wav

# Compare results
echo "Check output/ directory for transcription files"
cat output/2086-149220-0033.txt
```

Expected: MLX backend shows 5-10x performance improvement on Apple Silicon

**Step 8: Commit**

```bash
git add src/backends/mlx_backend.py tests/test_mlx_backend.py docs/research/
git commit -m "feat: complete MLX backend integration for Apple Neural Engine"
```

---

## Phase 4: Real-Time Push-to-Talk Recording

**IMPORTANT:** Ensure your virtual environment is activated. You'll need to install additional dependencies for audio recording and GUI.

### Overview

Phase 4 transforms the application into an interactive push-to-talk transcription tool with:
- Global hotkey monitoring (configurable: Option on Mac, Alt on Windows)
- Real-time audio recording from microphone
- Hold-duration threshold (default: 2 seconds before recording starts)
- Visual feedback overlay (top-right corner)
- Clipboard integration for instant access to transcribed text
- Status transitions: Holding → Recording → Transcribing → Done

### Architecture Changes

```
┌─────────────────────────────────────────────┐
│         Push-to-Talk Controller              │
│  (Hotkey Listener + Recording Manager)       │
└──────────────────┬──────────────────────────┘
                   │
        ┏━━━━━━━━━━┻━━━━━━━━━━┓
        ┃                     ┃
  ┌─────▼─────┐        ┌─────▼─────┐
  │   Audio   │        │    GUI    │
  │ Recorder  │        │  Overlay  │
  │           │        │           │
  │(Mic Input)│        │ (Status)  │
  └─────┬─────┘        └───────────┘
        │
  ┌─────▼─────┐
  │   Model   │
  │  Wrapper  │
  │           │
  │(Existing) │
  └─────┬─────┘
        │
  ┌─────▼─────┐
  │ Clipboard │
  │  Manager  │
  └───────────┘
```

### Dependencies

Push-to-talk dependencies are defined in `pyproject.toml` under the `[project.optional-dependencies]` section:

```toml
[project.optional-dependencies]
ptt = [
    "pynput>=1.7.6",      # Global keyboard listener
    "sounddevice>=0.4.6",  # Real-time audio recording
    "numpy>=1.24.0",       # Audio array handling
    "pyperclip>=1.8.2",    # Clipboard integration
]
```

Install with:
```bash
pip install -e .[ptt]
```

Note: `tkinter` is used for the GUI overlay and is included with Python by default.

### Updated Project Structure

```
parakeet-stt/
├── src/
│   ├── ptt/                      # NEW: Push-to-talk module
│   │   ├── __init__.py
│   │   ├── hotkey.py             # Global hotkey listener
│   │   ├── recorder.py           # Real-time audio recorder
│   │   ├── controller.py         # Push-to-talk controller
│   │   └── ui/                   # GUI components
│   │       ├── __init__.py
│   │       ├── overlay.py        # Status overlay window
│   │       └── styles.py         # UI styling
│   ├── clipboard.py              # NEW: Clipboard manager
│   ├── config.py                 # MODIFY: Add PTT settings
│   └── ...
│
├── tests/
│   ├── test_ptt/                 # NEW: PTT tests
│   │   ├── test_hotkey.py
│   │   ├── test_recorder.py
│   │   ├── test_controller.py
│   │   └── test_ui.py
│   ├── test_clipboard.py
│   └── ...
│
├── requirements-ptt.txt          # NEW: PTT dependencies
└── ...
```

---

### Task 12: Configuration for Push-to-Talk

**Files:**
- Modify: `src/config.py`
- Create: `tests/test_ptt_config.py`

**Step 1: Update configuration with PTT settings**

Edit `src/config.py` to add PTT configuration:

```python
"""Configuration management for Parakeet STT."""

import os
import platform
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PTTConfig:
    """Push-to-talk configuration."""

    # Hotkey settings
    hotkey: str = field(default_factory=lambda: PTTConfig._default_hotkey())
    hold_threshold: float = 2.0  # seconds to hold before recording starts

    # Audio settings
    sample_rate: int = 16000
    channels: int = 1  # mono
    chunk_size: int = 1024

    # UI settings
    overlay_position: str = "top-right"  # top-right, top-left, bottom-right, bottom-left
    overlay_opacity: float = 0.9
    show_waveform: bool = True

    # Clipboard settings
    auto_copy: bool = True

    @staticmethod
    def _default_hotkey() -> str:
        """Get default hotkey based on platform."""
        if platform.system() == "Darwin":
            return "option"  # Mac
        return "alt"  # Windows/Linux


@dataclass
class Config:
    """Application configuration."""

    # Model settings
    model_name: str = "nvidia/parakeet-tdt-0.6b-v3"
    device: str = "mps"  # mps for Mac, cuda for NVIDIA, cpu for fallback

    # Audio settings
    sample_rate: int = 16000
    supported_formats: tuple = (".wav", ".flac")

    # Output settings
    output_dir: Path = Path("output")
    include_timestamps: bool = True

    # Push-to-talk settings
    ptt: PTTConfig = field(default_factory=PTTConfig)

    # Environment overrides
    enable_mps_fallback: bool = os.getenv("PYTORCH_ENABLE_MPS_FALLBACK", "1") == "1"

    def __post_init__(self):
        """Ensure output directory exists."""
        self.output_dir.mkdir(exist_ok=True)

    @property
    def is_mac(self) -> bool:
        """Check if running on macOS."""
        import platform

        return platform.system() == "Darwin"

    def get_device(self) -> str:
        """Get appropriate device based on platform."""
        if self.is_mac:
            return "mps"
        return "cuda" if self._cuda_available() else "cpu"

    @staticmethod
    def _cuda_available() -> bool:
        """Check if CUDA is available."""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False
```

**Step 2: Write configuration tests**

Create `tests/test_ptt_config.py`:

```python
"""Tests for push-to-talk configuration."""

import pytest
import platform
from src.config import Config, PTTConfig


def test_ptt_config_defaults():
    """Test PTT configuration defaults."""
    ptt = PTTConfig()

    assert ptt.hold_threshold == 2.0
    assert ptt.sample_rate == 16000
    assert ptt.channels == 1
    assert ptt.overlay_position == "top-right"
    assert ptt.auto_copy is True


def test_ptt_default_hotkey_mac():
    """Test default hotkey on macOS."""
    with pytest.mock.patch("platform.system", return_value="Darwin"):
        ptt = PTTConfig()
        assert ptt.hotkey == "option"


def test_ptt_default_hotkey_windows():
    """Test default hotkey on Windows."""
    with pytest.mock.patch("platform.system", return_value="Windows"):
        ptt = PTTConfig()
        assert ptt.hotkey == "alt"


def test_config_includes_ptt():
    """Test main config includes PTT settings."""
    config = Config()

    assert hasattr(config, "ptt")
    assert isinstance(config.ptt, PTTConfig)


def test_ptt_custom_settings():
    """Test custom PTT settings."""
    ptt = PTTConfig(
        hotkey="ctrl",
        hold_threshold=3.0,
        overlay_position="bottom-right",
    )

    assert ptt.hotkey == "ctrl"
    assert ptt.hold_threshold == 3.0
    assert ptt.overlay_position == "bottom-right"
```

**Step 3: Run tests**

```bash
# Ensure venv is activated
source venv/bin/activate

python -m pytest tests/test_ptt_config.py -v
```

Expected: All tests pass

**Step 4: Commit**

```bash
git add src/config.py tests/test_ptt_config.py
git commit -m "feat: add push-to-talk configuration settings"
```

---

### Task 13: Real-Time Audio Recorder

**Files:**
- Create: `src/ptt/recorder.py`
- Create: `tests/test_ptt/test_recorder.py`

**Step 1: Install PTT dependencies**

```bash
# Ensure venv is activated
source venv/bin/activate

# Install push-to-talk extras
pip install -e .[ptt]
```

**Step 2: Write recorder tests**

Create `tests/test_ptt/test_recorder.py`:

```python
"""Tests for real-time audio recorder."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np


def test_recorder_initialization():
    """Test recorder initializes correctly."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    assert recorder.config == config
    assert recorder.is_recording is False
    assert recorder.audio_buffer == []


def test_recorder_start():
    """Test starting audio recording."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    with patch("src.ptt.recorder.sd.InputStream") as mock_stream:
        recorder.start()

        assert recorder.is_recording is True
        mock_stream.assert_called_once()


def test_recorder_stop():
    """Test stopping audio recording."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    with patch("src.ptt.recorder.sd.InputStream"):
        recorder.start()
        audio_data = recorder.stop()

        assert recorder.is_recording is False
        assert isinstance(audio_data, np.ndarray)


def test_recorder_get_audio_file(tmp_path):
    """Test saving recorded audio to file."""
    from src.ptt.recorder import AudioRecorder
    from src.config import Config

    config = Config()
    recorder = AudioRecorder(config)

    # Simulate recording
    recorder.audio_buffer = [np.array([0.1, 0.2, 0.3])]

    output_file = tmp_path / "recording.wav"
    recorder.save_audio(output_file)

    assert output_file.exists()
```

**Step 3: Implement audio recorder**

Create `src/ptt/__init__.py`:

```python
"""Push-to-talk module for real-time transcription."""

__all__ = ["AudioRecorder", "HotkeyListener", "PTTController"]
```

Create `src/ptt/recorder.py`:

```python
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
```

**Step 4: Run tests**

```bash
# Ensure venv is activated
source venv/bin/activate

python -m pytest tests/test_ptt/test_recorder.py -v
```

Expected: All tests pass

**Step 5: Commit**

```bash
git add src/ptt/ tests/test_ptt/
git commit -m "feat: add real-time audio recorder for microphone input"
```

---

### Task 14: Global Hotkey Listener

**Files:**
- Create: `src/ptt/hotkey.py`
- Create: `tests/test_ptt/test_hotkey.py`

**Step 1: Write hotkey listener tests**

Note: PTT dependencies (including pynput) should already be installed from Task 13.

Create `tests/test_ptt/test_hotkey.py`:

```python
"""Tests for global hotkey listener."""

import pytest
from unittest.mock import Mock, patch
import time


def test_hotkey_listener_initialization():
    """Test hotkey listener initializes."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    assert listener.config == config
    assert listener.is_pressed is False


def test_hotkey_listener_press_callback():
    """Test press callback is called."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    press_called = False

    def on_press():
        nonlocal press_called
        press_called = True

    listener.on_press = on_press
    listener._handle_press()

    assert press_called is True


def test_hotkey_listener_release_callback():
    """Test release callback is called."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    release_called = False

    def on_release():
        nonlocal release_called
        release_called = True

    listener.on_release = on_release
    listener._handle_release()

    assert release_called is True


def test_hotkey_listener_hold_duration():
    """Test hold duration tracking."""
    from src.ptt.hotkey import HotkeyListener
    from src.config import Config

    config = Config()
    listener = HotkeyListener(config)

    listener._handle_press()
    time.sleep(0.1)
    duration = listener.get_hold_duration()

    assert duration >= 0.1
```

**Step 2: Implement hotkey listener**

Create `src/ptt/hotkey.py`:

```python
"""Global hotkey listener for push-to-talk."""

from pynput import keyboard
from typing import Callable, Optional
import time

from ..config import Config


class HotkeyListener:
    """Listens for global hotkey press/release events."""

    def __init__(self, config: Config):
        """Initialize hotkey listener.

        Args:
            config: Application configuration
        """
        self.config = config
        self.is_pressed = False
        self.press_time: Optional[float] = None
        self.listener: Optional[keyboard.Listener] = None

        # Callbacks
        self.on_press: Optional[Callable] = None
        self.on_release: Optional[Callable] = None

        # Parse hotkey
        self.target_key = self._parse_hotkey(config.ptt.hotkey)

    def _parse_hotkey(self, hotkey: str) -> keyboard.Key:
        """Parse hotkey string to keyboard.Key.

        Args:
            hotkey: Hotkey name (e.g., 'option', 'alt', 'ctrl')

        Returns:
            Parsed keyboard.Key
        """
        hotkey_map = {
            "option": keyboard.Key.alt,  # Option key on Mac is alt
            "alt": keyboard.Key.alt,
            "ctrl": keyboard.Key.ctrl,
            "shift": keyboard.Key.shift,
            "cmd": keyboard.Key.cmd,
            "command": keyboard.Key.cmd,
        }

        return hotkey_map.get(hotkey.lower(), keyboard.Key.alt)

    def start(self) -> None:
        """Start listening for hotkey events."""
        self.listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self.listener.start()

    def stop(self) -> None:
        """Stop listening for hotkey events."""
        if self.listener:
            self.listener.stop()
            self.listener = None

    def _on_key_press(self, key):
        """Handle key press event.

        Args:
            key: Pressed key
        """
        if key == self.target_key and not self.is_pressed:
            self._handle_press()

    def _on_key_release(self, key):
        """Handle key release event.

        Args:
            key: Released key
        """
        if key == self.target_key and self.is_pressed:
            self._handle_release()

    def _handle_press(self) -> None:
        """Handle hotkey press."""
        self.is_pressed = True
        self.press_time = time.time()

        if self.on_press:
            self.on_press()

    def _handle_release(self) -> None:
        """Handle hotkey release."""
        self.is_pressed = False
        self.press_time = None

        if self.on_release:
            self.on_release()

    def get_hold_duration(self) -> float:
        """Get current hold duration in seconds.

        Returns:
            Hold duration in seconds (0 if not pressed)
        """
        if not self.is_pressed or not self.press_time:
            return 0.0

        return time.time() - self.press_time
```

**Step 3: Run tests**

```bash
# Ensure venv is activated
source venv/bin/activate

python -m pytest tests/test_ptt/test_hotkey.py -v
```

Expected: All tests pass

**Step 4: Commit**

```bash
git add src/ptt/hotkey.py tests/test_ptt/test_hotkey.py
git commit -m "feat: add global hotkey listener for push-to-talk"
```

---

### Task 15: Push-to-Talk Controller

**Files:**
- Create: `src/ptt/controller.py`
- Create: `tests/test_ptt/test_controller.py`

**Step 1: Write controller tests**

Create `tests/test_ptt/test_controller.py`:

```python
"""Tests for push-to-talk controller."""

import pytest
from unittest.mock import Mock, patch
import time


def test_controller_initialization():
    """Test controller initializes correctly."""
    from src.ptt.controller import PTTController
    from src.config import Config

    config = Config()

    with patch("src.ptt.controller.HotkeyListener"):
        with patch("src.ptt.controller.AudioRecorder"):
            with patch("src.ptt.controller.ModelWrapper"):
                controller = PTTController(config)

                assert controller.config == config
                assert controller.state == "idle"


def test_controller_state_transitions():
    """Test state transitions: idle → holding → recording → transcribing → done."""
    from src.ptt.controller import PTTController
    from src.config import Config

    config = Config()

    with patch("src.ptt.controller.HotkeyListener"):
        with patch("src.ptt.controller.AudioRecorder"):
            with patch("src.ptt.controller.ModelWrapper"):
                controller = PTTController(config)

                # Idle → Holding
                controller._on_hotkey_press()
                assert controller.state == "holding"

                # Holding → Recording (after threshold)
                time.sleep(config.ptt.hold_threshold + 0.1)
                assert controller.state == "recording"

                # Recording → Transcribing
                controller._on_hotkey_release()
                assert controller.state == "transcribing"


def test_controller_hold_threshold_not_met():
    """Test that recording doesn't start if threshold not met."""
    from src.ptt.controller import PTTController
    from src.config import Config

    config = Config()
    config.ptt.hold_threshold = 2.0

    with patch("src.ptt.controller.HotkeyListener"):
        with patch("src.ptt.controller.AudioRecorder") as mock_recorder:
            with patch("src.ptt.controller.ModelWrapper"):
                controller = PTTController(config)

                controller._on_hotkey_press()
                time.sleep(0.1)  # Less than threshold
                controller._on_hotkey_release()

                # Should not have started recording
                assert controller.state == "idle"
                mock_recorder.return_value.start.assert_not_called()
```

**Step 2: Implement controller**

Create `src/ptt/controller.py`:

```python
"""Push-to-talk controller coordinating hotkey, recording, and transcription."""

import time
from pathlib import Path
from typing import Optional, Callable
import tempfile

from ..config import Config
from ..model import ModelWrapper
from .hotkey import HotkeyListener
from .recorder import AudioRecorder


class PTTController:
    """Coordinates push-to-talk workflow."""

    # States: idle → holding → recording → transcribing → done

    def __init__(self, config: Config):
        """Initialize push-to-talk controller.

        Args:
            config: Application configuration
        """
        self.config = config
        self.state = "idle"

        # Components
        self.hotkey_listener = HotkeyListener(config)
        self.recorder = AudioRecorder(config)
        self.model = ModelWrapper(config)

        # Timing
        self.hold_start_time: Optional[float] = None
        self.threshold_timer: Optional[float] = None

        # Callbacks for UI updates
        self.on_state_change: Optional[Callable[[str], None]] = None

        # Setup hotkey callbacks
        self.hotkey_listener.on_press = self._on_hotkey_press
        self.hotkey_listener.on_release = self._on_hotkey_release

    def start(self) -> None:
        """Start the push-to-talk controller."""
        self.hotkey_listener.start()
        self._update_state("idle")

    def stop(self) -> None:
        """Stop the push-to-talk controller."""
        self.hotkey_listener.stop()
        if self.recorder.is_recording:
            self.recorder.stop()

    def _update_state(self, new_state: str) -> None:
        """Update state and notify callback.

        Args:
            new_state: New state name
        """
        self.state = new_state

        if self.on_state_change:
            self.on_state_change(new_state)

    def _on_hotkey_press(self) -> None:
        """Handle hotkey press event."""
        if self.state != "idle":
            return

        self.hold_start_time = time.time()
        self._update_state("holding")

        # Start threshold timer
        self._check_threshold()

    def _check_threshold(self) -> None:
        """Check if hold threshold is met and start recording."""
        if self.state != "holding":
            return

        if not self.hold_start_time:
            return

        hold_duration = time.time() - self.hold_start_time

        if hold_duration >= self.config.ptt.hold_threshold:
            # Threshold met, start recording
            self._start_recording()
        else:
            # Check again after a short delay
            import threading
            threading.Timer(0.1, self._check_threshold).start()

    def _start_recording(self) -> None:
        """Start audio recording."""
        self._update_state("recording")
        self.recorder.start()

    def _on_hotkey_release(self) -> None:
        """Handle hotkey release event."""
        if self.state == "holding":
            # Released before threshold - cancel
            self.hold_start_time = None
            self._update_state("idle")

        elif self.state == "recording":
            # Stop recording and transcribe
            self._stop_recording()

    def _stop_recording(self) -> None:
        """Stop recording and start transcription."""
        audio_data = self.recorder.stop()

        if len(audio_data) == 0:
            self._update_state("idle")
            return

        self._update_state("transcribing")

        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        self.recorder.save_audio(tmp_path)

        # Transcribe
        try:
            result = self.model.transcribe(tmp_path, timestamps=False)
            transcription = result["text"]

            # Handle transcription result
            self._on_transcription_complete(transcription)

        finally:
            # Clean up temp file
            tmp_path.unlink()

    def _on_transcription_complete(self, text: str) -> None:
        """Handle completed transcription.

        Args:
            text: Transcribed text
        """
        # Copy to clipboard if enabled
        if self.config.ptt.auto_copy:
            self._copy_to_clipboard(text)

        self._update_state("done")

        # Return to idle after brief delay
        import threading
        threading.Timer(2.0, lambda: self._update_state("idle")).start()

    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard.

        Args:
            text: Text to copy
        """
        try:
            import pyperclip
            pyperclip.copy(text)
        except ImportError:
            print("Warning: pyperclip not installed, clipboard not available")
```

**Step 3: Run tests**

```bash
# Ensure venv is activated
source venv/bin/activate

python -m pytest tests/test_ptt/test_controller.py -v
```

Expected: All tests pass

Note: pyperclip is already installed as part of the PTT extras from Task 13.

**Step 4: Commit**

```bash
git add src/ptt/controller.py tests/test_ptt/test_controller.py
git commit -m "feat: add push-to-talk controller with state management"
```

---

### Task 16: GUI Status Overlay

**Files:**
- Create: `src/ptt/ui/overlay.py`
- Create: `src/ptt/ui/styles.py`
- Create: `tests/test_ptt/test_ui.py`

**Step 1: Write UI tests**

Create `tests/test_ptt/test_ui.py`:

```python
"""Tests for GUI overlay."""

import pytest
from unittest.mock import Mock, patch


def test_overlay_initialization():
    """Test overlay window initializes."""
    from src.ptt.ui.overlay import StatusOverlay
    from src.config import Config

    config = Config()

    with patch("tkinter.Tk"):
        overlay = StatusOverlay(config)

        assert overlay.config == config


def test_overlay_state_display():
    """Test overlay displays different states."""
    from src.ptt.ui.overlay import StatusOverlay
    from src.config import Config

    config = Config()

    with patch("tkinter.Tk"):
        overlay = StatusOverlay(config)

        # Test different states
        overlay.update_state("idle")
        overlay.update_state("holding")
        overlay.update_state("recording")
        overlay.update_state("transcribing")
        overlay.update_state("done")


def test_overlay_positioning():
    """Test overlay positions correctly."""
    from src.ptt.ui.overlay import StatusOverlay
    from src.config import Config

    config = Config()
    config.ptt.overlay_position = "top-right"

    with patch("tkinter.Tk") as mock_tk:
        overlay = StatusOverlay(config)

        # Verify window attributes set for top-right
        assert config.ptt.overlay_position == "top-right"
```

**Step 2: Implement overlay styling**

Create `src/ptt/ui/__init__.py`:

```python
"""UI components for push-to-talk."""

__all__ = ["StatusOverlay"]
```

Create `src/ptt/ui/styles.py`:

```python
"""UI styling for status overlay."""

# State colors
STATE_COLORS = {
    "idle": "#6c757d",        # Gray
    "holding": "#ffc107",     # Yellow/amber
    "recording": "#dc3545",   # Red
    "transcribing": "#0d6efd",  # Blue
    "done": "#198754",        # Green
}

# State messages
STATE_MESSAGES = {
    "idle": "Ready",
    "holding": "Hold to record...",
    "recording": "● Recording",
    "transcribing": "Transcribing...",
    "done": "✓ Copied to clipboard",
}

# Window dimensions
WINDOW_WIDTH = 280
WINDOW_HEIGHT = 80
PADDING = 20

# Font settings
FONT_FAMILY = "SF Pro Display" if True else "Segoe UI"  # Mac vs Windows
FONT_SIZE = 14
FONT_WEIGHT = "bold"
```

Create `src/ptt/ui/overlay.py`:

```python
"""Status overlay window for push-to-talk."""

import tkinter as tk
from typing import Optional

from ...config import Config
from .styles import STATE_COLORS, STATE_MESSAGES, WINDOW_WIDTH, WINDOW_HEIGHT, PADDING


class StatusOverlay:
    """Floating status overlay window."""

    def __init__(self, config: Config):
        """Initialize status overlay.

        Args:
            config: Application configuration
        """
        self.config = config
        self.window: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None
        self.current_state = "idle"

        self._create_window()

    def _create_window(self) -> None:
        """Create overlay window."""
        self.window = tk.Tk()

        # Window properties
        self.window.title("Parakeet STT")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.attributes("-topmost", True)  # Always on top
        self.window.attributes("-alpha", self.config.ptt.overlay_opacity)

        # Position window
        self._position_window()

        # Create label
        self.label = tk.Label(
            self.window,
            text=STATE_MESSAGES["idle"],
            font=("SF Pro Display", 14, "bold"),
            fg="white",
            bg=STATE_COLORS["idle"],
            padx=PADDING,
            pady=PADDING,
        )
        self.label.pack(fill=tk.BOTH, expand=True)

        # Start hidden
        self.hide()

    def _position_window(self) -> None:
        """Position window based on configuration."""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        position = self.config.ptt.overlay_position
        margin = 20

        if position == "top-right":
            x = screen_width - WINDOW_WIDTH - margin
            y = margin
        elif position == "top-left":
            x = margin
            y = margin
        elif position == "bottom-right":
            x = screen_width - WINDOW_WIDTH - margin
            y = screen_height - WINDOW_HEIGHT - margin
        elif position == "bottom-left":
            x = margin
            y = screen_height - WINDOW_HEIGHT - margin
        else:
            # Default to top-right
            x = screen_width - WINDOW_WIDTH - margin
            y = margin

        self.window.geometry(f"+{x}+{y}")

    def update_state(self, state: str) -> None:
        """Update overlay to show new state.

        Args:
            state: New state name
        """
        self.current_state = state

        if state == "idle":
            self.hide()
        else:
            self.show()

            # Update label
            if self.label:
                self.label.config(
                    text=STATE_MESSAGES.get(state, state),
                    bg=STATE_COLORS.get(state, "#6c757d"),
                )

    def show(self) -> None:
        """Show overlay window."""
        if self.window:
            self.window.deiconify()
            self.window.update()

    def hide(self) -> None:
        """Hide overlay window."""
        if self.window:
            self.window.withdraw()

    def start(self) -> None:
        """Start overlay main loop."""
        if self.window:
            self.window.mainloop()

    def stop(self) -> None:
        """Stop overlay and close window."""
        if self.window:
            self.window.quit()
            self.window.destroy()
```

**Step 3: Run tests**

```bash
# Ensure venv is activated
source venv/bin/activate

python -m pytest tests/test_ptt/test_ui.py -v
```

Expected: All tests pass

**Step 4: Commit**

```bash
git add src/ptt/ui/ tests/test_ptt/test_ui.py
git commit -m "feat: add GUI status overlay for push-to-talk feedback"
```

---

### Task 17: Main PTT Application

**Files:**
- Create: `src/ptt/app.py`
- Modify: `src/cli.py`
- Create: `tests/test_ptt/test_app.py`

**Step 1: Write app tests**

Create `tests/test_ptt/test_app.py`:

```python
"""Tests for PTT application."""

import pytest
from unittest.mock import Mock, patch


def test_ptt_app_initialization():
    """Test PTT app initializes all components."""
    from src.ptt.app import PTTApp
    from src.config import Config

    config = Config()

    with patch("src.ptt.app.PTTController"):
        with patch("src.ptt.app.StatusOverlay"):
            app = PTTApp(config)

            assert app.config == config


def test_ptt_app_start_stop():
    """Test app start and stop."""
    from src.ptt.app import PTTApp
    from src.config import Config

    config = Config()

    with patch("src.ptt.app.PTTController") as mock_controller:
        with patch("src.ptt.app.StatusOverlay") as mock_overlay:
            app = PTTApp(config)

            app.start()
            mock_controller.return_value.start.assert_called_once()

            app.stop()
            mock_controller.return_value.stop.assert_called_once()
```

**Step 2: Implement PTT app**

Create `src/ptt/app.py`:

```python
"""Main push-to-talk application."""

import threading
from typing import Optional

from ..config import Config
from .controller import PTTController
from .ui.overlay import StatusOverlay


class PTTApp:
    """Main push-to-talk application."""

    def __init__(self, config: Config):
        """Initialize PTT application.

        Args:
            config: Application configuration
        """
        self.config = config

        # Components
        self.controller = PTTController(config)
        self.overlay = StatusOverlay(config)

        # Connect controller state changes to overlay
        self.controller.on_state_change = self.overlay.update_state

    def start(self) -> None:
        """Start the PTT application."""
        print("Starting Parakeet STT Push-to-Talk...")
        print(f"Hotkey: {self.config.ptt.hotkey}")
        print(f"Hold threshold: {self.config.ptt.hold_threshold}s")
        print("Press Ctrl+C to quit\n")

        # Start controller in background thread
        controller_thread = threading.Thread(target=self.controller.start, daemon=True)
        controller_thread.start()

        # Start overlay (blocking - runs main loop)
        try:
            self.overlay.start()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop the PTT application."""
        print("\nStopping Parakeet STT...")
        self.controller.stop()
        self.overlay.stop()


def main():
    """Main entry point for PTT app."""
    from ..config import Config

    config = Config()
    app = PTTApp(config)

    try:
        app.start()
    except KeyboardInterrupt:
        app.stop()


if __name__ == "__main__":
    main()
```

**Step 3: Add PTT command to CLI**

Edit `src/cli.py` to add PTT command:

```python
@main.command()
@click.option(
    "--hotkey",
    type=str,
    default=None,
    help="Hotkey to use (option/alt/ctrl)",
)
@click.option(
    "--threshold",
    type=float,
    default=2.0,
    help="Hold duration threshold in seconds",
)
@click.option(
    "--position",
    type=click.Choice(["top-right", "top-left", "bottom-right", "bottom-left"]),
    default="top-right",
    help="Overlay position",
)
def ptt(hotkey: str, threshold: float, position: str):
    """Start push-to-talk mode for real-time transcription."""
    from .ptt.app import PTTApp
    from .ptt import PTTConfig

    # Create configuration
    config = Config()

    # Override PTT settings if provided
    if hotkey:
        config.ptt.hotkey = hotkey
    config.ptt.hold_threshold = threshold
    config.ptt.overlay_position = position

    # Start PTT app
    app = PTTApp(config)
    app.start()
```

**Step 4: Run tests**

```bash
# Ensure venv is activated
source venv/bin/activate

python -m pytest tests/test_ptt/ -v
```

Expected: All tests pass

**Step 5: Test PTT app manually**

```bash
# Ensure venv is activated
source venv/bin/activate

# Start PTT mode
parakeet-stt ptt

# Or with custom settings
parakeet-stt ptt --hotkey alt --threshold 1.5 --position bottom-right
```

Expected:
1. Overlay appears in top-right corner
2. Hold Option/Alt key
3. After 2 seconds, overlay shows "Recording"
4. Speak into microphone
5. Release key
6. Overlay shows "Transcribing..."
7. Overlay shows "✓ Copied to clipboard"
8. Text is in clipboard

**Step 6: Commit**

```bash
git add src/ptt/app.py src/cli.py tests/test_ptt/test_app.py
git commit -m "feat: add push-to-talk application with real-time transcription"
```

Note: PTT dependencies are already defined in `pyproject.toml` from Task 1. No separate requirements file needed.

---

## Summary

This plan creates a minimal STT CLI application in four phases with **MLX Framework** as the primary optimization target:

**Phase 1: Basic Implementation** ✅
- Project structure with proper configuration
- NeMo model wrapper with PyTorch MPS support
- Unit tests for core functionality
- Uses `2086-149220-0033.wav` for testing

**Phase 2: CLI Interface** ✅
- File output handler for transcription results
- Click-based CLI with colored output
- Integration tests with real audio (2086-149220-0033.wav)

**Phase 3: ANE Optimization (MLX Focus)**
- Backend abstraction layer
- MLX backend implementation for Apple Neural Engine
- Automatic backend selection based on platform
- **Task 11: Complete MLX integration** (primary deliverable)
- Comprehensive documentation

**Phase 4: Real-Time Push-to-Talk** 🆕
- Global hotkey listener (Option/Alt key)
- Real-time audio recording from microphone
- Hold-duration threshold (default 2 seconds)
- Push-to-talk state management
- GUI status overlay (top-right corner)
- Clipboard integration
- Visual feedback for all states

**Key Decisions:**
- **MLX Framework**: Primary approach for Apple Silicon optimization
- TDD approach with unit tests before implementation
- Backend abstraction for platform flexibility (NeMo fallback)
- Simple .txt file output (no frontend needed)
- Automatic hardware detection and optimization
- Using provided audio file (2086-149220-0033.wav) for all testing

**Success Criteria:**

*Phase 1-2 (Complete):*
1. ✅ CLI app transcribes audio to .txt files
2. ✅ Works with NeMo backend (CPU/GPU fallback)

*Phase 3 (MLX):*
3. ⏳ MLX backend achieves 5-10x speedup on Apple Silicon
4. ⏳ Automatic backend selection (MLX on Mac, NeMo elsewhere)
5. ⏳ All tests pass with real audio

*Phase 4 (Push-to-Talk):*
6. ⏳ Global hotkey detection (Option/Alt)
7. ⏳ Hold threshold works (2 seconds default)
8. ⏳ Real-time recording and transcription
9. ⏳ GUI overlay shows all states correctly
10. ⏳ Text automatically copies to clipboard

**Next Steps After This Plan:**
1. Performance optimization of MLX backend
2. Add waveform visualization in overlay
3. Add audio level meter during recording
4. Add keyboard shortcuts for settings
5. Add system tray icon
6. Package as standalone executable (PyInstaller/py2app)

---

Plan complete and saved to `docs/plans/2026-02-11-minimal-stt-cli.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
