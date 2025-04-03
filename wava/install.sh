#!/bin/bash
echo "Installing Python dependencies..."
sudo pacman -S install python-numpy python-pyaudio

# Create package directory
echo "Creating package directory..."
sudo mkdir -p /usr/local/share/meth-packages/wava

# Copy Python script to package directory
echo "Copying files..."
sudo cp wava.py /usr/local/share/meth-packages/wava/

# Make it executable
echo "Setting permissions..."
sudo chmod +x /usr/local/share/meth-packages/wava/wava.py

# Create symlink in PATH
echo "Creating symlink..."
sudo ln -sf /usr/local/share/meth-packages/wava/wava.py /usr/local/bin/wava

echo "Package NOX Audio Visualizer installed successfully"
echo "Run 'nox' to start the visualizer or 'nox --help' for options"
