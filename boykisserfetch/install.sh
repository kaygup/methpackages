#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/gittree-packages/boykisserfetch

# Copy Python script to package directory
cp boykisserfetch.py /usr/local/share/gittree-packages/boykisserfetch/

# Make it executable
chmod +x /usr/local/share/gittree-packages/boykisserfetch/boykisserfetch.py

# Create symlink in PATH
ln -sf /usr/local/share/gittree-packages/boykisserfetch/boykisserfetch.py /usr/local/bin/boykisserfetch

echo "Package boykisserfetch installed successfully"
