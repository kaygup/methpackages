#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Install dependencies
if [ -f /etc/arch-release ]; then
    echo "Detected Arch Linux"
    pacman -S --needed gcc make curl libcurl-devel
elif [ -f /etc/debian_version ]; then
    echo "Detected Debian/Ubuntu"
    apt-get update
    apt-get install -y gcc make libcurl4-openssl-dev
elif [ -f /etc/fedora-release ]; then
    echo "Detected Fedora"
    dnf install -y gcc make libcurl-devel
else
    echo "Unsupported distribution. Please install gcc, make, and libcurl manually."
fi

# Compile and install meth
make
make install

# Create required directories
mkdir -p /etc/meth
mkdir -p /usr/local/meth/packages
mkdir -p /tmp/meth

echo "Meth package manager installed successfully!"
echo "Usage:"
echo "  sudo meth cook PACKAGE    - Install a package"
echo "  sudo meth break PACKAGE   - Remove a package"
echo "  sudo meth update          - Update package index"
echo "  sudo meth sync            - Synchronize all packages"
