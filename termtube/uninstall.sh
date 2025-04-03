#!/bin/bash

# Remove symlink
rm -f /usr/local/bin/termtube

# Remove package directory
rm -rf /usr/local/share/meth-packages/termtube

# Cleanup temporary files
rm -rf ~/.termtube

echo "TermTube uninstalled successfully"
