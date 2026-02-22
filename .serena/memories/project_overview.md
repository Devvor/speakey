# Parakeet STT - Project Overview

## Purpose
Local-first speech-to-text CLI application using NVIDIA's Parakeet TDT 0.6B v3 model.
Includes push-to-talk (fn-ptt) functionality.

## Tech Stack
- Python 3.14 (venv-based)
- NeMo Toolkit for ASR (primary backend)
- MLX/parakeet-mlx for Apple Silicon (secondary backend)
- Click for CLI
- sounddevice for audio recording (fn-ptt)
- pytest for testing

## Project Structure
- `src/` — main package: config.py, model.py, cli.py, output.py
- `src/fn_ptt/` — function-key push-to-talk: app.py, manager.py, run.py
- `src/daemon/` — daemon mode: app.py, controller.py, ipc.py, manager.py, run_daemon.py
- `src/backends/` — backend abstraction: base.py, nemo_backend.py, mlx_backend.py, factory.py
- `tests/` — test suite
- `docs/` — knowledge, plans, research

## Model
- `nvidia/parakeet-tdt-0.6b-v3` (hardcoded in Config)
- **25 European languages only** — NO Chinese/Mandarin support
- NeMo backend: loads via `nemo_asr.models.ASRModel.from_pretrained()`
- MLX backend: loads via `parakeet_mlx.from_pretrained("mlx-community/parakeet-tdt-0.6b-v2")`

## Backend Selection (BackendFactory)
1. Apple Silicon + MLX available → MLXBackend
2. NeMo available → NeMoBackend
3. Neither → error
