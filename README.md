# Parakeet STT

Minimal speech-to-text CLI application using NVIDIA's Parakeet TDT 0.6B model, optimized for Apple Neural Engine on Mac.

## Features

- 🎯 Simple CLI interface
- 🚀 Automatic hardware optimization (ANE/GPU/CPU)
- 📝 Text file output with timestamps
- 🍎 Native Apple Silicon support via MLX
- 🎮 NVIDIA GPU support via CUDA
- 💻 CPU fallback for compatibility
- 🎙️ fn-key push-to-talk — hold fn to dictate, releases paste into any text field

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

### fn-key Push-to-Talk

Loads the model once in the background. Hold **fn** for ≥0.5s to record, release to transcribe and paste into the active text field.

#### macOS Permissions (one-time setup)

Go to **System Settings → Privacy & Security** and add your terminal app to:
- **Input Monitoring** — required for fn key detection
- **Microphone** — required for audio recording

#### Commands

```bash
# Start the daemon
parakeet-stt fn-ptt start

# Check status
parakeet-stt fn-ptt status

# Stop the daemon
parakeet-stt fn-ptt stop
```

#### How it works

1. `fn-ptt start` loads the model in the background (~10–30s on first run)
2. Click into any text field
3. Hold **fn** for at least 0.5 seconds and speak
4. Release **fn** — transcription appears in the text field within ~1–2s
5. Repeat as many times as needed without reloading the model

Logs are written to `~/.parakeet-stt/fn-ptt.log` if anything goes wrong.

### Background Daemon

```bash
# Start daemon
parakeet-stt daemon start

# Check status
parakeet-stt daemon status

# Stop daemon
parakeet-stt daemon stop

# Control recording
parakeet-stt record        # toggle
parakeet-stt record start
parakeet-stt record stop
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
│   │   ├── base.py         # Abstract backend interface
│   │   ├── nemo_backend.py # NeMo/PyTorch backend
│   │   ├── mlx_backend.py  # MLX/ANE backend
│   │   └── factory.py      # Automatic backend selection
│   ├── daemon/         # Background daemon service
│   ├── fn_ptt/         # fn-key push-to-talk
│   │   ├── app.py          # Event tap, recording, transcription, paste
│   │   ├── manager.py      # Process lifecycle (PID-based)
│   │   └── run.py          # Subprocess entry point
│   ├── cli.py          # CLI application
│   ├── config.py       # Configuration management
│   ├── model.py        # Model wrapper
│   └── output.py       # Output formatting
└── tests/              # Test suite
```

## Model Information

- **Model:** nvidia/parakeet-tdt-0.6b-v3
- **Parameters:** 600 million
- **Architecture:** FastConformer-TDT
- **Word Error Rate:** 6.05% average
- **License:** CC-BY-4.0

## Troubleshooting

### fn-ptt: Could not create event tap

Grant **Input Monitoring** permission to your terminal app:
System Settings → Privacy & Security → Input Monitoring

### fn-ptt: No audio recorded

Grant **Microphone** permission to your terminal app:
System Settings → Privacy & Security → Microphone

### fn-ptt: Check the log

```bash
tail -f ~/.parakeet-stt/fn-ptt.log
```

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
