#!/bin/bash
# Build script for Deluge Speed Toggle plugin

set -e

echo "Building Deluge Speed Toggle plugin..."

# Clean previous builds
if [ -d "dist" ]; then
    echo "Cleaning previous builds..."
    rm -rf dist build *.egg-info
fi

# Build the plugin egg
echo "Creating plugin egg..."
python setup.py bdist_egg

# Display the result
echo ""
echo "Build complete!"
echo "Plugin egg created at:"
ls -lh dist/*.egg

echo ""
echo "To install:"
echo "1. Open Deluge"
echo "2. Go to Preferences > Plugins"
echo "3. Click 'Install Plugin'"
echo "4. Select the .egg file from the dist/ directory"
echo "5. Enable the 'SpeedToggle' plugin"
