# Implementation Flows: PTT and Daemon Modes

> **Last Updated:** 2026-02-21
> **Scope:** Internal component interactions for push-to-talk (PTT) and daemon recording modes

---

## Overview

Both modes share the same audio recording and transcription pipeline but differ in how they are triggered and how they manage the model lifecycle.

| | PTT Mode | Daemon Mode |
|---|---|---|
| **Entry point** | `parakeet-stt ptt` | `parakeet-stt daemon start` |
| **Trigger** | Hold a hotkey | CLI command over Unix socket |
| **Process model** | Single foreground process | Persistent background subprocess |
| **Model loading** | Eager (on startup) | Lazy (on first `record stop`) |
| **Recorder init** | Eager (on startup) | Lazy (on first `record start`) |
| **UI feedback** | `StatusOverlay` (tkinter window) | Log file only (overlay disabled) |

---

## PTT Mode

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant PTTApp
    participant StatusOverlay
    participant PTTController
    participant HotkeyListener
    participant AudioRecorder
    participant ModelWrapper
    participant NeMo

    User->>CLI: parakeet-stt ptt
    CLI->>PTTApp: PTTApp(config).start()
    PTTApp->>StatusOverlay: create (tkinter window)
    PTTApp->>PTTController: create
    PTTController->>HotkeyListener: create (pynput)
    PTTController->>AudioRecorder: create
    PTTController->>ModelWrapper: load_model() ⏳ ~10s first time
    ModelWrapper->>NeMo: ASRModel.from_pretrained(...)
    PTTApp->>PTTController: start() [background thread]
    PTTApp->>StatusOverlay: start() [blocks main thread]
    PTTController-->>StatusOverlay: state → idle 🟢

    Note over User,NeMo: Recording Cycle

    User->>HotkeyListener: press hotkey
        HotkeyListener->>PTTController: on_press()
        PTTController-->>StatusOverlay: state → holding
        Note over PTTController: polls every 100ms

        alt released before hold_threshold (default 2s)
            User->>HotkeyListener: release hotkey
            HotkeyListener->>PTTController: on_release()
            PTTController-->>StatusOverlay: state → idle 🟢
        else held ≥ hold_threshold
            PTTController->>AudioRecorder: start()
            AudioRecorder->>AudioRecorder: open sd.InputStream (16kHz mono)
            PTTController-->>StatusOverlay: state → recording 🔴

            loop every ~64ms
                AudioRecorder->>AudioRecorder: _audio_callback → append chunk to buffer
            end

            User->>HotkeyListener: release hotkey
            HotkeyListener->>PTTController: on_release()
            PTTController->>AudioRecorder: stop()
            AudioRecorder->>AudioRecorder: concatenate buffer → numpy array
            PTTController-->>StatusOverlay: state → transcribing 🟡
            PTTController->>AudioRecorder: save_audio(tmp.wav) [float32 → int16]
            PTTController->>ModelWrapper: transcribe(tmp.wav)
            ModelWrapper->>NeMo: model.transcribe([path], timestamps=False)
            NeMo-->>ModelWrapper: text
            ModelWrapper-->>PTTController: {"text": "..."}
            PTTController->>PTTController: unlink(tmp.wav)
            PTTController->>PTTController: pyperclip.copy(text)
            PTTController-->>StatusOverlay: state → done ✓
            Note over PTTController: 2s timer
            PTTController-->>StatusOverlay: state → idle 🟢
        end
```

### State Machine

```mermaid
stateDiagram-v2
    [*] --> idle : app start

    idle --> holding : hotkey pressed
    holding --> idle : released before threshold
    holding --> recording : held ≥ threshold / recorder.start()

    recording --> transcribing : hotkey released / recorder.stop()
    transcribing --> done : transcribe complete / pyperclip.copy()

    done --> idle : after 2 seconds
