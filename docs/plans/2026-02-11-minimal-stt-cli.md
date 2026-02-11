# Minimal STT CLI Application Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a minimal CLI application that transcribes audio files using Parakeet TDT 0.6B and outputs results to .txt files, with Apple Neural Engine optimization for Mac.

**Architecture:** Three-phase approach: (1) Basic NeMo implementation with PyTorch MPS backend for Apple Silicon, (2) CLI interface with file I/O, (3) ANE optimization via **MLX framework** (primary approach). Focus on simplicity and testability.

**Tech Stack:** Python 3.10+, NeMo Toolkit 2.2, PyTorch 2.0+, **MLX (Apple Silicon - Primary)**, pytest, click (CLI)

**Test Audio:** Using `2086-149220-0033.wav` in project root for integration testing.

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
│   └── backends/                # Backend implementations
│       ├── __init__.py          # Backend package initialization
│       ├── base.py              # Abstract base backend
│       ├── nemo_backend.py      # NeMo/PyTorch backend
│       ├── mlx_backend.py       # MLX/ANE backend (Apple Silicon)
│       └── factory.py           # Automatic backend selection
│
├── tests/                       # Test suite
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Pytest fixtures and configuration
│   ├── test_config.py           # Configuration tests
│   ├── test_model.py            # Model wrapper tests
│   ├── test_output.py           # Output handler tests
│   ├── test_cli.py              # CLI tests
│   ├── test_backends.py         # Backend abstraction tests
│   ├── test_backend_factory.py  # Backend factory tests
│   ├── test_mlx_backend.py      # MLX backend integration tests
│   ├── test_integration.py      # End-to-end integration tests
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
├── 2086-149220-0033.wav         # Test audio file (provided)
│
├── requirements.txt             # Core dependencies (NeMo, PyTorch, Click)
├── requirements-mlx.txt         # MLX dependencies for Apple Silicon
├── pyproject.toml               # Project configuration and metadata
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

Create `requirements.txt`:
```txt
# Core dependencies
nemo-toolkit[asr]>=2.2.0
torch>=2.0.0
torchaudio>=2.0.0

# CLI and utilities
click>=8.1.0
colorama>=0.4.6
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Development
black>=23.0.0
ruff>=0.1.0
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
    "click>=8.1.0",
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

**Step 5: Verify project structure**

Run:
```bash
ls -la
cat requirements.txt
cat pyproject.toml
```

Expected: Files created with correct content

**Step 6: Commit**

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
    model_name: str = "nvidia/parakeet-tdt-0.6b-v2"
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

    assert config.model_name == "nvidia/parakeet-tdt-0.6b-v2"
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
python -m pytest tests/test_cli.py -v
```

Expected: All tests pass

**Step 5: Test CLI manually (optional dry run)**

Run:
```bash
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
- Create: `requirements-mlx.txt`

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

**Step 2: Create MLX requirements**

Create `requirements-mlx.txt`:
```txt
# MLX dependencies for Apple Silicon
mlx>=0.20.0
parakeet-mlx>=0.1.0  # May need to install from GitHub

# Optional audio processing
librosa>=0.10.0
soundfile>=0.12.0
```

**Step 3: Implement base backend**

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

**Step 4: Refactor NeMo backend**

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

**Step 5: Implement MLX backend stub**

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
        2. Initialize with model_name="nvidia/parakeet-tdt-0.6b-v2"
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

**Step 6: Run tests**

Run:
```bash
python -m pytest tests/test_backends.py -v
```

Expected: Tests pass (MLX tests skipped if not installed)

**Step 7: Commit**

```bash
git add src/backends/ tests/test_backends.py requirements-mlx.txt
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

# Install dependencies
pip install -r requirements.txt
```

### Apple Silicon Installation (MLX backend)

```bash
# Install with MLX support for Apple Neural Engine
pip install -r requirements.txt
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

### Run Tests

```bash
# Run all tests
pytest

# Run without slow tests
pytest -m "not slow"

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
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

- **Model:** nvidia/parakeet-tdt-0.6b-v2
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

- [Parakeet TDT Model](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2)
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
- Modify: `requirements-mlx.txt`
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

**Step 3: Update MLX requirements with correct package**

Update `requirements-mlx.txt`:
```txt
# MLX dependencies for Apple Silicon
mlx>=0.20.0

# Install parakeet-mlx from GitHub (if not on PyPI)
# git+https://github.com/EliFuzz/parakeet-mlx.git
# OR
# git+https://github.com/senstella/parakeet-mlx.git

# Audio processing
librosa>=0.10.0
soundfile>=0.12.0
numpy>=1.24.0
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
# Install MLX dependencies
pip install -r requirements-mlx.txt

# Run MLX-specific tests
python -m pytest tests/test_mlx_backend.py -v -m slow

# Test with the provided audio file (ensure PYTHONPATH is set)
export PYTHONPATH="${PYTHONPATH}:."
python -m src.cli transcribe 2086-149220-0033.wav

# Or use the installed command
parakeet-stt transcribe 2086-149220-0033.wav
```

Expected: MLX backend successfully transcribes audio with ANE acceleration

**Step 7: Benchmark performance**

Run:
```bash
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
git add src/backends/mlx_backend.py requirements-mlx.txt tests/test_mlx_backend.py docs/research/
git commit -m "feat: complete MLX backend integration for Apple Neural Engine"
```

---

## Summary

This plan creates a minimal STT CLI application in three phases with **MLX Framework** as the primary optimization target:

**Phase 1: Basic Implementation**
- Project structure with proper configuration
- NeMo model wrapper with PyTorch MPS support
- Unit tests for core functionality
- Uses `2086-149220-0033.wav` for testing

**Phase 2: CLI Interface**
- File output handler for transcription results
- Click-based CLI with colored output
- Integration tests with real audio (2086-149220-0033.wav)

**Phase 3: ANE Optimization (MLX Focus)**
- Backend abstraction layer
- MLX backend implementation for Apple Neural Engine
- Automatic backend selection based on platform
- **Task 11: Complete MLX integration** (primary deliverable)
- Comprehensive documentation

**Key Decisions:**
- **MLX Framework**: Primary approach for Apple Silicon optimization
- TDD approach with unit tests before implementation
- Backend abstraction for platform flexibility (NeMo fallback)
- Simple .txt file output (no frontend needed)
- Automatic hardware detection and optimization
- Using provided audio file (2086-149220-0033.wav) for all testing

**Success Criteria:**
1. ✅ CLI app transcribes audio to .txt files
2. ✅ Works with NeMo backend (CPU/GPU fallback)
3. ✅ MLX backend achieves 5-10x speedup on Apple Silicon
4. ✅ Automatic backend selection (MLX on Mac, NeMo elsewhere)
5. ✅ All tests pass with real audio

**Next Steps After This Plan:**
1. Performance optimization of MLX backend
2. Add batch processing for multiple files
3. Add real-time audio streaming support
4. Cross-platform testing (Mac/Linux/Windows)
5. Package as standalone executable

---

Plan complete and saved to `docs/plans/2026-02-11-minimal-stt-cli.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
