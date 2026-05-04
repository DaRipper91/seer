import os
import sqlite3
import stat
import time

DB_PATH = os.path.expanduser("~/Projects/seer/seer.db")
SEARCH_DIR = os.path.expanduser("~")

EXCLUDED_DIRS = {
    "node_modules", ".git", ".cache", ".npm", ".bun", ".local", 
    ".android", ".cargo", ".rustup", "venv", "__pycache__", 
    "Android", "SoftMaker", "FONTS", "Jules_Projects"
}

EXTENSIONS = {
    ".sh", ".bash", ".zsh", ".fish", ".py", ".js", ".ts", 
    ".jsx", ".tsx", ".rb", ".php", ".pl", ".lua", ".ps1", 
    ".bat", ".cmd"
}

def get_metadata(path):
    """Extracts shebang, description, and tags from the first few lines of a file."""
    shebang = None
    description = ""
    tags = ""
    linked_configs = []
    
    dir_name = os.path.dirname(path)
    base_name = os.path.splitext(os.path.basename(path))[0]

    # Look for common config files in the same directory
    config_exts = [".yaml", ".yml", ".json", ".toml", ".env", ".ini", ".conf"]
    for ext in config_exts:
        # Check for named configs like scriptname.yaml or config.yaml
        potential_configs = [f"{base_name}{ext}", f"config{ext}", f".env"]
        for pc in potential_configs:
            cfg_path = os.path.join(dir_name, pc)
            if os.path.exists(cfg_path):
                linked_configs.append(cfg_path)
    
    try:
        with open(path, 'r', errors='ignore') as f:
            lines = [f.readline().strip() for _ in range(15)]
            if lines and lines[0].startswith("#!"):
                shebang = lines[0]
            
            for line in lines:
                clean = line.lstrip("#/ *")
                if not clean: continue
                
                # Extract Tags: look for "Tags: tag1, tag2"
                if "tags:" in line.lower():
                    tags = line.lower().split("tags:")[1].strip()
                
                if not description and not line.startswith("#!"):
                    description = clean
    except Exception:
        pass
        
    return shebang, description, tags, ",".join(list(set(linked_configs)))

ACTIVE_DIRS = [
    os.path.expanduser("~/Projects"),
    os.path.expanduser("~/scripts"),
    os.path.expanduser("~/bin"),
    os.path.expanduser("~/.local/bin"),
    os.path.expanduser("~/.gemini/extensions"),
    os.path.expanduser("~/Jules_Projects") # Keeping this as requested
]

def index_scripts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"🚀 Seer is scanning active directories...")
    start_time = time.time()
    
    found_paths = set()
    new_count = 0
    updated_count = 0

    for search_dir in ACTIVE_DIRS:
        if not os.path.exists(search_dir):
            continue
            
        for root, dirs, files in os.walk(search_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

            for file in files:
                path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                is_script = ext in EXTENSIONS
                if not is_script:
                    # Check for extensionless executables with a shebang
                    try:
                        st = os.stat(path)
                        if st.st_mode & stat.S_IXUSR:
                            with open(path, 'r', errors='ignore') as f:
                                if f.read(2) == "#!":
                                    is_script = True
                    except Exception:
                        continue

                if is_script:
                    found_paths.add(path)
                    try:
                        mtime = os.path.getmtime(path)
                    except OSError:
                        continue
                    
                    # Check if we need to update
                    cursor.execute("SELECT mtime FROM scripts WHERE path = ?", (path,))
                    row = cursor.fetchone()
                    
                    if row is None:
                        # New script
                        shebang, description, tags, linked_configs = get_metadata(path)
                        cursor.execute("""
                            INSERT INTO scripts (path, name, extension, shebang, description, mtime, tags, linked_configs)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (path, file, ext, shebang, description, mtime, tags, linked_configs))
                        new_count += 1
                    elif row[0] < mtime:
                        # Updated script
                        shebang, description, tags, linked_configs = get_metadata(path)
                        cursor.execute("""
                            UPDATE scripts 
                            SET name = ?, extension = ?, shebang = ?, description = ?, mtime = ?, tags = ?, linked_configs = ?
                            WHERE path = ?
                        """, (file, ext, shebang, description, mtime, tags, linked_configs, path))
                        updated_count += 1

    # Remove deleted scripts
    cursor.execute("SELECT id, path FROM scripts")
    all_scripts = cursor.fetchall()
    deleted_count = 0
    for row_id, path in all_scripts:
        if path not in found_paths:
            cursor.execute("DELETE FROM scripts WHERE id = ?", (row_id,))
            deleted_count += 1

    conn.commit()
    conn.close()
    
    duration = time.time() - start_time
    print(f"✅ Scan complete in {duration:.2f}s")
    print(f"📊 New: {new_count} | Updated: {updated_count} | Deleted: {deleted_count}")

if __name__ == "__main__":
    index_scripts()
