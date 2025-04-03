#!/bin/bash

# Remove symlink from PATH
rm -f /usr/local/bin/tux

# Remove package directory and its contents
rm -rf /usr/local/share/meth-packages/tux

echo "Package ASCII Penguin uninstalled successfully"
