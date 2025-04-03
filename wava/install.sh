#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/macro

# Copy Python script to package directory
cp macro.py /usr/local/share/meth-packages/macro/

# Make it executable
chmod +x /usr/local/share/meth-packages/macro/macro.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/macro/macro.py /usr/local/bin/macro

echo "Macro Text Editor installed successfully"
