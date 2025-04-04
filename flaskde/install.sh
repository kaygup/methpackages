#!/bin/bash

# install.sh - Installation script for Little DE

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Define package directory
PACKAGE_DIR="/usr/local/share/meth-packages/little-de"
BIN_DIR="/usr/local/bin"

# Create package directory
mkdir -p "$PACKAGE_DIR"

echo -e "${YELLOW}Installing Little DE...${NC}"

# Detect OS and package manager
if [ -f /etc/debian_release ] || [ -f /etc/debian_version ] || \
   command -v apt &>/dev/null || command -v apt-get &>/dev/null; then
    # Debian, Ubuntu, or similar
    echo -e "${YELLOW}Detected Debian/Ubuntu-based system${NC}"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-gi gir1.2-gtk-3.0 udisks2
    pip3 install --user pygobject
    
elif [ -f /etc/arch-release ] || command -v pacman &>/dev/null; then
    # Arch Linux or similar
    echo -e "${YELLOW}Detected Arch-based system${NC}"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    sudo pacman -Sy --noconfirm python python-pip python-gobject gtk3 udisks2
    
elif [ -f /etc/fedora-release ] || [ -f /etc/redhat-release ] || \
     command -v dnf &>/dev/null || command -v yum &>/dev/null; then
    # Fedora, RHEL, CentOS or similar
    echo -e "${YELLOW}Detected Fedora/RHEL-based system${NC}"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    if command -v dnf &>/dev/null; then
        sudo dnf install -y python3 python3-pip python3-gobject gtk3 udisks2
    else
        sudo yum install -y python3 python3-pip python3-gobject gtk3 udisks2
    fi
    
elif [ -f /etc/SuSE-release ] || command -v zypper &>/dev/null; then
    # openSUSE or similar
    echo -e "${YELLOW}Detected openSUSE-based system${NC}"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    
    sudo zypper install -y python3 python3-pip python3-gobject gtk3 udisks2
    
else
    echo -e "${RED}Unsupported Linux distribution.${NC}"
    echo -e "${YELLOW}Please install the following dependencies manually:${NC}"
    echo "- Python 3"
    echo "- PyGObject"
    echo "- GTK 3"
    echo "- udisks2"
    read -p "Continue with installation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Installation cancelled.${NC}"
        exit 1
    fi
fi

# Copy the Python script
cp little_de.py "$PACKAGE_DIR/"
chmod +x "$PACKAGE_DIR/little_de.py"

# Create a launcher script
cat > "$BIN_DIR/little-de" << EOF
#!/bin/bash
$PACKAGE_DIR/little_de.py "\$@"
EOF

chmod +x "$BIN_DIR/little-de"

# Create desktop entry
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/little-de.desktop << EOF
[Desktop Entry]
Name= Flask DE
Comment=Minimal Desktop Environment
Exec=$BIN_DIR/little-de
Type=Application
Categories=Utility;System;
Terminal=false
Icon=system-software-install
EOF

echo -e "${GREEN}Little DE installed successfully!${NC}"
echo -e "${YELLOW}You can now run it by typing 'little-de' in the terminal or through your application menu.${NC}"
