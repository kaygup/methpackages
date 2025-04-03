#!/bin/bash

# Flask - USB ISO Flashing Utility Install Script

# Check if script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root or with sudo privileges."
    exit 1
fi

# Define package directory
PACKAGE_DIR="/usr/local/share/flask-iso-utility"

# Install required packages
install_dependencies() {
    echo "Installing dependencies..."
    
    # Detect OS
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        apt-get update
        apt-get install -y python3 python3-pip python3-kivy
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS/Fedora
        dnf install -y python3 python3-pip
        pip3 install kivy
    elif [ -f /etc/arch-release ]; then
        # Arch Linux
        pacman -Sy python python-pip python-kivy
    elif [ -f /etc/SuSE-release ]; then
        # openSUSE
        zypper install -y python3 python3-pip
        pip3 install kivy
    elif [ -f /etc/alpine-release ]; then
        # Alpine Linux
        apk add python3 py3-pip
        pip3 install kivy
    else
        # Generic fallback
        echo "Could not determine your distribution. Installing dependencies with pip..."
        if command -v pip3 &>/dev/null; then
            pip3 install kivy
        else
            echo "Please install pip3 first, then run: pip3 install kivy"
            exit 1
        fi
    fi
    
    echo "Dependencies installed successfully."
}

# Create package directory
create_package() {
    echo "Creating package directory..."
    mkdir -p "$PACKAGE_DIR"
    
    # Copy the main script to the package directory
    if [ -f "flask.py" ]; then
        cp flask.py "$PACKAGE_DIR/"
        chmod +x "$PACKAGE_DIR/flask.py"
        
        # Create symlink in PATH
        ln -sf "$PACKAGE_DIR/flask.py" /usr/local/bin/flask-iso
        
        echo "Flask USB ISO Flashing Utility installed successfully."
        echo "You can run it with the command: flask-iso"
    else
        echo "Error: flask.py not found in the current directory."
        echo "Please make sure flask.py is in the same directory as this install script."
        exit 1
    fi
}

# Main installation process
echo "=== Flask USB ISO Flashing Utility Installer ==="
install_dependencies
create_package

echo "Installation complete!"
