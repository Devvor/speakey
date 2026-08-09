# Contributing

Thanks for helping improve **Kuaishuo**.

This project is **source-first**: users (and AI agents) clone the repo and build with `./scripts/build-swift.sh`. There is no public DMG, notarization, or auto-updater to maintain.

## What to work on

| Path | Role |
|------|------|
| `swift/` | **Primary product** — macOS menu-bar push-to-talk app |
| `src/` | Optional Python CLI, daemon, and experimental fn-ptt |
| `tests/` | Python unit tests |
| `scripts/` | Build scripts (`build-swift.sh` is the supported path) |

Prefer changes that improve the Swift app’s daily UX, reliability, and **build-from-source** experience. Keep the README agent-friendly (one clear build command).

## Setup

### Swift app

```bash
./scripts/build-swift.sh          # debug
./scripts/build-swift.sh release  # release
./swift/.build/debug/kuaishuo
```

Requires macOS 14+ and a recent Swift toolchain (see README). Grant **Accessibility** and **Microphone** when testing fn-key dictation. After rebuilding to a new path, re-add the binary in Accessibility settings if needed.

### Python CLI

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock black ruff
pytest -m "not slow"
```

## Pull requests

1. Keep changes focused; avoid drive-by refactors.
2. Match existing style (Swift: AppKit/SwiftUI patterns in `swift/Sources/Kuaishuo/`; Python: Black/Ruff, 100 cols).
3. Do not commit secrets, model weights, or large binaries.
4. Update README when user-facing behavior, permissions, or the build path change.

## License

Code contributions are accepted under the MIT License (see `LICENSE`). NVIDIA Parakeet model weights remain under CC-BY-4.0.
