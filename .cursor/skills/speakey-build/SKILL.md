---
name: speakey-build
description: Build and run the Speakey macOS menu-bar app from source. Use when cloning Speakey, building the Swift app, fixing the install path, or helping an agent set up local fn-key speech-to-text.
---

# Speakey build

## Steps

1. From repo root: `./scripts/build-swift.sh` (or `release`).
2. Run: `./swift/.build/debug/speakey` (or `.build/release/speakey`).
3. Grant **Accessibility** and **Microphone**; quit and reopen.
4. Hold **fn** (~0.3s) to dictate, or **fn+Space** for hands-free; **Esc** cancels.

## Rules

- Source-first only — do not treat DMG packaging as the supported path.
- Never log transcription text (length/status only).
- Prefer changes under `swift/`; `src/` is optional Python CLI.
- Licenses: MIT (code), CC-BY-4.0 (Parakeet weights), Apache-2.0 (FluidAudio). See `NOTICE`.
