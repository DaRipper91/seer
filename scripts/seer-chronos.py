import os
import sys
import subprocess
import shutil
from datetime import datetime

CHRONOS_DIR = os.path.expanduser("~/.seer-chronos")
VAULT_DIR = os.path.join(CHRONOS_DIR, "vault")

def init_chronos():
    """Initializes the hidden git repository for tracking script history."""
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR, exist_ok=True)
        subprocess.run(["git", "init"], cwd=VAULT_DIR, capture_output=True)
        # Create an initial commit
        readme_path = os.path.join(VAULT_DIR, "README.md")
        with open(readme_path, "w") as f:
            f.write("# ⏳ The Scroll of Chronos\n\nThis vault contains the timeline of all executed scripts.")
        subprocess.run(["git", "add", "README.md"], cwd=VAULT_DIR, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial Epoch"], cwd=VAULT_DIR, capture_output=True)

def backup_script(script_path):
    """Copies a script to the vault and commits the changes."""
    init_chronos()
    
    if not os.path.exists(script_path):
        return
        
    script_name = os.path.basename(script_path)
    vault_path = os.path.join(VAULT_DIR, script_name)
    
    try:
        shutil.copy2(script_path, vault_path)
        
        # Check if there are changes to commit
        status = subprocess.run(["git", "status", "--porcelain", script_name], cwd=VAULT_DIR, capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "add", script_name], cwd=VAULT_DIR, capture_output=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"⏳ Chronos: Auto-backup of {script_name} at {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=VAULT_DIR, capture_output=True)
            
            # Print a subtle message if run interactively, otherwise it's silent
            if sys.stdout.isatty():
                print(f"\033[90m[Chronos recorded a new epoch for {script_name}]\033[0m")
    except Exception as e:
        print(f"\033[31m⚠️ Chronos failed to read the timeline: {e}\033[0m", file=sys.stderr)

def rewind_script(script_name):
    """Allows the user to view history and rewind a script (CLI usage)."""
    # This is a stub for the user to run manually if needed
    print(f"To view the timeline of {script_name}, run:")
    print(f"  cd {VAULT_DIR} && git log -p {script_name}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: seer-chronos.py [backup|rewind] <script_path_or_name>")
        sys.exit(1)
        
    action = sys.argv[1]
    target = sys.argv[2]
    
    if action == "backup":
        backup_script(target)
    elif action == "rewind":
        rewind_script(target)
