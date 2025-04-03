#!/bin/bash

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
