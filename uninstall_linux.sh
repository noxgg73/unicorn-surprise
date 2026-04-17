#!/bin/bash
# Unicorn Surprise - Linux Uninstaller

set -e

echo "============================================"
echo "  Unicorn Surprise - Desinstallation Linux"
echo "============================================"
echo ""

INSTALL_DIR="$HOME/.unicorn-surprise"
AUTOSTART_FILE="$HOME/.config/autostart/unicorn-surprise.desktop"

# Stop running process
if pgrep -f "unicorn_surprise.py" > /dev/null; then
    echo "Arret du processus en cours..."
    pkill -f "unicorn_surprise.py" || true
    sleep 1
fi

# Remove autostart entry
if [ -f "$AUTOSTART_FILE" ]; then
    echo "Suppression de l'entree autostart: $AUTOSTART_FILE"
    rm -f "$AUTOSTART_FILE"
fi

# Remove install directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Suppression du dossier: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
fi

echo ""
echo "Desinstallation terminee."
echo "(psutil est conserve dans pip; supprimez-le avec: pip3 uninstall psutil)"
