#!/bin/bash
#
# Sombra Desktop - Uninstallation Script
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    exec sudo "$0" "$@"
fi

echo -e "${BLUE}Uninstalling Sombra Desktop...${NC}"

# Remove application
rm -rf /opt/sombra-desktop

# Remove launcher
rm -f /usr/local/bin/sombra-desktop

# Remove desktop file
rm -f /usr/share/applications/sombra.desktop

# Remove icons
for size in 16 32 48 64 128 256 512; do
    rm -f "/usr/share/icons/hicolor/${size}x${size}/apps/sombra.png"
done
rm -f /usr/share/icons/hicolor/scalable/apps/sombra.svg

# Update caches
gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database /usr/share/applications 2>/dev/null || true

echo -e "${GREEN}Sombra Desktop has been uninstalled.${NC}"
