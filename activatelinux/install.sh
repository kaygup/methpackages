#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/linuxact

# Copy Python script to package directory
cp linuxact.py /usr/local/share/meth-packages/linuxact/

# Make it executable
chmod +x /usr/local/share/meth-packages/linuxact/linuxact.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/linuxact/linuxact.py /usr/local/bin/linuxact

echo "Linux Activation Watermark installed successfully"
echo "Run 'linuxact --on' to start the watermark"
echo "Run 'linuxact --autostart' to enable at system startup"
