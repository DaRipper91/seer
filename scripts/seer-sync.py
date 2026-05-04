import sqlite3
import json
import os
import sys

DB_PATH = os.path.expanduser("~/Projects/seer/seer.db")
SYNC_FILE = os.path.expanduser("~/Projects/seer/seer-metadata.json")

def export_metadata():
    print(f"\n\033[38;5;51m🪞 The Mirror is reflecting metadata to {SYNC_FILE}...\033[0m")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # We only export fields that we want to persist across machines
    cursor.execute("SELECT name, tags, description, run_count FROM scripts")
    rows = cursor.fetchall()
    
    metadata = {}
    for name, tags, desc, count in rows:
        metadata[name] = {
            "tags": tags,
            "description": desc,
            "run_count": count
        }
        
    with open(SYNC_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"\033[32m✅ Reflection complete. You can now commit this JSON file to Git.\033[0m\n")
    conn.close()

def import_metadata():
    if not os.path.exists(SYNC_FILE):
        print("\033[31m❌ No metadata reflection found to import.\033[0m")
        return
        
    print(f"\n\033[38;5;51m🪞 The Mirror is absorbing metadata from {SYNC_FILE}...\033[0m")
    with open(SYNC_FILE, 'r') as f:
        metadata = json.load(f)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updates = 0
    for name, data in metadata.items():
        # Update matching scripts by name
        cursor.execute("""
            UPDATE scripts 
            SET tags = COALESCE(?, tags), 
                run_count = GREATEST(run_count, ?)
            WHERE name = ?
        """, (data.get("tags"), data.get("run_count", 0), name))
        updates += cursor.rowcount
        
    conn.commit()
    conn.close()
    print(f"\033[32m✅ Absorption complete. {updates} script memories updated.\033[0m\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "import":
        import_metadata()
    else:
        export_metadata()
