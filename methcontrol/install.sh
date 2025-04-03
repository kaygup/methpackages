#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/methcontrol

# Copy Python script to package directory
cp methcontrol.py /usr/local/share/meth-packages/methcontrol/

# Make it executable
chmod +x /usr/local/share/meth-packages/methcontrol/methcontrol.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/methcontrol/methcontrol.py /usr/local/bin/methcontrol

echo "Package MethControl installed successfully"
