#!/bin/bash
set -e

# Define variables
APP_NAME="glance"
VERSION="1.0.0"
DEB_DIR="${APP_NAME}_deb"
DIST_DIR="dist"
BUILD_DIR="build"
PYTHON_EXEC="/home/mhdramzy/.globalenv/bin/python3"

echo "Starting build process for $APP_NAME version $VERSION..."
echo "Using Python environment: $PYTHON_EXEC"

# Ensure the Python executable exists
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "Error: Python executable not found at $PYTHON_EXEC"
    exit 1
fi

# Install dependencies (attempt)
echo "Installing/Verifying dependencies..."
"$PYTHON_EXEC" -m pip install pyinstaller
if [ -f "requirements.txt" ]; then
    "$PYTHON_EXEC" -m pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found!"
fi

# Clean previous builds
echo "Cleaning up previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR" "$DEB_DIR" *.spec

# Build with PyInstaller
echo "Building executable with PyInstaller..."
# Using python -m PyInstaller ensures we use the one installed in that env
"$PYTHON_EXEC" -m PyInstaller --noconfirm --onefile --windowed --name "$APP_NAME" \
    --add-data "docs:docs" \
    --hidden-import "PySide6" \
    --hidden-import "pyqtgraph" \
    --hidden-import "serial" \
    --hidden-import "numpy" \
    main.py

echo "PyInstaller build complete."

# Create .deb directory structure
echo "Creating .deb directory structure..."
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/scalable/apps"

# Copy files
echo "Copying files..."
# Executable
cp "$DIST_DIR/$APP_NAME" "$DEB_DIR/usr/bin/"
chmod 755 "$DEB_DIR/usr/bin/$APP_NAME"

# Icon
cp "docs/public/Glance.svg" "$DEB_DIR/usr/share/icons/hicolor/scalable/apps/glance.svg"

# Desktop file
cp "packaging/glance.desktop" "$DEB_DIR/usr/share/applications/"

# Control and Postinst
cp "packaging/control" "$DEB_DIR/DEBIAN/"
cp "packaging/postinst" "$DEB_DIR/DEBIAN/"
chmod 755 "$DEB_DIR/DEBIAN/postinst"

# Build the .deb package
echo "Building .deb package..."
dpkg-deb --build "$DEB_DIR" "${APP_NAME}_${VERSION}_amd64.deb"

echo "Build successful! Package: ${APP_NAME}_${VERSION}_amd64.deb"
ls -lh "${APP_NAME}_${VERSION}_amd64.deb"
