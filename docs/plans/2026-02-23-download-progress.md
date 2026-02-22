# Model Download Progress Indicator — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Show visible download progress in the menu bar when the app downloads models on first launch, with an animated icon, descriptive text, and a completion notification.

**Architecture:** Split the single `.loading` AppState into `.downloading` and `.loadingModel` phases. The menu bar icon pulses during download via `symbolEffect(.pulse)`. A `UNUserNotification` fires when the model is ready after first-time download. The `loadModel()` logic in AppDelegate checks `AsrModels.modelsExist()` to determine whether to download or just load from cache.

**Tech Stack:** SwiftUI (symbolEffect), UserNotifications framework, FluidAudio (AsrModels API)

---

### Task 1: Split AppState.Status into download and loading phases

**Files:**
- Modify: `swift/Sources/ParakeetPTT/AppState.swift`

**Step 1: Update the Status enum**

Replace `.loading` with `.downloading` and `.loadingModel`:

```swift
import SwiftUI

@Observable
@MainActor
final class AppState {
    enum Status: Equatable {
        case downloading    // First launch: downloading models from HuggingFace
        case loadingModel   // Loading cached models into memory
        case ready          // Idle, waiting for fn key
        case recording      // fn held, mic active
        case transcribing   // fn released, processing audio
        case error(String)  // Something went wrong
    }

    var status: Status = .loadingModel
    var lastTranscription: String = ""

    var isRecording: Bool { status == .recording }
    var statusText: String {
        switch status {
        case .downloading:        return "Downloading model (~2.5GB)..."
        case .loadingModel:       return "Loading model..."
        case .ready:              return "Ready"
        case .recording:          return "Recording..."
        case .transcribing:       return "Transcribing..."
        case .error(let message): return "Error: \(message)"
        }
    }

    var statusIcon: String {
        switch status {
        case .downloading:   return "arrow.down.circle"
        case .loadingModel:  return "gear"
        case .ready:         return "waveform"
        case .recording:     return "mic.fill"
        case .transcribing:  return "ellipsis.circle"
        case .error:         return "exclamationmark.triangle"
        }
    }

    var isDownloading: Bool { status == .downloading }
}
```

Note: default status changes from `.loading` to `.loadingModel` since most launches will load from cache.

**Step 2: Build to check for compile errors**

Run: `cd swift && swift build 2>&1 | head -30`

Expected: Compile errors in files that switch on `Status` (AppDelegate, OverlayView). This is expected — we fix them in subsequent tasks.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/AppState.swift
git commit -m "feat: split loading status into downloading and loadingModel phases"
```

---

### Task 2: Update OverlayView to handle new status cases

**Files:**
- Modify: `swift/Sources/ParakeetPTT/OverlayView.swift`

**Step 1: Update the indicator and label switch statements**

The overlay only shows for `.recording` and `.transcribing`. The new `.downloading` and `.loadingModel` cases should fall into the `default` branch (overlay is not shown during download — the menu bar handles that). The old `.loading` case no longer exists, so remove any reference to it.

```swift
import SwiftUI

struct OverlayView: View {
    let status: AppState.Status

    var body: some View {
        HStack(spacing: 10) {
            indicator
            Text(label)
                .font(.system(size: 14, weight: .medium))
                .foregroundStyle(.primary)
        }
        .padding(.horizontal, 28)
        .padding(.vertical, 12)
        .fixedSize()
        .background(.ultraThinMaterial, in: Capsule())
    }

    @ViewBuilder
    private var indicator: some View {
        switch status {
        case .recording:
            Circle()
                .fill(.red)
                .frame(width: 10, height: 10)
        case .transcribing:
            ProgressView()
                .controlSize(.small)
        default:
            EmptyView()
        }
    }

    private var label: String {
        switch status {
        case .recording:    return "Recording..."
        case .transcribing: return "Transcribing..."
        default:            return ""
        }
    }
}
```

No functional changes — just ensuring the switch is exhaustive with the new enum cases.

**Step 2: Build to verify**

Run: `cd swift && swift build 2>&1 | head -30`

Expected: OverlayView compiles. May still have errors in other files.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/OverlayView.swift
git commit -m "fix: update OverlayView for new status enum cases"
```

---

### Task 3: Update MenuBarView to show subtitle during download

**Files:**
- Modify: `swift/Sources/ParakeetPTT/MenuBarView.swift`

**Step 1: Add a subtitle line for the downloading phase**

```swift
import SwiftUI

struct MenuBarView: View {
    let appState: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: appState.statusIcon)
                    .foregroundStyle(appState.isRecording ? .red : .secondary)
                Text(appState.statusText)
                    .font(.headline)
            }

            if appState.isDownloading {
                Text("First launch only.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Divider()

            Text("Hold fn for 0.5s to record")
                .font(.caption)
                .foregroundStyle(.secondary)

            Divider()

            Button("Quit Parakeet PTT") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q")
        }
        .padding()
        .frame(width: 240)
    }
}
```

