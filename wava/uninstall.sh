#!/bin/bash

# Remove symlink
if [ -L /usr/local/bin/macro ]; then
    rm /usr/local/bin/macro
fi

# Remove package directory
if [ -d /usr/local/share/meth-packages/macro ]; then
    rm -rf /usr/local/share/meth-packages/macro
fi

echo "Macro Text Editor uninstalled successfully"
