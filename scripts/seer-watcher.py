import time
import subprocess
import os
import sys

# Add the scripts directory to path to import indexer if needed, 
# but we can just call seer-refresh or seer-index.py directly.

REFRESH_COMMAND = ["python3", os.path.expanduser("~/Projects/seer/scripts/seer-index.py")]
INTERVAL = 60 # Check every minute

def watch():
    print("🐈 The Familiar is watching your scripts...")
    while True:
        try:
            # We just run the indexer. It already handles mtime checks efficiently.
            subprocess.run(REFRESH_COMMAND, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"⚠️ Familiar encountered an error: {e}", file=sys.stderr)
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    # Small delay on start
    time.sleep(5)
    watch()
