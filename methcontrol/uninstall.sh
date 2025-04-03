#!/bin/bash

# NOX Volume Control - Uninstallation Script

echo "Uninstalling NOX Volume Control..."

# Check if running as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Remove symlink
if [ -L /usr/local/bin/nox ]; then
    rm /usr/local/bin/nox
    echo "Removed symlink from PATH"
fi

# Remove package directory
if [ -d /usr/local/share/meth-packages/methcontrol ]; then
    rm -rf /usr/local/share/meth-packages/nox
    echo "Removed application files"
fi



echo "Meth Volume Control has been uninstalled successfully."
