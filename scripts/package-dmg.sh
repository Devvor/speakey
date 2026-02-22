#!/usr/bin/env bash
# scripts/package-dmg.sh — Build .app bundle and create .dmg for distribution
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SWIFT_DIR="$PROJECT_DIR/swift"
BUILD_DIR="$PROJECT_DIR/build"
APP_NAME="ParakeetPTT"
APP_BUNDLE="$BUILD_DIR/$APP_NAME.app"
DMG_NAME="$APP_NAME.dmg"
DMG_PATH="$PROJECT_DIR/$DMG_NAME"
VERSION="1.0.0"

echo "=== Parakeet PTT — DMG Packager ==="
echo ""

# --- Step 1: Build release binary ---
echo "[1/4] Building release binary..."
cd "$SWIFT_DIR"
swift build -c release 2>&1

BINARY="$SWIFT_DIR/.build/release/parakeet-ptt"
if [ ! -f "$BINARY" ]; then
    echo "Error: Binary not found at $BINARY"
    exit 1
fi
echo "  Binary: $BINARY"

# --- Step 2: Create .app bundle ---
echo "[2/4] Creating .app bundle..."
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"

# Copy binary
cp "$BINARY" "$APP_BUNDLE/Contents/MacOS/parakeet-ptt"

# Write Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Parakeet PTT</string>
    <key>CFBundleDisplayName</key>
    <string>Parakeet PTT</string>
    <key>CFBundleIdentifier</key>
    <string>com.parakeet.ptt</string>
    <key>CFBundleExecutable</key>
    <string>parakeet-ptt</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSUIElement</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSMicrophoneUsageDescription</key>
    <string>Parakeet PTT needs microphone access to record speech for transcription.</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

echo "  Bundle: $APP_BUNDLE"

# --- Step 3: Create DMG ---
echo "[3/4] Creating DMG..."

# Clean up previous DMG
rm -f "$DMG_PATH"

# Create a temporary directory for DMG contents
DMG_STAGING="$BUILD_DIR/dmg-staging"
rm -rf "$DMG_STAGING"
mkdir -p "$DMG_STAGING"

# Copy .app into staging
cp -R "$APP_BUNDLE" "$DMG_STAGING/"

# Create Applications symlink
ln -s /Applications "$DMG_STAGING/Applications"

# Create DMG from staging directory
hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$DMG_STAGING" \
    -ov \
    -format UDZO \
    "$DMG_PATH" \
    2>&1

# Clean up staging
rm -rf "$DMG_STAGING"

echo "  DMG: $DMG_PATH"

# --- Step 4: Summary ---
echo ""
echo "[4/4] Done!"
echo ""
echo "  DMG:     $DMG_PATH"
echo "  Size:    $(du -h "$DMG_PATH" | cut -f1)"
echo ""
echo "To install:"
echo "  1. Open $DMG_NAME"
echo "  2. Drag Parakeet PTT to Applications"
echo "  3. Right-click > Open (first launch only, bypasses Gatekeeper)"
echo "  4. Grant Microphone + Accessibility permissions when prompted"