**Step 2: Build to verify**

Run: `cd swift && swift build 2>&1 | head -30`

Expected: MenuBarView compiles.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/MenuBarView.swift
git commit -m "feat: show 'First launch only' subtitle during model download"
```

---

### Task 4: Animate menu bar icon during download

**Files:**
- Modify: `swift/Sources/ParakeetPTT/ParakeetApp.swift`

**Step 1: Add symbolEffect(.pulse) to the menu bar label**

The `symbolEffect` modifier with `isActive` parameter lets us pulse only when downloading.

```swift
import SwiftUI

@main
struct ParakeetApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra {
            MenuBarView(appState: appDelegate.appState)
        } label: {
            Label("Parakeet PTT", systemImage: appDelegate.appState.statusIcon)
                .symbolEffect(.pulse, isActive: appDelegate.appState.isDownloading)
        }
        .menuBarExtraStyle(.window)
    }
}
```

**Step 2: Build to verify**

Run: `cd swift && swift build 2>&1 | head -30`

Expected: Compiles successfully.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/ParakeetApp.swift
git commit -m "feat: pulse menu bar icon during model download"
```

---

### Task 5: Rewrite loadModel() to split download from load, add notification

**Files:**
- Modify: `swift/Sources/ParakeetPTT/AppDelegate.swift`

**Step 1: Add UserNotifications import and rewrite loadModel()**

This is the main logic change. We:
1. Add `import UserNotifications`
2. Request notification permission at launch
3. Check `AsrModels.modelsExist()` to decide download vs load-from-cache
4. Set status to `.downloading` or `.loadingModel` as appropriate
5. Send a notification after first-time download completes

```swift
import AppKit
import AVFoundation
import FluidAudio
import SwiftUI
import UserNotifications

@MainActor
class AppDelegate: NSObject, NSApplicationDelegate {
    let appState = AppState()
    private let transcriptionService = TranscriptionService()
    private let audioRecorder = AudioRecorder()
    private let fnKeyMonitor = FnKeyMonitor()
    private var overlayPanel: OverlayPanel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        requestMicPermission()
        requestNotificationPermission()
        setupOverlay()
        setupFnKeyMonitor()
        loadModel()
    }

    private func requestMicPermission() {
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
        case .authorized:
            print("[PTT] Microphone permission: authorized")
        case .notDetermined:
            print("[PTT] Requesting microphone permission...")
            AVCaptureDevice.requestAccess(for: .audio) { granted in
                print("[PTT] Microphone permission \(granted ? "granted" : "denied")")
            }
        case .denied, .restricted:
            print("[PTT] Microphone permission denied — check System Settings > Privacy > Microphone")
            appState.status = .error("Grant Microphone permission in System Settings")
        @unknown default:
            break
        }
    }

    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { granted, error in
            if let error {
                print("[PTT] Notification permission error: \(error.localizedDescription)")
            } else {
                print("[PTT] Notification permission \(granted ? "granted" : "denied")")
            }
        }
    }

    // MARK: - Setup

    private func setupOverlay() {
        overlayPanel = OverlayPanel()
    }

    private func setupFnKeyMonitor() {
        fnKeyMonitor.onHoldStart = { [weak self] in
            self?.startRecording()
        }
        fnKeyMonitor.onRelease = { [weak self] in
            self?.stopRecordingAndTranscribe()
        }

        if !fnKeyMonitor.start() {
            appState.status = .error("Grant Accessibility permission in System Settings")
        }
    }

    private func loadModel() {
        Task {
            do {
                let cacheDir = AsrModels.defaultCacheDirectory(for: .v3)
                let needsDownload = !AsrModels.modelsExist(at: cacheDir, version: .v3)

                if needsDownload {
                    appState.status = .downloading
                    print("[PTT] Models not cached, downloading...")
                    try await AsrModels.download(version: .v3)
                    print("[PTT] Download complete")
                }

                appState.status = .loadingModel
                print("[PTT] Loading model into memory...")
                try await transcriptionService.loadFromCache()
                print("[PTT] Model loaded successfully")

                appState.status = .ready

                if needsDownload {
                    sendReadyNotification()
                }
            } catch {
                appState.status = .error("Model load failed: \(error.localizedDescription)")
            }
        }
    }

    private func sendReadyNotification() {
        let content = UNMutableNotificationContent()
        content.title = "Parakeet PTT"
        content.body = "Model ready — hold fn to start dictating"
        content.sound = .default

        let request = UNNotificationRequest(
            identifier: "model-ready",
            content: content,
            trigger: nil
        )
        UNUserNotificationCenter.current().add(request) { error in
            if let error {
                print("[PTT] Failed to send notification: \(error.localizedDescription)")
            }
        }
    }

    // MARK: - Recording pipeline

    private func startRecording() {
        Task {
            guard appState.status == .ready else { return }
            appState.status = .recording
            showOverlay()

            do {
                try audioRecorder.startRecording()
            } catch {
                appState.status = .error("Mic error: \(error.localizedDescription)")
                hideOverlay()
            }
        }
    }

    private func stopRecordingAndTranscribe() {
        Task {
            guard appState.status == .recording else { return }
            appState.status = .transcribing
            updateOverlay()

            let samples = audioRecorder.stopRecording()
            let duration = Double(samples.count) / 16000.0
            print("[PTT] Captured \(samples.count) samples (\(String(format: "%.1f", duration))s of audio)")

            // Check audio levels
            if !samples.isEmpty {
                let maxAmp = samples.map { abs($0) }.max() ?? 0
                let rms = sqrt(samples.map { $0 * $0 }.reduce(0, +) / Float(samples.count))
                print("[PTT] Audio levels — max: \(maxAmp), RMS: \(rms)")
            }

            guard !samples.isEmpty else {
                print("[PTT] No samples captured, skipping transcription")
                appState.status = .ready
                hideOverlay()
                return
            }

            do {
                let text = try await transcriptionService.transcribe(samples)
                print("[PTT] Transcription result: '\(text)'")
                if !text.isEmpty {
                    PasteService.paste(text)
                    appState.lastTranscription = text
                } else {
                    print("[PTT] Transcription returned empty text")
                }
            } catch {
                print("[PTT] Transcription error: \(error)")
                appState.status = .error("Transcription failed: \(error.localizedDescription)")
            }

            appState.status = .ready
            hideOverlay()
        }
    }

    // MARK: - Overlay

    private func showOverlay() {
        overlayPanel?.showView(OverlayView(status: appState.status))
    }

    private func updateOverlay() {
        overlayPanel?.showView(OverlayView(status: appState.status))
    }

    private func hideOverlay() {
        overlayPanel?.orderOut(nil)
    }
}
```

