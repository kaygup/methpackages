#!/bin/bash

# Install script for hello-world package
# This should be placed in the hello-world directory in your repository

# Create the target directory if it doesn't exist
mkdir -p /usr/local/bin

# Copy the Python script to the bin directory
cp hello-world.py /usr/local/bin/hello-world

# Make it executable
chmod +x /usr/local/bin/hello-world

# Create a simple wrapper script for easier execution
cat > /usr/local/bin/hello-world << EOF
#!/usr/bin/env python3
# Hello World package installed via meth package manager

print("Hello, World!")
EOF

echo "hello-world package installed successfully!"
