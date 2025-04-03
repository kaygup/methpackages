#!/bin/bash

# Remove symlink from PATH
rm -f /usr/local/bin/boykisserfetch

# Remove package directory
rm -rf /usr/local/share/meth-packages/boykisserfetch

echo "Package boykisserfetch uninstalled successfully"
