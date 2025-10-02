#!/bin/bash
# Build GZDoom Launcher.app as standalone bundle with py2app

set -e

echo "Building GZDoom Launcher.app with py2app..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "GZDoom Launcher.app"

# Generate icon if needed
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
    iconutil -c icns doom-launcher.iconset -o doom-launcher.icns
    rm -rf doom-launcher.iconset
    echo "Icon generated successfully"
else
    echo "Warning: doom-launcher.png not found, skipping icon generation"
fi

# Install py2app if not already installed
echo "Ensuring py2app is installed..."
pip3 install --quiet py2app 2>/dev/null || true

# Build with py2app
echo "Building standalone app bundle..."
python3 setup.py py2app

# Move from dist to current directory
if [ -d "dist/GZDoom Launcher.app" ]; then
    mv "dist/GZDoom Launcher.app" .
    rm -rf build dist
    echo ""
    echo "✓ Build complete: GZDoom Launcher.app"
    echo ""
    echo "This is a standalone app with Python and PySide6 bundled."
    echo ""
    echo "To install to Applications folder:"
    echo "  cp -R \"GZDoom Launcher.app\" ~/Applications/"
    echo ""
else
    echo "Error: Build failed"
    exit 1
fi
