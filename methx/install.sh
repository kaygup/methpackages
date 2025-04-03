#!/bin/bash

# Exit on error
set -e

echo "Installing Methx File Explorer..."

# Create package directory
mkdir -p /usr/local/share/meth-packages/methx

# Copy Python script to package directory
cp methx.py /usr/local/share/meth-packages/methx/

# Make it executable
chmod +x /usr/local/share/meth-packages/methx/methx.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/methx/methx.py /usr/local/bin/methx

# Check for wxPython
echo "Installing required dependencies..."
sudo pacman -S python-wxpython
echo "Methx File Explorer installed successfully!"
echo "You can run it by typing 'methx' in your terminal."
