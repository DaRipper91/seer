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
    """Extracts shebang and description from the first few lines of a file."""
    shebang = None
    description = ""
    try:
        with open(path, 'r', errors='ignore') as f:
            lines = [f.readline().strip() for _ in range(10)]
            if lines and lines[0].startswith("#!"):
                shebang = lines[0]
            
            # Look for a description in the comments
            for line in lines:
                clean = line.lstrip("#/ *")
                if clean and not line.startswith("#!"):
                    # Simple heuristic: the first non-shebang comment line is the description
                    description = clean
                    break
    except Exception:
        pass
    return shebang, description

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
                mtime = os.path.getmtime(path)
                
                # Check if we need to update
                cursor.execute("SELECT mtime FROM scripts WHERE path = ?", (path,))
                row = cursor.fetchone()
                
                if row is None:
                    # New script
                    shebang, description = get_metadata(path)
                    cursor.execute("""
                        INSERT INTO scripts (path, name, extension, shebang, description, mtime)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (path, file, ext, shebang, description, mtime))
                    new_count += 1
                elif row[0] < mtime:
                    # Updated script
                    shebang, description = get_metadata(path)
                    cursor.execute("""
                        UPDATE scripts 
                        SET name = ?, extension = ?, shebang = ?, description = ?, mtime = ?
                        WHERE path = ?
                    """, (file, ext, shebang, description, mtime, path))
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
