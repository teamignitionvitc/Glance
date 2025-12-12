#!/bin/bash
set -e

APP_NAME="glance"
VERSION="1.0.0"
APP_DIR="Glance.AppDir"
DIST_DIR="dist"
PYTHON_EXEC="/home/mhdramzy/.globalenv/bin/python3"

echo "Starting AppImage build for $APP_NAME..."

# Ensure binary exists, if not build it
if [ ! -f "$DIST_DIR/$APP_NAME" ]; then
    echo "Binary not found. Building..."
    "$PYTHON_EXEC" -m PyInstaller --noconfirm --onefile --windowed --name "$APP_NAME" \
        --add-data "docs:docs" \
        --hidden-import "PySide6" \
        --hidden-import "pyqtgraph" \
        --hidden-import "serial" \
        --hidden-import "numpy" \
        main.py
fi

# Clean up previous AppDir
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/pixmaps"

# Copy binary
cp "$DIST_DIR/$APP_NAME" "$APP_DIR/usr/bin/"

# Copy AppRun
cp "packaging/AppRun" "$APP_DIR/"
chmod +x "$APP_DIR/AppRun"

# Copy Icon
# AppImage spec expects the icon to be at the root of AppDir AND in standard paths like /usr/share/pixmaps
cp "docs/public/Glance_nobg_jl.png" "$APP_DIR/glance.png"
cp "docs/public/Glance_nobg_jl.png" "$APP_DIR/.DirIcon"
cp "docs/public/Glance_nobg_jl.png" "$APP_DIR/usr/share/pixmaps/glance.png"

# Copy Desktop file
cp "packaging/glance.desktop" "$APP_DIR/"

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "Generating AppImage..."
# ARCH=x86_64 ./appimagetool-x86_64.AppImage "$APP_DIR" "Glance-${VERSION}-x86_64.AppImage"
# Using --appimage-extract-and-run if FUSE is not available (common in containers/some envs)
ARCH=x86_64 ./appimagetool-x86_64.AppImage --appimage-extract-and-run "$APP_DIR" "Glance-${VERSION}-x86_64.AppImage"

echo "AppImage created: Glance-${VERSION}-x86_64.AppImage"
ls -lh "Glance-${VERSION}-x86_64.AppImage"
