# parakeet-ptt: Pure Swift Push-to-Talk macOS App

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Build a standalone macOS menu bar app that provides push-to-talk speech-to-text using CoreML/Apple Neural Engine via FluidAudio, with zero Python involvement.

**Architecture:** A SwiftUI menu bar app (`MenuBarExtra`) with no dock icon. CGEvent tap monitors fn key hold/release. AVAudioEngine captures mic audio into a PCM buffer. FluidAudio transcribes in-memory via CoreML/ANE. Result is pasted into the active field via NSPasteboard + simulated Cmd+V. A floating overlay panel shows recording/transcribing state.

**Tech Stack:** SwiftUI (macOS 14+), [FluidAudio](https://github.com/FluidInference/FluidAudio) v0.12.1 (Swift Package, Apache 2.0), AVAudioEngine, CoreGraphics (CGEvent), AppKit (NSPanel, NSPasteboard).

**Design Doc:** `docs/plans/2026-02-22-coreml-ane-backend-design.md`

---

## Prerequisites

- **macOS 14+** (Sonoma or later)
- **Apple Silicon** (M1/M2/M3/M4)
- **Xcode Command Line Tools** — `xcode-select --install`
- **Swift 6.0+** — ships with Xcode 16+

---

### Task 1: Swift package manifest

**Files:**
- Create: `swift/Package.swift`

**Step 1: Create the Swift package directory structure**

```bash
mkdir -p swift/Sources/ParakeetPTT
```

**Step 2: Write Package.swift**

```swift
// swift/Package.swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ParakeetPTT",
    platforms: [.macOS(.v14)],
    dependencies: [
        .package(
            url: "https://github.com/FluidInference/FluidAudio.git",
            from: "0.12.1"
        ),
    ],
    targets: [
        .executableTarget(
            name: "parakeet-ptt",
            dependencies: [
                .product(name: "FluidAudio", package: "FluidAudio"),
            ],
            path: "Sources/ParakeetPTT",
            linkerSettings: [
                .linkedFramework("AVFoundation"),
                .linkedFramework("CoreGraphics"),
                .linkedFramework("AppKit"),
            ]
        ),
    ]
)
```

**Step 3: Create a minimal main.swift placeholder so the package resolves**

```swift
// swift/Sources/ParakeetPTT/ParakeetApp.swift
import SwiftUI

@main
struct ParakeetApp: App {
    var body: some Scene {
        MenuBarExtra("Parakeet PTT", systemImage: "waveform") {
            Text("Loading...")
            Divider()
            Button("Quit") { NSApplication.shared.terminate(nil) }
        }
    }
}
```

**Step 4: Resolve dependencies**

```bash
cd swift && swift package resolve
```

Expected: Dependencies resolved. `Package.resolved` created.

**Step 5: Build to verify**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds (or warnings only — the app won't do anything useful yet).

**Step 6: Commit**

```bash
git add swift/Package.swift swift/Sources/ParakeetPTT/ParakeetApp.swift
git commit -m "chore: add Swift package manifest for parakeet-ptt"
```

---

### Task 2: App state management

**Files:**
- Create: `swift/Sources/ParakeetPTT/AppState.swift`

**Step 1: Write AppState**

This is the central observable state that drives the UI. All state transitions flow through here.

```swift
// swift/Sources/ParakeetPTT/AppState.swift
import SwiftUI

@Observable
@MainActor
final class AppState {
    enum Status: Equatable {
        case loading       // Model downloading/loading
        case ready         // Idle, waiting for fn key
        case recording     // fn held, mic active
        case transcribing  // fn released, processing audio
        case error(String) // Something went wrong
    }

    var status: Status = .loading
    var lastTranscription: String = ""

    var isRecording: Bool { status == .recording }
    var statusText: String {
        switch status {
        case .loading:            return "Loading model..."
        case .ready:              return "Ready"
        case .recording:          return "Recording..."
        case .transcribing:       return "Transcribing..."
        case .error(let message): return "Error: \(message)"
        }
    }

    var statusIcon: String {
        switch status {
        case .loading:       return "arrow.down.circle"
        case .ready:         return "waveform"
        case .recording:     return "mic.fill"
        case .transcribing:  return "ellipsis.circle"
        case .error:         return "exclamationmark.triangle"
        }
    }
}
```

**Step 2: Build to verify**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/AppState.swift
git commit -m "feat: add AppState observable for PTT state management"
```

---

### Task 3: Fn key monitor

**Files:**
- Create: `swift/Sources/ParakeetPTT/FnKeyMonitor.swift`

**Step 1: Write FnKeyMonitor**

Uses CGEvent tap to detect fn key hold (>0.5s threshold) and release. Calls back on press/release. Runs on the main thread (CGEvent taps require a run loop).

```swift
// swift/Sources/ParakeetPTT/FnKeyMonitor.swift
import CoreGraphics
import Foundation

final class FnKeyMonitor: @unchecked Sendable {
    private let holdThreshold: TimeInterval = 0.5
    private var eventTap: CFMachPort?
    private var runLoopSource: CFRunLoopSource?
    private var fnPressTime: Date?
    private var holdTimerActive = false
    private var isHolding = false

    var onHoldStart: (() -> Void)?
    var onRelease: (() -> Void)?

    func start() -> Bool {
        let eventMask: CGEventMask = 1 << CGEventType.flagsChanged.rawValue

        guard let tap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: eventMask,
            callback: { proxy, type, event, refcon in
                guard let refcon else { return Unmanaged.passUnretained(event) }
                let monitor = Unmanaged<FnKeyMonitor>.fromOpaque(refcon).takeUnretainedValue()
                return monitor.handleEvent(type: type, event: event)
            },
            userInfo: Unmanaged.passUnretained(self).toOpaque()
        ) else {
            return false
        }

        eventTap = tap
        runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetMain(), runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: tap, enable: true)
        return true
    }

    func stop() {
        if let tap = eventTap {
            CGEvent.tapEnable(tap: tap, enable: false)
        }
        if let source = runLoopSource {
            CFRunLoopRemoveSource(CFRunLoopGetMain(), source, .commonModes)
        }
        eventTap = nil
        runLoopSource = nil
    }

    private func handleEvent(type: CGEventType, event: CGEvent) -> Unmanaged<CGEvent>? {
        // Re-enable if system disabled our tap
        if type == .tapDisabledByTimeout || type == .tapDisabledByUserInput {
            if let tap = eventTap {
                CGEvent.tapEnable(tap: tap, enable: true)
            }
            return Unmanaged.passUnretained(event)
        }

        guard type == .flagsChanged else {
            return Unmanaged.passUnretained(event)
        }

        let keycode = event.getIntegerValueField(.keyboardEventKeycode)
        guard keycode == 63 else { return Unmanaged.passUnretained(event) } // 63 = fn key

        let fnDown = event.flags.contains(.maskSecondaryFn)

        if fnDown && fnPressTime == nil {
            fnPressTime = Date()
            holdTimerActive = true
            DispatchQueue.main.asyncAfter(deadline: .now() + holdThreshold) { [weak self] in
                self?.checkThreshold()
            }
        } else if !fnDown && fnPressTime != nil {
            fnPressTime = nil
            holdTimerActive = false
            if isHolding {
                isHolding = false
                DispatchQueue.main.async { [weak self] in
                    self?.onRelease?()
                }
            }
        }

        return Unmanaged.passUnretained(event)
    }

    private func checkThreshold() {
        guard holdTimerActive, fnPressTime != nil else { return }
        isHolding = true
        DispatchQueue.main.async { [weak self] in
            self?.onHoldStart?()
        }
    }

    deinit { stop() }
}
```

**Step 2: Build to verify**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/FnKeyMonitor.swift
git commit -m "feat: add fn key hold/release monitor via CGEvent tap"
```

