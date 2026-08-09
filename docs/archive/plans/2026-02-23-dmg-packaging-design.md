# Design: DMG Packaging

## Problem

The app can only be run as a bare binary from `.build/release/`. This prevents `UNUserNotificationCenter` from working (no bundle identity) and isn't distributable to users.

## Solution

A `scripts/package-dmg.sh` script that builds the release binary, wraps it in a `.app` bundle, and creates a `.dmg` disk image for distribution.

## What the script does

1. Builds the release binary (`swift build -c release`)
2. Creates `.app` bundle structure with `Info.plist` and the binary
3. Creates `.dmg` containing the `.app` and an Applications folder shortcut
4. Outputs `ParakeetPTT.dmg` in the project root

## .app bundle structure

```
ParakeetPTT.app/
└── Contents/
    ├── Info.plist
    └── MacOS/
        └── parakeet-ptt
```

## Info.plist contents

- `CFBundleName`: Parakeet PTT
- `CFBundleIdentifier`: com.parakeet.ptt
- `CFBundleExecutable`: parakeet-ptt
- `CFBundleVersion` / `CFBundleShortVersionString`: 1.0.0
- `CFBundlePackageType`: APPL
- `LSUIElement`: true (hide from Dock — menu bar app)
- `NSMicrophoneUsageDescription`: existing mic permission string
- `LSMinimumSystemVersion`: 14.0

## No code signing

Unsigned for now. Users right-click > Open on first launch to bypass Gatekeeper.

## Files

- Create: `scripts/package-dmg.sh`
- Untouched: all Swift source, `scripts/build-swift.sh`
