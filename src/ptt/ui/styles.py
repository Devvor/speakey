"""UI styling for status overlay."""

# State colors
STATE_COLORS = {
    "idle": "#6c757d",        # Gray
    "holding": "#ffc107",     # Yellow/amber
    "recording": "#dc3545",   # Red
    "transcribing": "#0d6efd",  # Blue
    "done": "#198754",        # Green
}

# State messages
STATE_MESSAGES = {
    "idle": "Ready",
    "holding": "Hold to record...",
    "recording": "● Recording",
    "transcribing": "Transcribing...",
    "done": "✓ Copied to clipboard",
}

# Window dimensions
WINDOW_WIDTH = 280
WINDOW_HEIGHT = 80
PADDING = 20

# Font settings
FONT_FAMILY = "SF Pro Display"  # Mac default
FONT_SIZE = 14
FONT_WEIGHT = "bold"