---

### Task 4: Audio recorder

**Files:**
- Create: `swift/Sources/ParakeetPTT/AudioRecorder.swift`

**Step 1: Write AudioRecorder**

Uses AVAudioEngine with a mixer node to capture mic audio at 16kHz mono Float32 — the format FluidAudio expects. Accumulates samples in memory (no disk I/O).

```swift
// swift/Sources/ParakeetPTT/AudioRecorder.swift
import AVFoundation

final class AudioRecorder {
    private let engine = AVAudioEngine()
    private let mixer = AVAudioMixerNode()
    private var samples: [Float] = []
    private let lock = NSLock()
    private var isRecording = false

    private let targetFormat = AVAudioFormat(
        commonFormat: .pcmFormatFloat32,
        sampleRate: 16000,
        channels: 1,
        interleaved: false
    )!

    init() {
        engine.attach(mixer)
    }

    func startRecording() throws {
        guard !isRecording else { return }

        let inputNode = engine.inputNode
        let hardwareFormat = inputNode.inputFormat(forBus: 0)

        engine.connect(inputNode, to: mixer, format: hardwareFormat)
        engine.connect(mixer, to: engine.mainMixerNode, format: targetFormat)

        // Silence output to prevent feedback
        engine.mainMixerNode.outputVolume = 0

        lock.lock()
        samples = []
        lock.unlock()

        mixer.installTap(onBus: 0, bufferSize: 4096, format: targetFormat) { [weak self] buffer, _ in
            self?.processBuffer(buffer)
        }

        engine.prepare()
        try engine.start()
        isRecording = true
    }

    func stopRecording() -> [Float] {
        guard isRecording else { return [] }

        mixer.removeTap(onBus: 0)
        engine.stop()
        isRecording = false

        lock.lock()
        let captured = samples
        samples = []
        lock.unlock()

        return captured
    }

    private func processBuffer(_ buffer: AVAudioPCMBuffer) {
        guard let channelData = buffer.floatChannelData else { return }
        let frameCount = Int(buffer.frameLength)
        let newSamples = Array(UnsafeBufferPointer(
            start: channelData[0],
            count: frameCount
        ))

        lock.lock()
        samples.append(contentsOf: newSamples)
        lock.unlock()
    }
}
```

