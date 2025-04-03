#!/bin/bash

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Remove symlink
if [ -L /usr/local/bin/methshot ]; then
    rm /usr/local/bin/methshot
    echo "Removed symlink from PATH"
fi

# Remove package directory
if [ -d /usr/local/share/meth-packages/methshot ]; then
    rm -rf /usr/local/share/meth-packages/methshot
    echo "Removed methshot package directory"
fi

# Check if meth-packages directory is empty and remove if it is


echo "Methshot screenshot utility uninstalled successfully!"
