#!/bin/bash

# Create package directory
mkdir -p /usr/local/share/meth-packages/methshot

# Copy Python script to package directory
cp methshot.py /usr/local/share/meth-packages/methshot/

# Make it executable
chmod +x /usr/local/share/meth-packages/methshot/methshot.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/methshot/methshot.py /usr/local/bin/methshot
echo "Methshot screenshot utility installed successfully!"
echo "Type 'methshot' to run the application."
