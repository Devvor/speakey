#!/usr/bin/env bash
# scripts/build-swift.sh — Build the parakeet-ptt Swift app
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SWIFT_DIR="$(dirname "$SCRIPT_DIR")/swift"
BUILD_MODE="${1:-debug}"

echo "=== Parakeet PTT — Swift Builder ==="
echo ""

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

# Prefer swift.org toolchain over CLT to avoid PackageDescription ABI mismatch
# (CLT 26.x has a known bug where libPackageDescription.dylib symbols don't match)
TOOLCHAIN_DIR="$HOME/Library/Developer/Toolchains/swift-6.2.3-RELEASE.xctoolchain/usr/bin"
if [ -d "$TOOLCHAIN_DIR" ]; then
    echo "Using swift.org toolchain at $TOOLCHAIN_DIR"
    export PATH="$TOOLCHAIN_DIR:$PATH"
else
    echo "Using system Swift ($(swift --version 2>&1 | head -1))"
    echo "If the build fails with 'Undefined symbols for PackageDescription',"
    echo "install the swift.org toolchain:"
    echo "  curl -O https://download.swift.org/swift-6.2.3-release/xcode/swift-6.2.3-RELEASE/swift-6.2.3-RELEASE-osx.pkg"
    echo "  installer -pkg swift-6.2.3-RELEASE-osx.pkg -target CurrentUserHomeDirectory"
    echo ""
fi

cd "$SWIFT_DIR"

if [ "$BUILD_MODE" = "release" ]; then
    echo "Building in release mode..."
    swift build -c release 2>&1
    BINARY="$SWIFT_DIR/.build/release/parakeet-ptt"
else
    echo "Building in debug mode..."
    swift build 2>&1
    BINARY="$SWIFT_DIR/.build/debug/parakeet-ptt"
fi

if [ -f "$BINARY" ]; then
    echo ""
    echo "Build successful: $BINARY"
    echo "Size: $(du -h "$BINARY" | cut -f1)"
    echo ""
    echo "Run with:  $BINARY"
    echo "First run downloads the CoreML model (~2.5GB)."
    echo ""
    echo "Required macOS permissions:"
    echo "  - Accessibility (System Settings > Privacy > Accessibility)"
    echo "  - Microphone   (System Settings > Privacy > Microphone)"
else
    echo "Error: Build completed but binary not found"
    exit 1
fi
