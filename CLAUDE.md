# Speakey — Agent Guide

Local-first macOS speech-to-text. **Primary product:** Swift menu-bar app in `swift/`. **Optional:** Python CLI / daemon / fn-ptt in `src/`.

**Distribution:** source-first (clone → build → run). No public DMG / notarization / Sparkle.

---

## Build & run (Swift)

```bash
./scripts/build-swift.sh          # debug
./swift/.build/debug/speakey
./scripts/build-swift.sh release  # release
```

Grant **Accessibility** + **Microphone**, then quit and reopen. First launch downloads the CoreML model (~2.5GB).

---

## Python (optional)

```bash
source venv/bin/activate
pip install -r requirements.txt
# MLX backend: pip install "parakeet-stt[mlx]"
pip install pytest pytest-cov pytest-mock black ruff
pytest -m "not slow"
```

---

## Layout

```
swift/Sources/Speakey/   # Menu-bar app (fn / fn+Space PTT)
src/                     # CLI, backends, daemon, fn-ptt
scripts/build-swift.sh   # Supported build path
tests/                   # Python tests
docs/knowledge/          # Reference notes
docs/archive/            # Historical plans (do not treat as current)
```

---

## Rules for agents

1. Prefer Swift app changes over Python experiments.
2. Keep README build path accurate (`./scripts/build-swift.sh` → run binary).
3. **Never log transcription text** — length/status only.
4. Daemon IPC: runtime dir `0o700`, socket `0o600`.
5. Do not commit secrets, model weights, or large binaries.
6. Licenses: repo code **MIT**; Parakeet weights **CC-BY-4.0**; FluidAudio **Apache-2.0** (see `NOTICE`).

---

## Style

- Python: Black + Ruff, 100 cols; type hints encouraged.
- Swift: match patterns in `swift/Sources/Speakey/`.
- Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`.

---

## Model

`nvidia/parakeet-tdt-0.6b-v3` — FastConformer-TDT, ~600M, 16 kHz mono, CC-BY-4.0 weights.

---

## More detail

- User install: [README.md](README.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security: [SECURITY.md](SECURITY.md)
- Phase history / deep notes: [docs/knowledge/](docs/knowledge/), [docs/archive/](docs/archive/)
