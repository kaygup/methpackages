#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/waterfall

# Copy Python script to package directory
cp waterfall.py /usr/local/share/meth-packages/waterfall/

# Make it executable
chmod +x /usr/local/share/meth-packages/waterfall/waterfall.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/waterfall/waterfall.py /usr/local/bin/waterfall

echo "Terminal Waterfall animation installed successfully"
echo "Run 'waterfall' to start the animation"
echo "Press 'q' to quit the animation"
