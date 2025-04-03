#!/bin/bash

# Stop any running instances
pkill -f "linuxact --on"

# Remove autostart entry
if [ -f ~/.config/autostart/linuxact.desktop ]; then
    rm ~/.config/autostart/linuxact.desktop
    echo "Removed autostart entry"
fi

# Remove symlink
if [ -L /usr/local/bin/linuxact ]; then
    rm /usr/local/bin/linuxact
fi

# Remove package directory
if [ -d /usr/local/share/meth-packages/linuxact ]; then
    rm -rf /usr/local/share/meth-packages/linuxact
fi

echo "Linux Activation Watermark uninstalled successfully"
