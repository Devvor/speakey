#!/usr/bin/env python
"""Daemon runner script - handles module imports correctly."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Now we can import the app
from src.daemon.app import main

if __name__ == "__main__":
    main()