**Step 2: Build to verify**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/AudioRecorder.swift
git commit -m "feat: add AVAudioEngine mic recorder with 16kHz resampling"
```

---

### Task 5: Transcription service

**Files:**
- Create: `swift/Sources/ParakeetPTT/TranscriptionService.swift`

**Step 1: Write TranscriptionService**

Wraps FluidAudio's AsrModels + AsrManager. Loads model once at startup, transcribes in-memory `[Float]` audio samples. No disk I/O in the hot path.

```swift
// swift/Sources/ParakeetPTT/TranscriptionService.swift
import FluidAudio

actor TranscriptionService {
    private var models: AsrModels?
    private var manager: AsrManager?

    func loadModel() async throws {
        let models = try await AsrModels.downloadAndLoad(version: .v3)
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

**Step 2: Build to verify**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds. This is the first file that imports FluidAudio — watch for any dependency resolution issues.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/TranscriptionService.swift
git commit -m "feat: add FluidAudio transcription service with in-memory audio"
```

---

### Task 6: Paste service

**Files:**
- Create: `swift/Sources/ParakeetPTT/PasteService.swift`

**Step 1: Write PasteService**

Copies text to NSPasteboard and simulates Cmd+V via CGEvent to paste into the active field.

```swift
// swift/Sources/ParakeetPTT/PasteService.swift
import AppKit
import CoreGraphics

enum PasteService {
    static func paste(_ text: String) {
        // Copy to clipboard
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)

        // Small delay for pasteboard to propagate
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
            simulateCmdV()
        }
    }

    private static func simulateCmdV() {
        let source = CGEventSource(stateID: .combinedSessionState)

        // 0x09 = virtual key code for "V"
        let keyDown = CGEvent(keyboardEventSource: source, virtualKey: 0x09, keyDown: true)
        let keyUp = CGEvent(keyboardEventSource: source, virtualKey: 0x09, keyDown: false)

        keyDown?.flags = .maskCommand
        keyUp?.flags = .maskCommand

        keyDown?.post(tap: .cgSessionEventTap)
        keyUp?.post(tap: .cgSessionEventTap)
    }
}
```

**Step 2: Build to verify**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/PasteService.swift
git commit -m "feat: add paste service (NSPasteboard + simulated Cmd+V)"
```

---

### Task 7: Floating overlay panel

**Files:**
- Create: `swift/Sources/ParakeetPTT/OverlayPanel.swift`
- Create: `swift/Sources/ParakeetPTT/OverlayView.swift`

**Step 1: Write OverlayPanel (NSPanel subclass)**

A floating panel that appears above all windows, doesn't steal focus, and positions at top-center of the screen.

```swift
// swift/Sources/ParakeetPTT/OverlayPanel.swift
import AppKit
import SwiftUI

class OverlayPanel: NSPanel {
    init() {
        super.init(
            contentRect: NSRect(x: 0, y: 0, width: 240, height: 48),
            styleMask: [.nonactivatingPanel, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )

        level = .floating
        isFloatingPanel = true
        collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]

        titleVisibility = .hidden
        titlebarAppearsTransparent = true
        isMovableByWindowBackground = false
        backgroundColor = .clear
        isOpaque = false
        hasShadow = true
        hidesOnDeactivate = false
        animationBehavior = .utilityWindow

        standardWindowButton(.closeButton)?.isHidden = true
        standardWindowButton(.miniaturizeButton)?.isHidden = true
        standardWindowButton(.zoomButton)?.isHidden = true
    }

    override var canBecomeKey: Bool { false }
    override var canBecomeMain: Bool { false }

    func positionAtTopCenter() {
        guard let screen = NSScreen.main else { return }
        let visibleFrame = screen.visibleFrame
        let x = visibleFrame.midX - (frame.width / 2)
        let y = visibleFrame.maxY - frame.height - 20
        setFrameOrigin(NSPoint(x: x, y: y))
    }
}
```

