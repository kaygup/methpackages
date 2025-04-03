#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/tux

# Copy Python script to package directory
cp ascii_penguin.py /usr/local/share/meth-packages/tux/

# Make it executable
chmod +x /usr/local/share/meth-packages/tux/ascii_penguin.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/tux/ascii_penguin.py /usr/local/bin/tux

echo "Package ASCII Penguin installed successfully"
