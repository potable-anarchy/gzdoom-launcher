#!/bin/bash
# Build GZDoom Launcher.app from source files

set -e

APP_NAME="GZDoom Launcher.app"
APP_DIR="$APP_NAME/Contents"

echo "Building $APP_NAME..."

# Clean existing app bundle
if [ -d "$APP_NAME" ]; then
    echo "Removing existing app bundle..."
    rm -rf "$APP_NAME"
fi

# Create app bundle structure
echo "Creating app bundle structure..."
mkdir -p "$APP_DIR/MacOS"
mkdir -p "$APP_DIR/Resources"

# Copy launcher script
echo "Installing launcher script..."
cat > "$APP_DIR/MacOS/launcher" << 'EOF'
#!/bin/bash

# Get the Resources directory inside the app bundle
RESOURCES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../Resources" && pwd)"

# Launch the GUI Python script directly
cd "$RESOURCES_DIR"
python3 doom-launcher-gui.py
EOF
chmod +x "$APP_DIR/MacOS/launcher"

# Copy Python scripts
echo "Installing Python scripts..."
cp doom-launcher-gui.py "$APP_DIR/Resources/"
cp doom-launcher.py "$APP_DIR/Resources/"

# Copy documentation
echo "Installing documentation..."
cp LICENSE "$APP_DIR/Resources/"
cp README.md "$APP_DIR/Resources/"

# Generate icon
echo "Generating app icon..."
if [ -f "doom-launcher.png" ]; then
    # Create iconset
    rm -rf doom-launcher.iconset
    mkdir doom-launcher.iconset

    sips -z 16 16 doom-launcher.png --out doom-launcher.iconset/icon_16x16.png > /dev/null
    sips -z 32 32 doom-launcher.png --out doom-launcher.iconset/icon_16x16@2x.png > /dev/null
    sips -z 32 32 doom-launcher.png --out doom-launcher.iconset/icon_32x32.png > /dev/null
    sips -z 64 64 doom-launcher.png --out doom-launcher.iconset/icon_32x32@2x.png > /dev/null
    sips -z 128 128 doom-launcher.png --out doom-launcher.iconset/icon_128x128.png > /dev/null
    sips -z 256 256 doom-launcher.png --out doom-launcher.iconset/icon_128x128@2x.png > /dev/null
    sips -z 256 256 doom-launcher.png --out doom-launcher.iconset/icon_256x256.png > /dev/null
    sips -z 512 512 doom-launcher.png --out doom-launcher.iconset/icon_512x512.png > /dev/null
    sips -z 1024 1024 doom-launcher.png --out doom-launcher.iconset/icon_512x512@2x.png > /dev/null

    # Convert to icns
    iconutil -c icns doom-launcher.iconset -o "$APP_DIR/Resources/AppIcon.icns"
    rm -rf doom-launcher.iconset
    echo "Icon generated successfully"
else
    echo "Warning: doom-launcher.png not found, skipping icon generation"
fi

# Create Info.plist
echo "Creating Info.plist..."
cat > "$APP_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.gzdoom.launcher</string>
    <key>CFBundleName</key>
    <string>GZDoom Launcher</string>
    <key>CFBundleDisplayName</key>
    <string>GZDoom Launcher</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <false/>
    <key>LSBackgroundOnly</key>
    <false/>
</dict>
</plist>
EOF

echo ""
echo "✓ Build complete: $APP_NAME"
echo ""
echo "To install to Applications folder:"
echo "  cp -R \"$APP_NAME\" ~/Applications/"
echo ""
