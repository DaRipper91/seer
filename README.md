# Seer: The Eye of Automation

Seer is an intelligent automation suite that helps you hunt, manage, and manifest your project scripts. It bridges the gap between raw terminal power and intuitive, visual control.

## 🔮 The Astral Dashboard (New!)

Seer now features a sleek, high-performance GUI called the **Astral Dashboard**. Built with `customtkinter`, it provides a modern, dark-mode experience that makes managing your scripts a breeze.

### Key Features:
*   **Threaded Scanning Engine**: Scan directories without locking your interface.
*   **Recursive Discovery**: Automatically hunts for scripts across nested folder structures.
*   **Visual Manifestation**: A "Crystal Ball" textbox that streams found scripts in real-time.
*   **System Integration**: One-click installation into your Linux application menu.

## 🚀 Quick Start

### Installation
Register Seer in your system menu:
```bash
./scripts/install_seer.sh
```
Once installed, search for **"Seer Astral Dashboard"** in your application launcher.

### Development Workflow
For developers, the dashboard is located at `scripts/seer-gui.py`. 

1.  **Launch**: Open the app from your launcher or via command line:
    ```bash
    ~/Projects/seer/venv/bin/python3 scripts/seer-gui.py
    ```
2.  **Scan**: Enter any directory path in the "Whisper your intent..." field and hit **Enter**.
3.  **Manifest**: The dashboard will recursively scan for `.py`, `.fish`, `.sh`, and executable scripts.

## 🛠 Project Components
- **Dashboard (`scripts/seer-gui.py`)**: The new Python-based GUI entry point.
- **Engine (`scripts/seer.fish`)**: The core CLI fuzzy-finder powered by `fzf` and `sqlite3`.
- **Scripts (`scripts/`)**: A collection of utility scripts for search, embedding, and system healing.

---
*Manifested with the Eye of Automation.*
