# Design: Model Download Progress Indicator

## Problem

On first launch, FluidAudio downloads ~2.5GB of CoreML models with no visible feedback. The menu bar icon appears silently and shows a generic "Loading model..." in its dropdown. Users have no idea anything is happening or how long to wait.

## Solution

Split the single `.loading` state into `.downloading` and `.loadingModel` phases. Animate the menu bar icon during download. Send a macOS notification when the model is ready.

## Changes

### 1. AppState — split loading into two phases

Replace `.loading` with:
- `.downloading` — models not cached, downloading ~2.5GB from HuggingFace
- `.loadingModel` — models cached locally, loading into memory

Update `statusText`:
- `.downloading` → "Downloading model (~2.5GB)..."
- `.loadingModel` → "Loading model..."

Update `statusIcon`:
- `.downloading` → "arrow.down.circle"
- `.loadingModel` → "gear"

### 2. Menu bar icon — animate during download

Use SwiftUI `symbolEffect(.pulse)` on the menu bar icon when status is `.downloading`. This makes the download arrow visibly pulse so the user notices activity without clicking the dropdown.

Static icons for all other states (no animation).

### 3. Menu bar dropdown — descriptive phase text

During `.downloading`, show a subtitle "First launch only." below the status text so the user knows this is a one-time operation.

All other states keep their current single-line display.

### 4. Notification on completion

Request `UNUserNotificationCenter` permission at app launch (alongside mic permission).

After first-time download completes and model is ready, send a local notification:
- Title: "Parakeet PTT"
- Body: "Model ready — hold fn to start dictating"

Only send the notification when transitioning from `.downloading` → `.ready` (not on subsequent launches from cache).

### 5. AppDelegate.loadModel() — split download from load

Current: calls `AsrModels.downloadAndLoad()` (combined)

New logic:
1. Check `AsrModels.modelsExist(at:version:)` for cached models
2. If not cached:
   - Set status to `.downloading`
   - Call `AsrModels.download(version:)`
   - Set status to `.loadingModel`
   - Call `AsrModels.loadFromCache(version:)`
   - Send completion notification
3. If cached:
   - Set status to `.loadingModel`
   - Call `AsrModels.loadFromCache(version:)`
   - No notification (user already knows about the app)
4. Set status to `.ready`

### Files touched

- `AppState.swift` — new enum cases, updated statusText/statusIcon
- `AppDelegate.swift` — split loadModel(), add notification permission request, send notification
- `ParakeetApp.swift` — add symbolEffect to menu bar icon
- `MenuBarView.swift` — add subtitle line for downloading phase

### Files untouched

- OverlayPanel.swift, OverlayView.swift — recording/transcribing overlay unchanged
- TranscriptionService.swift — download logic moves to AppDelegate
- FnKeyMonitor.swift, AudioRecorder.swift, PasteService.swift — no changes

## FluidAudio API used

- `AsrModels.modelsExist(at:version:)` — check if models are cached
- `AsrModels.download(to:force:version:)` — download only
- `AsrModels.loadFromCache(configuration:version:)` — load from cache
- `AsrModels.defaultCacheDirectory(for:)` — get cache path

## Verification

1. Build: `cd swift && swift build -c release`
2. Delete cached models: `rm -rf ~/Library/Application\ Support/FluidAudio/Models/`
3. Run app — menu bar icon should pulse during download, dropdown shows "Downloading model (~2.5GB)..." with "First launch only."
4. After download completes, icon changes to gear, dropdown shows "Loading model..."
5. After load, icon becomes waveform, dropdown says "Ready", notification appears
6. Quit and relaunch — should skip download, briefly show "Loading model...", then "Ready", no notification
