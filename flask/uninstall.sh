#!/bin/bash

# Flask - USB ISO Flashing Utility Uninstall Script

# Check if script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root or with sudo privileges."
    exit 1
fi

# Define package directory
PACKAGE_DIR="/usr/local/share/meth-packages/flask"

# Remove the package
echo "=== Flask USB ISO Flashing Utility Uninstaller ==="
echo "Removing Flask USB ISO Flashing Utility..."

# Remove symlink
if [ -L "/usr/local/bin/flask-iso" ]; then
    rm -f /usr/local/bin/flask-iso
    echo "Removed symlink from PATH."
else
    echo "Symlink not found in PATH."
fi

# Remove package directory
if [ -d "$PACKAGE_DIR" ]; then
    rm -rf "$PACKAGE_DIR"
    echo "Removed package directory."
else
    echo "Package directory not found."
fi

echo "Flask USB ISO Flashing Utility has been uninstalled successfully."
