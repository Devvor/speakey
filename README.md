# Speakey

Local speech-to-text for Mac — hold **fn**, speak, release, and your words appear wherever your cursor is. Runs entirely on-device using the Apple Neural Engine. No internet required, no subscriptions.

**Distribution model:** source-first. There is no public DMG or App Store build. Clone the repo, build on your Mac (or point an AI coding agent at the repo and ask it to build), then run the **Speakey** binary.

This repository also includes an optional Python CLI under `src/`.

---

## Install — build from source

### Requirements

- Apple Silicon Mac (recommended) running **macOS 14+**
- Swift toolchain (Xcode or Command Line Tools; the build script prefers the [swift.org](https://www.swift.org/download/) `swift-6.2.3-RELEASE` toolchain if installed)

### Build & run

```bash
git clone https://github.com/Devvor/speakey.git
cd speakey

./scripts/build-swift.sh          # debug (default)
# ./scripts/build-swift.sh release  # optimised

# Run the menu-bar app
./swift/.build/debug/speakey
# or, after a release build:
# ./swift/.build/release/speakey
```

First launch downloads the CoreML model (~2.5GB) into the app cache. Later launches reuse it.

**For AI agents:** the only required steps are clone → `./scripts/build-swift.sh` → run the binary path printed at the end of the script → grant permissions below → quit and reopen once.

### Grant permissions (one-time)

**System Settings → Privacy & Security**

| Permission | Why it's needed |
|---|---|
| **Accessibility** | Detect fn / fn+Space / Esc, and paste transcribed text into any app |
| **Microphone** | Record your voice |

After granting permissions, quit the app and start it again.

### How to use

1. Click into any text field (email, Slack, Notes, terminal — anything)
2. Hold **fn** for about **0.3 seconds** and speak (or press **fn+Space** for hands-free; **Esc** to cancel)
3. Release **fn** (or tap **fn** again in hands-free mode)
4. Your words appear in the text field within 1–2 seconds

### Menu bar

Click the microphone icon in the menu bar to:

- See the current status (loading / ready / recording)
- Enable launch at login
- Quit the app

### Troubleshooting

**Nothing happens when I hold fn**  
→ Grant **Accessibility**, then quit and reopen the app. If you rebuild to a new path, remove the old binary from the Accessibility list and add the new one.

**Audio records but text doesn't appear**  
→ Accessibility is also required for paste.

**No audio is captured**  
→ Grant **Microphone**, then quit and reopen.

**Build fails with `PackageDescription` / undefined symbols**  
→ Install the swift.org toolchain and re-run `./scripts/build-swift.sh` (the script documents the exact package URL).

**macOS blocks the binary**  
→ Right-click → Open, or run it from Terminal. Local builds are unsigned; that is expected for source-first installs.

**Slow on first dictation**  
→ Wait until the menu bar shows **Ready** (model still loading or downloading).

### Optional: local `.app` / DMG

`scripts/package-dmg.sh` can wrap a build into a `.app` / DMG for your own machine. It is **not** the supported install path and is not used for public releases, notarization, or auto-updates.

---

## For Developers

**Primary product:** native Swift menu-bar app in `swift/` (**Speakey**).  
**Optional:** Python CLI / daemon / fn-ptt in `src/` for scripting and experiments (`parakeet-stt` package name).

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and PR guidance.

### Project Structure

```
speakey/
├── src/                    # Optional Python CLI and daemon
│   ├── backends/           # Backend implementations (NeMo, MLX)
│   ├── daemon/             # Background recording daemon (Unix socket IPC)
│   ├── fn_ptt/             # Python fn-key push-to-talk
│   ├── cli.py              # Click-based CLI
│   ├── config.py           # Configuration management
│   ├── model.py            # Model wrapper
│   └── output.py           # Output formatting
├── swift/                  # Native macOS menu-bar app (Speakey)
│   └── Sources/Speakey/
├── scripts/
│   ├── build-swift.sh      # Primary: build & run from source
│   └── package-dmg.sh      # Optional: local .app/DMG only
└── tests/                  # Python test suite
```

### Python CLI (optional)

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Apple Silicon — also: pip install -r requirements-mlx.txt

parakeet-stt transcribe audio.wav
parakeet-stt fn-ptt start
```

| Platform | Backend | Hardware | Performance |
|---|---|---|---|
| Mac (Apple Silicon) | MLX | Apple Neural Engine | 10x faster |
| Mac (Intel) | NeMo | CPU | Baseline |
| Linux/Windows (NVIDIA) | NeMo | CUDA | 3–5x faster |
| Other | NeMo | CPU | Baseline |

### Testing & quality

```bash
source venv/bin/activate
pip install pytest pytest-cov pytest-mock black ruff

pytest -m "not slow"
black --line-length 100 src/ tests/
ruff check --line-length 100 src/ tests/
```

CI on `main`: Python lint, unit tests, Swift debug build, `pip-audit`.

---

## Model

- **Model:** [nvidia/parakeet-tdt-0.6b-v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Parameters:** 600 million
- **Architecture:** FastConformer-TDT
- **Word Error Rate:** 6.05% average
- **Model license:** CC-BY-4.0 (weights / model card — separate from this repo’s code license)

## License

- **This repository’s source code** is released under the [MIT License](LICENSE) (Copyright © 2026 Devvor).
- **NVIDIA Parakeet model weights** used at runtime remain under [CC-BY-4.0](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3).
