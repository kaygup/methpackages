#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to detect the package manager
detect_package_manager() {
  if command -v apt &> /dev/null; then
    PKG_MANAGER="apt"
    INSTALL_CMD="apt install -y"
    UPDATE_CMD="apt update"
  elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    INSTALL_CMD="dnf install -y"
    UPDATE_CMD="dnf check-update"
  elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
    INSTALL_CMD="yum install -y"
    UPDATE_CMD="yum check-update"
  elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
    INSTALL_CMD="pacman -S --noconfirm"
    UPDATE_CMD="pacman -Sy"
  elif command -v zypper &> /dev/null; then
    PKG_MANAGER="zypper"
    INSTALL_CMD="zypper install -y"
    UPDATE_CMD="zypper refresh"
  else
    echo -e "${RED}Error: No supported package manager found.${NC}"
    echo "This script supports apt, dnf, yum, pacman, and zypper."
    exit 1
  fi
}

# Function to check if running as root
check_root() {
  if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    echo "Please run with sudo or as root"
    exit 1
  fi
}

# Function to install dependencies based on package manager
install_dependencies() {
  echo -e "${YELLOW}Updating package repositories...${NC}"
  $UPDATE_CMD

  echo -e "${YELLOW}Installing dependencies using $PKG_MANAGER...${NC}"
  
  case $PKG_MANAGER in
    apt)
      $INSTALL_CMD python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0 gir1.2-pango-1.0 python3-pip
      ;;
    dnf|yum)
      $INSTALL_CMD python3 python3-gobject gtk3 python3-cairo-devel gobject-introspection-devel cairo-gobject-devel python3-pip
      ;;
    pacman)
      $INSTALL_CMD python python-gobject gtk3 python-cairo gobject-introspection cairo python-pip
      ;;
    zypper)
      $INSTALL_CMD python3 python3-gobject gtk3 python3-cairo python3-gobject-cairo python3-pip
      ;;
  esac
  
  # Install Python dependencies
  pip3 install setuptools wheel
}

# Function to create NoxDE directory structure
setup_noxde() {
  echo -e "${YELLOW}Creating NoxDE directory structure...${NC}"
  
  # Create package directory
  mkdir -p /usr/local/share/noxde
  
  # Create directories for application
  mkdir -p /usr/local/share/noxde/bin
  mkdir -p /usr/local/share/noxde/applications
  mkdir -p /usr/local/share/xsessions
  
  # Copy main script
  cp noxde.py /usr/local/share/noxde/bin/
  chmod +x /usr/local/share/noxde/bin/noxde.py
  
  # Create symlink in PATH
  ln -sf /usr/local/share/noxde/bin/noxde.py /usr/local/bin/noxde
  
  # Create desktop entry for NoxDE
  cat > /usr/local/share/applications/noxde.desktop << EOF
[Desktop Entry]
Name=NoxDE
Comment=Minimal Desktop Environment
Exec=/usr/local/bin/noxde
Type=Application
Keywords=DE;Desktop;Environment;
EOF

  # Create XSession entry
  cat > /usr/local/share/xsessions/noxde.desktop << EOF
[Desktop Entry]
Name=NoxDE
Comment=Minimal Desktop Environment
Exec=/usr/local/bin/noxde
Type=Application
Keywords=DE;Desktop;Environment;
EOF

  # Set permissions
  chmod 644 /usr/local/share/applications/noxde.desktop
  chmod 644 /usr/local/share/xsessions/noxde.desktop
}

# Function to install Flask2 and USB Creator
install_apps() {
  echo -e "${YELLOW}Installing Flask2 Editor and USB Creator...${NC}"
  
  # Create desktop entries
  cat > /usr/local/share/noxde/applications/flask2.desktop << EOF
[Desktop Entry]
Name=Flask2 Editor
Comment=Text Editor
Exec=python3 -c "import sys; sys.path.append('/usr/local/share/noxde/bin'); from noxde import Flask2Editor; editor = Flask2Editor(); editor.run(); import gi; gi.repository.Gtk.main()"
Icon=accessories-text-editor
Type=Application
Categories=Utility;TextEditor;
EOF

  cat > /usr/local/share/noxde/applications/usbcreator.desktop << EOF
[Desktop Entry]
Name=USB Creator
Comment=Create bootable USB drives
Exec=python3 -c "import sys; sys.path.append('/usr/local/share/noxde/bin'); from noxde import USBCreator; creator = USBCreator(); creator.run(); import gi; gi.repository.Gtk.main()"
Icon=drive-removable-media
Type=Application
Categories=Utility;
EOF

  # Copy to system applications directory
  cp /usr/local/share/noxde/applications/flask2.desktop /usr/local/share/applications/
  cp /usr/local/share/noxde/applications/usbcreator.desktop /usr/local/share/applications/
  
  # Set permissions
  chmod 644 /usr/local/share/applications/flask2.desktop
  chmod 644 /usr/local/share/applications/usbcreator.desktop
}

# Main installation function
install_noxde() {
  check_root
  detect_package_manager
  
  echo -e "${YELLOW}Beginning installation of NoxDE...${NC}"
  
  install_dependencies
  setup_noxde
  install_apps
  
  echo -e "${GREEN}Installation completed successfully!${NC}"
  echo "NoxDE has been installed to /usr/local/share/noxde"
  echo "You can now select NoxDE from your login screen"
  echo "Run NoxDE directly with the command 'noxde'"
}

# Create uninstallation script
create_uninstall_script() {
  cat > /usr/local/share/noxde/uninstall.sh << 'EOF'
#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Error: This script must be run as root${NC}"
  echo "Please run with sudo or as root"
  exit 1
fi

echo -e "${YELLOW}Uninstalling NoxDE...${NC}"

# Remove desktop entries
rm -f /usr/local/share/applications/noxde.desktop
rm -f /usr/local/share/applications/flask2.desktop
rm -f /usr/local/share/applications/usbcreator.desktop

# Remove XSession entry
rm -f /usr/local/share/xsessions/noxde.desktop

# Remove symlink
rm -f /usr/local/bin/noxde

# Remove NoxDE directory
rm -rf /usr/local/share/noxde

echo -e "${GREEN}NoxDE has been uninstalled successfully!${NC}"
EOF

  chmod +x /usr/local/share/noxde/uninstall.sh
  ln -sf /usr/local/share/noxde/uninstall.sh /usr/local/bin/uninstall-noxde
  
  echo "To uninstall NoxDE, run: sudo uninstall-noxde"
}

# Run the installation
install_noxde
create_uninstall_script

exit 0