```

---

## Daemon Mode

### Sequence Diagram

The daemon involves **two separate processes**: the short-lived CLI process that sends commands, and the persistent daemon process that executes them.

```mermaid
sequenceDiagram
    actor User
    participant CLI as CLI Process
    participant Manager as DaemonManager
    participant DaemonProc as Daemon Process
    participant IPCServer
    participant DaemonApp
    participant Controller as DaemonRecordingController
    participant AudioRecorder
    participant ModelWrapper
    participant NeMo

    Note over User,NeMo: Startup

        User->>CLI: parakeet-stt daemon start
        CLI->>Manager: DaemonManager().start()
        Manager->>DaemonProc: subprocess.Popen(run_daemon.py, start_new_session=True)
        Note over Manager: writes PID → ~/.parakeet-stt/daemon.pid
        Manager-->>CLI: True
        CLI-->>User: ✓ Daemon started

        DaemonProc->>DaemonApp: DaemonApp(runtime_dir)
        DaemonApp->>IPCServer: create + start()
        IPCServer->>IPCServer: bind socket ~/.parakeet-stt/daemon.sock
        IPCServer->>IPCServer: _listen() [background thread]
        DaemonApp->>DaemonApp: while True: sleep(1)
        Note over DaemonApp: main thread parks - IPC thread handles all work

    Note over User,NeMo: Record Start

        User->>CLI: parakeet-stt record
        CLI->>Manager: is_running()? → True
        CLI->>CLI: IPCClient(socket_path)
        CLI->>IPCServer: connect + send {"command": "record_toggle"}
        IPCServer->>DaemonApp: on_message(message) [handler thread]
        DaemonApp->>Controller: toggle_recording() [state=idle]
        Controller->>AudioRecorder: lazy init (first call only)
        Controller->>AudioRecorder: start() → sd.InputStream
        Controller->>Controller: state → recording 🔴
        DaemonApp-->>IPCServer: {"status": "ok", "message": "Recording started"}
        IPCServer-->>CLI: JSON response
        CLI-->>User: ✓ Recording started

        loop every ~64ms
            AudioRecorder->>AudioRecorder: _audio_callback → append chunk to buffer
        end

    Note over User,NeMo: Record Stop

        User->>CLI: parakeet-stt record
        CLI->>IPCServer: connect + send {"command": "record_toggle"}
        Note over CLI: timeout=60s (model may need to load)
        IPCServer->>DaemonApp: on_message(message) [handler thread]
        DaemonApp->>Controller: toggle_recording() [state=recording]
        Controller->>AudioRecorder: stop()
        AudioRecorder->>AudioRecorder: concatenate buffer → numpy array
        Controller->>Controller: state → transcribing 🟡
        Controller->>AudioRecorder: save_audio(tmp.wav) [float32 → int16]
        Controller->>ModelWrapper: lazy init + load_model() ⏳ first call only
        ModelWrapper->>NeMo: ASRModel.from_pretrained(...)
        Controller->>ModelWrapper: transcribe(tmp.wav)
        ModelWrapper->>NeMo: model.transcribe([path], timestamps=False)
        NeMo-->>ModelWrapper: text
        ModelWrapper-->>Controller: {"text": "..."}
        Controller->>Controller: unlink(tmp.wav)
        Controller->>Controller: pyperclip.copy(text)
        Controller->>DaemonApp: on_transcription_complete(text) [logs to file]
        Controller->>Controller: state → done ✓
        Note over Controller: 2s timer
        Controller->>Controller: state → idle 🟢
        DaemonApp-->>IPCServer: {"status": "ok", "text": "...", "message": "Transcription complete"}
        IPCServer-->>CLI: JSON response
        CLI-->>User: ✓ Transcription complete + text
```

### State Machine (Daemon Controller)

```mermaid
stateDiagram-v2
    [*] --> idle : daemon start

    idle --> recording : record_start or toggle / recorder.start()
    recording --> transcribing : record_stop or toggle / recorder.stop()
    transcribing --> done : transcribe complete / pyperclip.copy()

    done --> idle : after 2 seconds

    note right of idle : error in any state → resets to idle
```

---

## Shared Transcription Pipeline

Both modes funnel through the same pipeline once audio is captured:

```
AudioRecorder.stop()
        │
        ▼
  np.concatenate(buffer)          ← raw float32 numpy array
        │
        ▼
  AudioRecorder.save_audio()      ← convert float32 → int16, write .wav
        │
        ▼
  ModelWrapper.transcribe(path)
        │
        ▼
  Backend.transcribe(path)        ← NeMoBackend or MLXBackend
        │
        ▼
  model.transcribe([path],        ← full-file batch inference
      timestamps=False)           ← (no chunking; entire recording at once)
        │
        ▼
  {"text": "transcription..."}
        │
        ▼
  pyperclip.copy(text)            ← auto-copies to clipboard
```

---

## Key Differences in Model Lifecycle

### PTT Mode — Eager Loading
```
parakeet-stt ptt
    └─▶ PTTController.__init__()
            └─▶ ModelWrapper(config)     ← loads immediately on startup
                    └─▶ NeMo model loaded into memory (~2.4 GB)
                            └─▶ Ready before first recording
```

**Implication:** First keystroke is instant; startup takes ~10s.

### Daemon Mode — Lazy Loading
```
parakeet-stt daemon start
    └─▶ DaemonApp starts (fast, model NOT loaded)

parakeet-stt record        (first record start)
    └─▶ AudioRecorder lazy-init  ← happens here

parakeet-stt record        (first record stop)
    └─▶ ModelWrapper lazy-init   ← ~10s delay on first stop only
            └─▶ NeMo model loaded into memory
                    └─▶ All subsequent stops are fast
```

**Implication:** Daemon starts instantly; the first `record stop` has a ~10s delay for model loading.
