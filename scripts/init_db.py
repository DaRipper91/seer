import sqlite3
import os

DB_PATH = os.path.expanduser("~/Projects/seer/seer.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Core metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        extension TEXT,
        shebang TEXT,
        description TEXT,
        last_run DATETIME,
        run_count INTEGER DEFAULT 0,
        mtime REAL NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # FTS5 Virtual Table for fast searching
    # We include path, name, and description for full-text indexing
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS scripts_fts USING fts5(
        path,
        name,
        description,
        content='scripts',
        content_rowid='id'
    )
    """)

    # Triggers to keep FTS in sync with the main table
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS scripts_ai AFTER INSERT ON scripts BEGIN
        INSERT INTO scripts_fts(rowid, path, name, description) VALUES (new.id, new.path, new.name, new.description);
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS scripts_ad AFTER DELETE ON scripts BEGIN
        INSERT INTO scripts_fts(scripts_fts, rowid, path, name, description) VALUES('delete', old.id, old.path, old.name, old.description);
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS scripts_au AFTER UPDATE ON scripts BEGIN
        INSERT INTO scripts_fts(scripts_fts, rowid, path, name, description) VALUES('delete', old.id, old.path, old.name, old.description);
        INSERT INTO scripts_fts(rowid, path, name, description) VALUES (new.id, new.path, new.name, new.description);
    END;
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
