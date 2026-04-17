#!/bin/bash
# Unicorn Surprise - macOS Installer

set -e

echo "============================================"
echo "   Unicorn Surprise - Installation macOS"
echo "============================================"
echo ""

INSTALL_DIR="$HOME/.unicorn-surprise"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/com.unicorn-surprise.plist"

# Create install directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$PLIST_DIR"

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 est requis."
    echo "Installez-le via: brew install python3 python-tk"
    exit 1
fi

# Install psutil
python3 -m pip install psutil 2>/dev/null || pip3 install psutil

# Copy the app
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/app/unicorn_surprise.py" ]; then
    cp "$SCRIPT_DIR/app/unicorn_surprise.py" "$INSTALL_DIR/unicorn_surprise.py"
else
    echo "Telechargement de l'application..."
    curl -sL "https://raw.githubusercontent.com/$(git config user.name 2>/dev/null || echo 'user')/unicorn-surprise/main/app/unicorn_surprise.py" -o "$INSTALL_DIR/unicorn_surprise.py" 2>/dev/null || {
        echo "Erreur: impossible de telecharger. Copiez unicorn_surprise.py dans $INSTALL_DIR/"
        exit 1
    }
fi

chmod +x "$INSTALL_DIR/unicorn_surprise.py"

# Create LaunchAgent plist
PYTHON_PATH=$(which python3)
cat > "$PLIST_FILE" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.unicorn-surprise</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${INSTALL_DIR}/unicorn_surprise.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>${INSTALL_DIR}/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${INSTALL_DIR}/stderr.log</string>
</dict>
</plist>
PLIST

# Load the agent
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo ""
echo "Installation terminee !"
echo "Unicorn Surprise se lancera a chaque connexion."
echo ""
echo "Pour desinstaller:"
echo "  launchctl unload $PLIST_FILE"
echo "  rm -rf $INSTALL_DIR"
echo "  rm -f $PLIST_FILE"
echo ""

read -p "Lancer maintenant ? (o/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    nohup python3 "$INSTALL_DIR/unicorn_surprise.py" &>/dev/null &
    echo "Lance ! PID: $!"
fi
