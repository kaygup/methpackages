#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/simpleedit

# Copy Python script to package directory
cp simpleedit.py /usr/local/share/meth-packages/simpleedit/

# Make it executable
chmod +x /usr/local/share/meth-packages/simpleedit/simpleedit.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/simpleedit/simpledit.py /usr/local/bin/simpleedit

echo "Package Simple Edit installed successfully"
