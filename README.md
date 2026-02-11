# Parakeet STT

> **Status:** 🚧 In Development - Implementation planning phase

A minimal, locally-run speech-to-text CLI application using NVIDIA's Parakeet TDT 0.6B model, optimized for Apple Neural Engine on Mac with fallback support for NVIDIA CUDA GPUs and CPU.

## 🎯 Project Goals

- **Local-first:** All processing happens on your machine - no cloud dependencies
- **Apple Silicon optimized:** Native ANE acceleration via MLX framework (10x faster)
- **Cross-platform:** Mac (ANE), Windows/Linux (CUDA GPU), CPU fallback
- **Simple CLI:** Easy-to-use command-line interface
- **Accurate:** 6.05% WER using NVIDIA's Parakeet TDT 0.6B model

## ✨ Features

- 🎤 High-accuracy speech recognition (600M parameter model)
- 🍎 **Apple Neural Engine optimization** via MLX framework
- 🎮 NVIDIA GPU acceleration via CUDA
- 💻 CPU fallback for universal compatibility
- 📝 Text file output with optional word/segment timestamps
- 🚀 Real-time performance on Apple Silicon
- 🎯 Supports WAV and FLAC audio formats (16kHz recommended)

## 🏗️ Architecture

```
parakeet-stt/
├── src/                    # Main application package
│   ├── backends/           # Platform-specific implementations
│   │   ├── nemo_backend.py # NeMo/PyTorch (CUDA/CPU)
│   │   ├── mlx_backend.py  # MLX (Apple Neural Engine)
│   │   └── factory.py      # Automatic backend selection
│   ├── config.py           # Configuration management
│   ├── model.py            # Model wrapper
│   ├── output.py           # Output formatting
│   └── cli.py              # CLI interface
├── tests/                  # Test suite
├── docs/                   # Documentation and research
└── output/                 # Transcription outputs
```

## 🛠️ Technology Stack

- **Model:** [nvidia/parakeet-tdt-0.6b-v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) (FastConformer-TDT)
- **Frameworks:**
  - [NeMo Toolkit](https://github.com/NVIDIA/NeMo) for baseline implementation
  - [MLX](https://github.com/ml-explore/mlx) for Apple Silicon optimization
  - PyTorch 2.0+ with MPS/CUDA support
- **CLI:** Click framework
- **Testing:** pytest with coverage

## 🚀 Planned Usage

```bash
# Basic transcription
parakeet-stt transcribe audio.wav

# With custom output directory
parakeet-stt transcribe audio.wav --output-dir results/

# Without timestamps
parakeet-stt transcribe audio.wav --no-timestamps

# Force specific device
parakeet-stt transcribe audio.wav --device cpu
```

### Output Format

Transcriptions are saved as `.txt` files:

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

## 🎛️ Hardware Acceleration

| Platform | Backend | Hardware | Expected Performance |
|----------|---------|----------|---------------------|
| Mac (Apple Silicon) | MLX | Apple Neural Engine | **10x faster** |
| Mac (Intel) | NeMo | CPU/MPS GPU | Baseline |
| Linux/Windows (NVIDIA) | NeMo | CUDA GPU | 3-5x faster |
| Other | NeMo | CPU | Baseline |

## 📋 Development Roadmap

- [x] Research Apple Neural Engine optimization approaches
- [x] Create implementation plan with MLX framework
- [x] Define project structure and architecture
- [ ] **Phase 1:** Basic NeMo implementation with PyTorch MPS
- [ ] **Phase 2:** CLI interface with file I/O
- [ ] **Phase 3:** MLX backend integration for ANE acceleration
- [ ] Performance benchmarking across backends
- [ ] Batch processing support
- [ ] Real-time audio streaming

## 📚 Documentation

- **Model Info:** [docs/knowledge/parakeet-tdt-model.md](docs/knowledge/parakeet-tdt-model.md)
- **Implementation Plan:** [docs/plans/2026-02-11-minimal-stt-cli.md](docs/plans/2026-02-11-minimal-stt-cli.md)
- **MLX Research:** [docs/research/mlx-integration.md](docs/research/mlx-integration.md)

## 🔬 Model Information

- **Model:** nvidia/parakeet-tdt-0.6b-v2
- **Parameters:** 600 million
- **Architecture:** FastConformer-TDT with full attention
- **Word Error Rate:** 6.05% average across benchmarks
- **RTFx:** 3380 on HF-Open-ASR leaderboard
- **License:** CC-BY-4.0

## 🌟 MLX Framework Integration

This project prioritizes the **MLX Framework** for Apple Silicon optimization:

- **Direct ANE Access:** Utilizes Apple Neural Engine for 10x performance boost
- **Low Memory Usage:** 14x reduction compared to CPU implementation
- **Native Integration:** Purpose-built for M1/M2/M3 chips
- **Active Development:** Based on [parakeet-mlx](https://github.com/EliFuzz/parakeet-mlx) implementations

## 🔗 References

- [Parakeet TDT Model](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) - HuggingFace model page
- [NeMo Framework](https://docs.nvidia.com/nemo-framework/) - NVIDIA's toolkit
- [Apple MLX](https://github.com/ml-explore/mlx) - Apple's ML framework
- [parakeet-mlx](https://github.com/EliFuzz/parakeet-mlx) - MLX implementation
- [Argmax Optimization](https://www.argmaxinc.com/blog/nvidia-frontier-speech-models-on-argmax-sdk) - Performance benchmarks

## 📄 License

This project follows the model's **CC-BY-4.0** license.

## 🤝 Contributing

This is currently a personal project in active development. Once the initial implementation is complete, contribution guidelines will be added.

---

**Built with Claude Code** • [Implementation Plan](docs/plans/2026-02-11-minimal-stt-cli.md)