**Step 2: Write OverlayView (SwiftUI content)**

```swift
// swift/Sources/ParakeetPTT/OverlayView.swift
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
        .padding(.horizontal, 20)
        .padding(.vertical, 12)
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

**Step 3: Build to verify**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds.

**Step 4: Commit**

```bash
git add swift/Sources/ParakeetPTT/OverlayPanel.swift swift/Sources/ParakeetPTT/OverlayView.swift
git commit -m "feat: add floating overlay panel for recording/transcribing state"
```

---

### Task 8: Menu bar view

**Files:**
- Create: `swift/Sources/ParakeetPTT/MenuBarView.swift`

**Step 1: Write MenuBarView**

The dropdown content shown when the menu bar icon is clicked.

```swift
// swift/Sources/ParakeetPTT/MenuBarView.swift
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

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds.

**Step 3: Commit**

```bash
git add swift/Sources/ParakeetPTT/MenuBarView.swift
git commit -m "feat: add menu bar dropdown view"
```

---

### Task 9: Wire everything together in the app

**Files:**
- Modify: `swift/Sources/ParakeetPTT/ParakeetApp.swift`

This is the main integration task. Replace the placeholder app with the full wiring: model loading on startup, fn key → record → transcribe → paste pipeline, overlay show/hide.

**Step 1: Replace ParakeetApp.swift with the full implementation**

```swift
// swift/Sources/ParakeetPTT/ParakeetApp.swift
import SwiftUI

@main
struct ParakeetApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra {
            MenuBarView(appState: appDelegate.appState)
        } label: {
            Label("Parakeet PTT", systemImage: appDelegate.appState.statusIcon)
        }
        .menuBarExtraStyle(.window)
    }
}
```

**Step 2: Create AppDelegate with full orchestration**

Create `swift/Sources/ParakeetPTT/AppDelegate.swift`:

```swift
// swift/Sources/ParakeetPTT/AppDelegate.swift
import AppKit
import SwiftUI

class AppDelegate: NSObject, NSApplicationDelegate {
    let appState = AppState()
    private let transcriptionService = TranscriptionService()
    private let audioRecorder = AudioRecorder()
    private let fnKeyMonitor = FnKeyMonitor()
    private var overlayPanel: OverlayPanel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        setupOverlay()
        setupFnKeyMonitor()
        loadModel()
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
            Task { @MainActor in
                appState.status = .error("Grant Accessibility permission in System Settings")
            }
        }
    }

    private func loadModel() {
        Task {
            do {
                try await transcriptionService.loadModel()
                await MainActor.run {
                    appState.status = .ready
                }
            } catch {
                await MainActor.run {
                    appState.status = .error("Model load failed: \(error.localizedDescription)")
                }
            }
        }
    }

    // MARK: - Recording pipeline

    private func startRecording() {
        Task { @MainActor in
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
        Task { @MainActor in
            guard appState.status == .recording else { return }
            appState.status = .transcribing
            updateOverlay()

            let samples = audioRecorder.stopRecording()

            guard !samples.isEmpty else {
                appState.status = .ready
                hideOverlay()
                return
            }

            do {
                let text = try await transcriptionService.transcribe(samples)
                if !text.isEmpty {
                    PasteService.paste(text)
                    appState.lastTranscription = text
                }
            } catch {
                appState.status = .error("Transcription failed: \(error.localizedDescription)")
            }

            appState.status = .ready
            hideOverlay()
        }
    }

    // MARK: - Overlay

    private func showOverlay() {
        let view = OverlayView(status: appState.status)
        overlayPanel?.contentView = NSHostingView(rootView: view)
        overlayPanel?.positionAtTopCenter()
        overlayPanel?.orderFrontRegardless()
    }

    private func updateOverlay() {
        let view = OverlayView(status: appState.status)
        overlayPanel?.contentView = NSHostingView(rootView: view)
    }

    private func hideOverlay() {
        overlayPanel?.orderOut(nil)
    }
}
```

**Step 3: Build**

```bash
cd swift && swift build 2>&1
```

Expected: Build succeeds.

**Step 4: Commit**

```bash
git add swift/Sources/ParakeetPTT/ParakeetApp.swift swift/Sources/ParakeetPTT/AppDelegate.swift
git commit -m "feat: wire up full PTT pipeline (fn key → record → transcribe → paste)"
```

---

### Task 10: Build script + gitignore

**Files:**
- Create: `scripts/build-swift.sh`
- Modify: `.gitignore`

**Step 1: Write the build script**

