#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/nox

# Copy Python script to package directory
cp nox.py /usr/local/share/meth-packages/nox/

# Make it executable
chmod +x /usr/local/share/meth-packages/nox/nox.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/nox/nox.py /usr/local/bin/nox

echo "Package Simple Edit installed successfully"
