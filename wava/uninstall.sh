#!/bin/bash

echo "Uninstalling NOX Audio Visualizer..."

# Remove symlink
if [ -L /usr/local/bin/wava ]; then
    sudo rm /usr/local/bin/wava
    echo "Removed symlink"
fi

# Remove package directory
if [ -d /usr/local/share/meth-packages/wava ]; then
    sudo rm -rf /usr/local/share/meth-packages/wava
    echo "Removed package files"
fi

echo "NOX Audio Visualizer uninstalled successfully"
