# Parakeet STT - Daemon Mode Usage Guide

## Overview

Daemon mode runs Parakeet STT as a background service that you control via CLI commands. This **avoids the pynput/PyObjC compatibility issues** by using inter-process communication instead of global hotkeys.

## Architecture

```
Background Daemon Process
├── IPC Server (Unix socket)
├── Recording Controller
├── Audio Recorder
├── Transcription Model
└── Status Overlay (visual feedback)

CLI Commands → Unix Socket → Daemon
```

## Quick Start

### 1. Start the Daemon

```bash
cd /Users/samuel/Desktop/.personal/parakeet-stt-phase-4
source venv/bin/activate
parakeet-stt daemon start
```

**Output:**
```
✓ Daemon started
Socket: /Users/samuel/.parakeet-stt/daemon.sock
Log: /Users/samuel/.parakeet-stt/daemon.log

Control recording with:
  parakeet-stt record
```

The daemon runs in the background and shows a status overlay on your screen.

### 2. Control Recording

**Toggle recording on/off:**
```bash
parakeet-stt record
```

**Explicit start/stop:**
```bash
parakeet-stt record start    # Start recording
parakeet-stt record stop     # Stop and transcribe
```

### 3. Check Daemon Status

```bash
parakeet-stt daemon status
```

**Output:**
```
✓ Daemon is running
PID: 12345
Socket: /Users/samuel/.parakeet-stt/daemon.sock
Log: /Users/samuel/.parakeet-stt/daemon.log
```

### 4. Stop the Daemon

```bash
parakeet-stt daemon stop
```

## Workflow

1. **Start daemon** (once)
2. **Trigger recording** via CLI command
3. **Speak into microphone**
4. **Stop recording** via CLI command
5. **Text auto-copies to clipboard**

## Binding to System Shortcuts

You can bind the `parakeet-stt record` command to macOS keyboard shortcuts:

### Option 1: macOS Shortcuts App

1. Open **System Settings → Keyboard → Keyboard Shortcuts**
2. Click **App Shortcuts** → **+**
3. Choose **All Applications**
4. Menu Title: (leave blank)
5. Keyboard Shortcut: (choose your hotkey, e.g., ⌘⇧R)
6. Create a Quick Action in **Shortcuts.app** that runs:
   ```bash
   /Users/samuel/Desktop/.personal/parakeet-stt-phase-4/venv/bin/parakeet-stt record
   ```

### Option 2: Alfred/Raycast

Create a workflow/script command:
```bash
source /Users/samuel/Desktop/.personal/parakeet-stt-phase-4/venv/bin/activate
parakeet-stt record
```

### Option 3: Simple Shell Script

Create `~/bin/record-voice.sh`:
```bash
#!/bin/bash
source /Users/samuel/Desktop/.personal/parakeet-stt-phase-4/venv/bin/activate
parakeet-stt record
```

Make executable: `chmod +x ~/bin/record-voice.sh`

Bind to hotkey using tools like:
- BetterTouchTool
- Karabiner-Elements
- Hammerspoon

## Visual Feedback

The daemon shows an overlay in the corner of your screen:

- **🟢 Idle** - Ready to record
- **🔴 Recording** - Microphone is active
- **🟡 Transcribing** - Processing audio
- **✓ Done** - Transcription complete (text copied)

Overlay position can be configured in `~/.parakeet-stt/config.yaml` (future feature).

## Troubleshooting

### Daemon won't start

Check the log file:
```bash
tail -f ~/.parakeet-stt/daemon.log
```

### "Daemon is not running" error

Verify status:
```bash
parakeet-stt daemon status
```

If stuck, clean up and restart:
```bash
rm ~/.parakeet-stt/daemon.pid
rm ~/.parakeet-stt/daemon.sock
parakeet-stt daemon start
```

### No audio recorded

Check microphone permissions:
- System Settings → Privacy & Security → Microphone
- Grant permission to Terminal (or your terminal app)

### Model loading issues

The first start may take time to download the model (~2.4GB):
```bash
tail -f ~/.parakeet-stt/daemon.log
```

## Advantages Over PTT Mode

✅ **No pynput issues** - Uses IPC instead of global hotkeys
✅ **More reliable** - Simpler architecture, fewer dependencies
✅ **Flexible triggering** - CLI, shortcuts, scripts, automations
✅ **Better integration** - Works with all automation tools
✅ **Persistent** - Daemon stays running, instant response

## Files

- **PID file:** `~/.parakeet-stt/daemon.pid`
- **Unix socket:** `~/.parakeet-stt/daemon.sock`
- **Log file:** `~/.parakeet-stt/daemon.log`

## Commands Summary

```bash
# Daemon management
parakeet-stt daemon start     # Start background daemon
parakeet-stt daemon stop      # Stop daemon
parakeet-stt daemon status    # Check if running

# Recording control
parakeet-stt record           # Toggle recording
parakeet-stt record start     # Start recording
parakeet-stt record stop      # Stop and transcribe
```

## What Happened to PTT Mode?

PTT (push-to-talk) mode with global hotkeys is still available via:
```bash
parakeet-stt ptt --hotkey cmd_r
```

However, it has compatibility issues with Python/pynput on macOS. Daemon mode is the recommended approach for reliability.