```bash
#!/usr/bin/env bash
# scripts/build-swift.sh — Build the parakeet-ptt Swift app
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SWIFT_DIR="$(dirname "$SCRIPT_DIR")/swift"

echo "Building parakeet-ptt..."

# Check prerequisites
if ! command -v swift &> /dev/null; then
    echo "Error: Swift not found. Install Xcode Command Line Tools:"
    echo "  xcode-select --install"
    exit 1
fi

MACOS_VERSION=$(sw_vers -productVersion | cut -d. -f1)
if [ "$MACOS_VERSION" -lt 14 ]; then
    echo "Error: macOS 14+ required (you have $(sw_vers -productVersion))"
    exit 1
fi

cd "$SWIFT_DIR"
swift build -c release 2>&1

BINARY="$SWIFT_DIR/.build/release/parakeet-ptt"
if [ -f "$BINARY" ]; then
    echo ""
    echo "Build successful: $BINARY"
    echo ""
    echo "Run with:  $BINARY"
    echo "First run downloads the CoreML model (~2.5GB)."
else
    echo "Error: Build completed but binary not found"
    exit 1
fi
```

**Step 2: Make it executable**

```bash
chmod +x scripts/build-swift.sh
```

**Step 3: Add Swift build artifacts to .gitignore**

Append to `.gitignore`:

```
# Swift build
swift/.build/
swift/Package.resolved
```

**Step 4: Commit**

```bash
git add scripts/build-swift.sh .gitignore
git commit -m "chore: add Swift build script and gitignore for swift artifacts"
```

---

### Task 11: Build, run, and test manually

**Prerequisites:**
- macOS 14+ with Apple Silicon
- Xcode Command Line Tools installed

**Step 1: Build release**

```bash
scripts/build-swift.sh
```

Expected: Build succeeds. Binary at `swift/.build/release/parakeet-ptt`.

**Step 2: Run the app**

```bash
swift/.build/release/parakeet-ptt
```

Expected:
1. Menu bar icon appears (waveform icon)
2. First run: model downloads (~2.5GB), status shows "Loading model..."
3. After model loads, status shows "Ready"
4. Hold fn for 0.5s → overlay shows "Recording..." at top-center
5. Release fn → overlay shows "Transcribing..." → text pasted into active field → overlay disappears
6. Ctrl+C (or click Quit in menu) to stop

**Step 3: Test permissions prompts**

On first run, macOS should prompt for:
- **Microphone** access (when recording starts)
- **Accessibility** access (when CGEvent tap starts — may need to add app manually in System Settings)

**Step 4: Verify existing Python tests still pass**

```bash
source venv/bin/activate && pytest -v
```

Expected: All existing tests pass (Swift changes don't affect Python).

**Step 5: Commit if everything works**

```bash
git commit --allow-empty -m "feat: parakeet-ptt pure Swift macOS menu bar app complete"
```

---

## File Summary

| Action | Path |
|--------|------|
| Create | `swift/Package.swift` |
| Create | `swift/Sources/ParakeetPTT/ParakeetApp.swift` |
| Create | `swift/Sources/ParakeetPTT/AppDelegate.swift` |
| Create | `swift/Sources/ParakeetPTT/AppState.swift` |
| Create | `swift/Sources/ParakeetPTT/FnKeyMonitor.swift` |
| Create | `swift/Sources/ParakeetPTT/AudioRecorder.swift` |
| Create | `swift/Sources/ParakeetPTT/TranscriptionService.swift` |
| Create | `swift/Sources/ParakeetPTT/PasteService.swift` |
| Create | `swift/Sources/ParakeetPTT/OverlayPanel.swift` |
| Create | `swift/Sources/ParakeetPTT/OverlayView.swift` |
| Create | `swift/Sources/ParakeetPTT/MenuBarView.swift` |
| Create | `scripts/build-swift.sh` |
| Modify | `.gitignore` |

## Known Risks

1. **FluidAudio `[Float]` transcribe path:** The `transcribe(_ audioSamples: [Float], source:)` overload expects 16kHz mono. The AudioRecorder outputs this format via the mixer node, but verify at build time that no additional format conversion is needed.
2. **First-run model download:** ~2.5GB download on first launch. The app should remain responsive during this (model loads on a background Task, UI shows "Loading model...").
3. **Accessibility permission:** CGEvent tap creation will fail silently if permission isn't granted. The app detects this and shows an error in the menu bar status.
4. **Swift concurrency:** `AppDelegate` methods mix `@MainActor` and non-isolated code. The `TranscriptionService` is an `actor` to ensure thread safety. `FnKeyMonitor` callbacks dispatch to main queue.
