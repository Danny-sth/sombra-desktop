#!/bin/bash
#
# Sombra Desktop - Installation Script
# Installs the application system-wide with desktop integration
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/sombra-desktop"
BIN_DIR="/usr/local/bin"
ICON_DIR="/usr/share/icons/hicolor"
DESKTOP_DIR="/usr/share/applications"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║       Sombra Desktop Installer            ║"
echo "║       Voice-enabled AI Assistant          ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}This script requires sudo privileges.${NC}"
    exec sudo "$0" "$@"
fi

# Install system dependencies
echo -e "${BLUE}[1/6]${NC} Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3-venv python3-dev portaudio19-dev libxcb-cursor0 python3-xlib > /dev/null

# Create installation directory
echo -e "${BLUE}[2/6]${NC} Creating installation directory..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy application files
echo -e "${BLUE}[3/6]${NC} Copying application files..."
cp -r "$SCRIPT_DIR/src" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/pyproject.toml" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"

# Create virtual environment and install dependencies
echo -e "${BLUE}[4/6]${NC} Setting up Python environment..."
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --upgrade pip -q
"$INSTALL_DIR/.venv/bin/pip" install -e "$INSTALL_DIR" -q

# Create launcher script
echo -e "${BLUE}[5/6]${NC} Creating launcher..."
cat > "$BIN_DIR/sombra-desktop" << 'EOF'
#!/bin/bash
cd /opt/sombra-desktop
source .venv/bin/activate
exec python -m sombra "$@"
EOF
chmod +x "$BIN_DIR/sombra-desktop"

# Install icons
echo -e "${BLUE}[6/6]${NC} Installing desktop integration..."
for size in 16 32 48 64 128 256 512; do
    mkdir -p "$ICON_DIR/${size}x${size}/apps"
    if [ -f "$SCRIPT_DIR/resources/icons/sombra-512.png" ]; then
        convert "$SCRIPT_DIR/resources/icons/sombra-512.png" -resize ${size}x${size} \
            "$ICON_DIR/${size}x${size}/apps/sombra.png" 2>/dev/null || \
        cp "$SCRIPT_DIR/resources/icons/sombra-512.png" "$ICON_DIR/${size}x${size}/apps/sombra.png"
    fi
done

# Install SVG icon
mkdir -p "$ICON_DIR/scalable/apps"
cp "$SCRIPT_DIR/resources/icons/sombra.svg" "$ICON_DIR/scalable/apps/sombra.svg"

# Update icon cache
gtk-update-icon-cache "$ICON_DIR" 2>/dev/null || true

# Install desktop file
cp "$SCRIPT_DIR/sombra.desktop" "$DESKTOP_DIR/"
chmod 644 "$DESKTOP_DIR/sombra.desktop"

# Update desktop database
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Installation completed successfully!   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "You can now launch Sombra Desktop:"
echo -e "  ${BLUE}•${NC} From terminal: ${YELLOW}sombra-desktop${NC}"
echo -e "  ${BLUE}•${NC} From applications menu: search for ${YELLOW}Sombra${NC}"
echo ""
echo -e "Configuration file: ${YELLOW}/opt/sombra-desktop/.env${NC}"
echo ""
