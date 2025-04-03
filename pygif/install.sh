#!/bin/bash

# Check for required dependencies
echo "Checking dependencies..."
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting."; exit 1; }

# Check for pip
command -v pip3 >/dev/null 2>&1 || { echo "pip3 is required but not installed. Aborting."; exit 1; }

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install pillow || { echo "Failed to install dependencies. Aborting."; exit 1; }

# Create package directory
echo "Creating package directory..."
sudo mkdir -p /usr/local/share/meth-packages/pygif || { echo "Failed to create package directory. Aborting."; exit 1; }

# Copy Python script to package directory
echo "Installing pygif..."
sudo cp pygif.py /usr/local/share/meth-packages/pygif/ || { echo "Failed to copy script. Aborting."; exit 1; }

# Make it executable
sudo chmod +x /usr/local/share/meth-packages/pygif/pygif.py || { echo "Failed to make script executable. Aborting."; exit 1; }

# Create symlink in PATH
sudo ln -sf /usr/local/share/meth-packages/pygif/pygif.py /usr/local/bin/pygif || { echo "Failed to create symlink. Aborting."; exit 1; }

echo "Package GIF Terminal Player (gittree) installed successfully!"
echo "Usage: pygif <gif_url>"
