#!/bin/bash

# Set the name of the package and executable
PACKAGE_NAME="macro"
EXECUTABLE_NAME="macro"

# Remove symlink from PATH
rm -f /usr/local/bin/$EXECUTABLE_NAME

# Remove package directory
rm -rf /usr/local/share/meth-packages/$PACKAGE_NAME

echo "Package $PACKAGE_NAME uninstalled successfully"
