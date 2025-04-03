#!/bin/bash

# Remove symlink
echo "Removing symlink..."
sudo rm -f /usr/local/bin/pygif

# Remove package files
echo "Removing package files..."
sudo rm -rf /usr/local/share/meth-packages/pygif

echo "Package GIF Terminal Player (meth) uninstalled successfully!"
