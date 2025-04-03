#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/editor

# Copy Python script to package directory
cp simpleedit.py /usr/local/share/meth-packages/editor/

# Make it executable
chmod +x /usr/local/share/meth-packages/editor/simpleedit.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/editor/simpledit.py /usr/local/bin/editor

echo "Package Simple Edit installed successfully"
