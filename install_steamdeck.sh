#!/bin/bash
# KH1 Save Editor - Steam Deck Installer
# Uses Python's built-in tkinter desktop UI.

INSTALL_DIR="$HOME/.local/share/kh1-save-editor"
DESKTOP_FILE="$HOME/.local/share/applications/kh1-save-editor.desktop"
ICON_DIR="$HOME/.local/share/icons"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================"
echo "  KH1 Save Editor - Steam Deck Setup  "
echo "======================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found."
    exit 1
fi

if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "ERROR: Python tkinter is not available on this system."
    echo "This build cannot launch until tkinter is installed."
    exit 1
fi

echo "Creating install directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$ICON_DIR"
mkdir -p "$(dirname "$DESKTOP_FILE")"

echo "Copying files..."
cp "$SCRIPT_DIR"/kh1_*.py "$INSTALL_DIR/"
for banner in banner.png banner.gif; do
    if [ -f "$SCRIPT_DIR/$banner" ]; then
        cp "$SCRIPT_DIR/$banner" "$INSTALL_DIR/"
    fi
done

# Launcher
LAUNCHER="$INSTALL_DIR/launch.sh"
cat > "$LAUNCHER" << 'LAUNCHEOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 kh1_save_editor.py
LAUNCHEOF
chmod +x "$LAUNCHER"

# SVG icon
cat > "$ICON_DIR/kh1-save-editor.svg" << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="12" fill="#1a1a2e"/>
  <polygon points="32,6 58,32 32,58 6,32" fill="#e94560" opacity="0.9"/>
  <polygon points="32,14 50,32 32,50 14,32" fill="#f0a500"/>
  <polygon points="32,22 42,32 32,42 22,32" fill="#1a1a2e"/>
</svg>
SVGEOF

# Desktop entry
cat > "$DESKTOP_FILE" << DESKTOPEOF
[Desktop Entry]
Name=KH1 Save Editor
Comment=Kingdom Hearts HD 1.5 ReMIX Save Editor
Exec=bash $INSTALL_DIR/launch.sh
Icon=$ICON_DIR/kh1-save-editor.svg
Terminal=false
Type=Application
Categories=Game;Utility;
Keywords=kingdom hearts;save editor;kh1;
StartupWMClass=kh1_save_editor
DESKTOPEOF

chmod +x "$DESKTOP_FILE"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo ""
echo "======================================"
echo "  Done!"
echo ""
echo "  The editor opens as a desktop app."
echo ""
echo "  Launch from App Menu -> Utilities"
echo "  Or run: bash $INSTALL_DIR/launch.sh"
echo "======================================"
