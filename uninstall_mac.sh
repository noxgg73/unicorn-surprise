#!/bin/bash
# Unicorn Surprise - macOS Uninstaller

set -e

echo "============================================"
echo "  Unicorn Surprise - Desinstallation macOS"
echo "============================================"
echo ""

INSTALL_DIR="$HOME/.unicorn-surprise"
PLIST_FILE="$HOME/Library/LaunchAgents/com.unicorn-surprise.plist"

# Unload LaunchAgent
if [ -f "$PLIST_FILE" ]; then
    echo "Dechargement de l'agent: $PLIST_FILE"
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    rm -f "$PLIST_FILE"
fi

# Kill any remaining process
if pgrep -f "unicorn_surprise.py" > /dev/null; then
    echo "Arret du processus en cours..."
    pkill -f "unicorn_surprise.py" || true
    sleep 1
fi

# Remove install directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Suppression du dossier: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
fi

echo ""
echo "Desinstallation terminee."
echo "(psutil est conserve dans pip; supprimez-le avec: pip3 uninstall psutil)"
