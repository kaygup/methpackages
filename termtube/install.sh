#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/termtube

# Copy Python script to package directory
cp termtube.py /usr/local/share/meth-packages/termtube/

# Make it executable
chmod +x /usr/local/share/meth-packages/termtube/termtube.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/termtube/termtube.py /usr/local/bin/termtube

# Install required dependencies
echo "Installing dependencies..."
pip install pytube pillow numpy opencv-python

echo "TermTube installed successfully!"
echo "Usage: termtube [youtube-url] [-r {360p,480p,720p,1080p}]"
