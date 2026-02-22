# parakeet-ptt: Pure Swift Push-to-Talk macOS App

**Goal:** A standalone macOS menu bar app that provides push-to-talk speech-to-text using CoreML/Apple Neural Engine via [FluidAudio](https://github.com/FluidInference/FluidAudio) (v0.12.1). Hold fn to record, release to transcribe and paste.

**Replaces:** The previous plan (`2026-02-22-coreml-ane-backend.md`) proposed a Python subprocess bridge to a Swift CLI. This design replaces that with a pure Swift app — zero Python involvement, zero per-call overhead, model loaded once and kept warm.

---

## Architecture

```
parakeet-ptt.app (SwiftUI menu bar app)
├── App lifecycle      — SwiftUI @main, NSApplication (no dock icon)
├── MenuBarExtra       — persistent menu bar icon + dropdown
├── CGEvent tap        — fn key hold/release detection
├── AVAudioEngine      — mic capture into PCM buffer
├── FluidAudio         — CoreML/ANE transcription (model loaded once)
├── Floating overlay   — SwiftUI window at top-center (recording/transcribing)
└── NSPasteboard + CGEvent — paste result via Cmd+V
```

### Data Flow

```
fn held >0.5s
    │
    ▼
AVAudioEngine starts → captures mic audio into PCM buffer (in memory)
    │
fn released
    │
    ▼
AVAudioEngine stops → PCM buffer passed to FluidAudio (no disk I/O)
    │
    ▼
FluidAudio transcribes via CoreML on ANE → text result
    │
    ▼
NSPasteboard.general.setString(text) → simulated Cmd+V → text pasted
```

Key difference from Python fn-ptt: no temp WAV file. Audio goes from mic buffer directly to FluidAudio in-memory (if the API supports it — fallback to temp file if it only accepts URLs).

---

## App States

| State | Trigger | Menu Bar Icon | Floating Overlay |
|-------|---------|---------------|-----------------|
| **Idle** | App launched, model loaded | Mic icon | Hidden |
| **Recording** | fn held >0.5s | Red/active indicator | "Recording..." pill with red accent |
| **Transcribing** | fn released (after recording) | Spinner indicator | "Transcribing..." pill with spinner |
| **Done** | Transcription complete | Returns to mic icon | Disappears |
| **Loading** | App startup, model downloading | Dimmed icon | Optional loading indicator |

---

## UI Components

### Menu Bar

```
┌──────────────────────────────────────┐
│  Wi-Fi  BT  🎙  Battery  Clock      │
│              │                       │
│              ├───────────────┐       │
│              │ ● Ready       │       │
│              │ ──────────────│       │
│              │ Hold fn to talk│      │
│              │ ──────────────│       │
│              │ Quit          │       │
│              └───────────────┘       │
└──────────────────────────────────────┘
```

SwiftUI `MenuBarExtra` with:
- Status indicator (Ready / Recording / Transcribing)
- Usage hint
- Quit button

No dock icon (`LSUIElement = true` or `Application is agent` in Info.plist).

### Floating Overlay

```
Recording state:
┌───────────────────────────┐
│  ●  Recording...          │
└───────────────────────────┘
     (top-center, pill shape, red accent)

Transcribing state:
┌───────────────────────────┐
│  ◦  Transcribing...       │
└───────────────────────────┘
     (same position, spinner/pulse)
```

- SwiftUI overlay window (`.panel` style, floats above all windows)
- Positioned at top-center of main screen
- Rounded pill shape with vibrancy/blur (`.ultraThinMaterial`)
- Appears on recording start, disappears when transcription completes and text is pasted

---

## Coexistence with Python fn-ptt

Both tools live in the same repo, independently:

```
src/fn_ptt/        ← Python fn-ptt (stays as-is, works with NeMo/MLX)
swift/             ← Pure Swift parakeet-ptt (new, uses CoreML/ANE)
```

No integration between them. Users choose which to use based on their setup.

---

## Requirements

- **macOS 14+** (Sonoma or later)
- **Apple Silicon** (M1/M2/M3/M4)
- **Xcode Command Line Tools** (`xcode-select --install`)
- **Swift 5.10+** (ships with Xcode 15.3+)
- **Permissions:** Accessibility (Input Monitoring) + Microphone

---

## Tech Stack

- **SwiftUI** — app lifecycle, menu bar, overlay UI
- **FluidAudio v0.12.1** — CoreML/ANE transcription (Swift Package)
- **AVAudioEngine** — microphone capture
- **Quartz/CoreGraphics** — CGEvent tap for fn key, simulated Cmd+V
- **AppKit** — NSPasteboard for clipboard

---

## Known Risks

1. **FluidAudio audio input API:** May only accept file URLs, not in-memory buffers. If so, fall back to writing a temp WAV file (same as Python fn-ptt, adds ~5ms).
2. **FluidAudio ASRResult token timing properties:** Underdocumented. Not needed for PTT (we only need `result.text`), but worth noting.
3. **First-run model download:** FluidAudio downloads ~2.5GB CoreML model on first use. Need to handle this gracefully in the UI (loading state).
4. **Accessibility permissions:** CGEvent tap requires Input Monitoring permission. App needs to detect and guide the user if not granted.

---

## Build & Run

```bash
# Build
cd swift && swift build -c release

# Run
swift/.build/release/parakeet-ptt

# Or via build script
scripts/build-swift.sh
```