**Step 2: Add `loadFromCache()` method to TranscriptionService**

The current `TranscriptionService.loadModel()` calls `AsrModels.downloadAndLoad()`. We need a new method that only loads from cache (download is handled by AppDelegate now).

Modify `swift/Sources/ParakeetPTT/TranscriptionService.swift`:

```swift
import FluidAudio
import Foundation

actor TranscriptionService {
    private var models: AsrModels?
    private nonisolated(unsafe) var manager: AsrManager?

    func loadModel() async throws {
        let models = try await AsrModels.downloadAndLoad(version: .v3)
        let manager = AsrManager(config: .default)
        try await manager.initialize(models: models)
        self.models = models
        self.manager = manager
    }

    func loadFromCache() async throws {
        let models = try await AsrModels.loadFromCache(version: .v3)
        let manager = AsrManager(config: .default)
        try await manager.initialize(models: models)
        self.models = models
        self.manager = manager
    }

    func transcribe(_ audioSamples: [Float]) async throws -> String {
        guard let manager else {
            throw TranscriptionError.notInitialized
        }
        let result = try await manager.transcribe(audioSamples, source: .microphone)
        print("[PTT] ASRResult — text: '\(result.text)', confidence: \(result.confidence)")
        return result.text
    }
}

enum TranscriptionError: LocalizedError {
    case notInitialized

    var errorDescription: String? {
        switch self {
        case .notInitialized: return "Model not loaded"
        }
    }
}
```

**Step 3: Build to verify everything compiles**

Run: `cd swift && swift build 2>&1 | head -40`

Expected: Successful build with no errors.

**Step 4: Commit**

```bash
git add swift/Sources/ParakeetPTT/AppDelegate.swift swift/Sources/ParakeetPTT/TranscriptionService.swift
git commit -m "feat: split download from load, add completion notification"
```

---

### Task 6: Manual testing

**Step 1: Build release**

Run: `cd swift && swift build -c release`

Expected: Successful build.

**Step 2: Test first-launch flow (download needed)**

Delete cached models and run:

```bash
rm -rf ~/Library/Application\ Support/FluidAudio/Models/
./swift/.build/release/parakeet-ptt
```

Expected:
- Menu bar icon appears as `arrow.down.circle` and pulses
- Clicking the dropdown shows "Downloading model (~2.5GB)..." with "First launch only." subtitle
- After download completes, icon changes to `gear`, text shows "Loading model..."
- After load, icon becomes `waveform`, text shows "Ready"
- macOS notification appears: "Parakeet PTT — Model ready — hold fn to start dictating"

**Step 3: Test subsequent launch (cached)**

```bash
pkill parakeet-ptt
./swift/.build/release/parakeet-ptt
```

Expected:
- Menu bar icon appears as `gear` briefly
- Text shows "Loading model..." (no download phase)
- Quickly transitions to `waveform` / "Ready"
- No notification sent

**Step 4: Test PTT still works**

Hold fn key for 0.5s, speak, release. Verify transcription works as before.

**Step 5: Commit any fixes, then final commit**

```bash
git add -A
git commit -m "test: verify download progress indicator working end-to-end"
```
