#!/bin/bash

# Remove symlink
rm -f /usr/local/bin/gittree

# Remove package directory and files
rm -rf /usr/local/share/meth-packages/gittree

echo "Package GitTree uninstalled successfully"
