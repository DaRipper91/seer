#!/bin/bash

# Configuration
PROJECT_DIR="$HOME/Projects/seer"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
SCRIPT_PATH="$PROJECT_DIR/scripts/seer-gui.py"
DESKTOP_ENTRY_DIR="$HOME/.local/share/applications"
DESKTOP_ENTRY_PATH="$DESKTOP_ENTRY_DIR/seer-dashboard.desktop"

# 1. Ensure Dependencies
echo "Ensuring customtkinter is installed..."
$VENV_PYTHON -m pip install customtkinter

# 2. Create Directory if it doesn't exist
mkdir -p "$DESKTOP_ENTRY_DIR"

# 3. Create Desktop Entry
echo "Creating desktop entry..."
cat <<EOF > "$DESKTOP_ENTRY_PATH"
[Desktop Entry]
Name=Seer Astral Dashboard
Comment=Astral Dashboard for Seer Automation
Exec=$VENV_PYTHON $SCRIPT_PATH
Icon=$PROJECT_DIR/assets/witch_cat.svg
Terminal=false
Type=Application
Categories=Development;Utility;
EOF

# 4. Make executable
chmod +x "$DESKTOP_ENTRY_PATH"

echo "Installation complete! 'Seer Astral Dashboard' should now appear in your application menu."
