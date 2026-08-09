#!/usr/bin/env bash
# scripts/package-dmg.sh — Optional local .app / DMG helper.
# Not the supported install path. Preferred: ./scripts/build-swift.sh && run the binary.
# No public releases, notarization, or auto-update feed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SWIFT_DIR="$PROJECT_DIR/swift"
BUILD_DIR="$PROJECT_DIR/build"
APP_NAME="Kuaishuo"
APP_BUNDLE="$BUILD_DIR/$APP_NAME.app"
DMG_NAME="$APP_NAME.dmg"
DMG_PATH="$PROJECT_DIR/$DMG_NAME"
VERSION="1.0.0"

echo "=== Kuaishuo — DMG Packager ==="
echo ""

# Prefer swift.org toolchain over CLT to avoid PackageDescription ABI mismatch
TOOLCHAIN_DIR="$HOME/Library/Developer/Toolchains/swift-6.2.3-RELEASE.xctoolchain/usr/bin"
if [ -d "$TOOLCHAIN_DIR" ]; then
    echo "Using swift.org toolchain"
    export PATH="$TOOLCHAIN_DIR:$PATH"
fi

# --- Step 1: Build binary ---
BUILD_MODE="${BUILD_MODE:-debug}"
echo "[1/4] Building binary ($BUILD_MODE)..."
cd "$SWIFT_DIR"
swift build -c "$BUILD_MODE" 2>&1

if [ "$BUILD_MODE" = "release" ]; then
    BINARY="$SWIFT_DIR/.build/release/kuaishuo"
else
    BINARY="$SWIFT_DIR/.build/debug/kuaishuo"
fi
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
cp "$BINARY" "$APP_BUNDLE/Contents/MacOS/kuaishuo"

# Write Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Kuaishuo</string>
    <key>CFBundleDisplayName</key>
    <string>Kuaishuo</string>
    <key>CFBundleIdentifier</key>
    <string>com.devvor.kuaishuo</string>
    <key>CFBundleExecutable</key>
    <string>kuaishuo</string>
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
    <string>Kuaishuo needs microphone access to record speech for transcription.</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

echo "  Bundle: $APP_BUNDLE"

# --- Step 2b: Code signing ---
SIGNING_IDENTITY="${CODESIGN_IDENTITY:--}"
if [ "$SIGNING_IDENTITY" = "-" ]; then
    echo "  Signing: ad-hoc (local use only)"
    echo "  For distribution, set CODESIGN_IDENTITY='Developer ID Application: Your Name'"
else
    echo "  Signing: $SIGNING_IDENTITY"
fi
codesign --force --sign "$SIGNING_IDENTITY" \
    --entitlements /dev/stdin \
    "$APP_BUNDLE/Contents/MacOS/kuaishuo" << 'ENTITLEMENTS'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.device.audio-input</key>
    <true/>
</dict>
</plist>
ENTITLEMENTS

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
echo "Optional local package only (not a public release)."
echo "Preferred install: ./scripts/build-swift.sh && run the printed binary path."
echo ""
echo "If you use this DMG on your machine:"
echo "  1. Open $DMG_NAME"
echo "  2. Drag Kuaishuo to Applications"
echo "  3. Right-click > Open if macOS blocks the unsigned app"
echo "  4. Grant Microphone + Accessibility permissions when prompted"
