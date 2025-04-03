#!/bin/bash

# Exit on error
set -e

echo "Uninstalling Methx File Explorer..."

# Remove symlink
if [ -L /usr/local/bin/methx ]; then
    rm /usr/local/bin/methx
    echo "Removed symlink from /usr/local/bin/methx"
fi

# Remove package directory
if [ -d /usr/local/share/meth-packages/methx ]; then
    rm -rf /usr/local/share/meth-packages/methx
    echo "Removed package files from /usr/local/share/meth-packages/methx"
fi

echo "Methx File Explorer uninstalled successfully!"
