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
