#!/bin/bash
# Unicorn Surprise - Linux Installer

set -e

echo "============================================"
echo "   Unicorn Surprise - Installation Linux"
echo "============================================"
echo ""

INSTALL_DIR="$HOME/.unicorn-surprise"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "Python3 est requis. Installation..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3 python3-pip python3-tk
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip python3-tkinter
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm python python-pip tk
    else
        echo "Impossible d'installer Python3 automatiquement."
        echo "Installez Python3 manuellement puis relancez ce script."
        exit 1
    fi
fi

# Install psutil
python3 -m pip install --user psutil 2>/dev/null || pip3 install --user psutil

# Download the app
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

# Create autostart entry
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_DIR/unicorn-surprise.desktop" << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=Unicorn Surprise
Comment=Dancing unicorn and oiia cat on app launch
Exec=python3 /home/PLACEHOLDER/.unicorn-surprise/unicorn_surprise.py
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
StartupNotify=false
DESKTOP

# Fix the path in the desktop file
sed -i "s|/home/PLACEHOLDER|$HOME|g" "$AUTOSTART_DIR/unicorn-surprise.desktop"

echo ""
echo "Installation terminee !"
echo "Unicorn Surprise se lancera au prochain demarrage."
echo ""
echo "Pour lancer maintenant:"
echo "  python3 $INSTALL_DIR/unicorn_surprise.py &"
echo ""
echo "Pour desinstaller:"
echo "  rm -rf $INSTALL_DIR"
echo "  rm -f $AUTOSTART_DIR/unicorn-surprise.desktop"
echo ""

# Ask to launch now
read -p "Lancer maintenant ? (o/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Oo]$ ]]; then
    nohup python3 "$INSTALL_DIR/unicorn_surprise.py" &>/dev/null &
    echo "Lance ! PID: $!"
fi
