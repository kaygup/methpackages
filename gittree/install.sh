#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/gittree

# Copy Python script to package directory
cp gittree.py /usr/local/share/meth-packages/gittree/

# Make it executable
chmod +x /usr/local/share/meth-packages/gittree/gittree.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/gittree/gittree.py /usr/local/bin/gittree

echo "Package GitTree installed successfully"
