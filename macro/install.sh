#!/bin/bash

# Set the name of the package and executable
PACKAGE_NAME="macro"
EXECUTABLE_NAME="macro"

# Create package directory
mkdir -p /usr/local/share/meth-packages/$PACKAGE_NAME

# Copy Python script to package directory
cp macro.py /usr/local/share/meth-packages/$PACKAGE_NAME/

# Make it executable
chmod +x /usr/local/share/meth-packages/$PACKAGE_NAME/macro.py

# Create symlink in PATH
ln -sf /usr/local/share/meth-packages/$PACKAGE_NAME/macro.py /usr/local/bin/$EXECUTABLE_NAME

echo "Package $PACKAGE_NAME installed successfully"
echo "You can now use the editor by running: $EXECUTABLE_NAME [filename]"
