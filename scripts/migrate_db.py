import sqlite3
import os

DB_PATH = os.path.expanduser("~/Projects/seer/seer.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔮 Refining the Oracle's Memory (Migrating Database)...")

    # Add new columns if they don't exist
    try:
        cursor.execute("ALTER TABLE scripts ADD COLUMN tags TEXT")
        print("✅ Added 'tags' column.")
    except sqlite3.OperationalError:
        print("ℹ️ 'tags' column already exists.")

    try:
        cursor.execute("ALTER TABLE scripts ADD COLUMN linked_configs TEXT")
        print("✅ Added 'linked_configs' column.")
    except sqlite3.OperationalError:
        print("ℹ️ 'linked_configs' column already exists.")

    # Recreate FTS table to include tags
    cursor.execute("DROP TABLE IF EXISTS scripts_fts")
    cursor.execute("""
    CREATE VIRTUAL TABLE scripts_fts USING fts5(
        path,
        name,
        description,
        tags,
        content='scripts',
        content_rowid='id'
    )
    """)
    
    # Sync FTS with existing data
    cursor.execute("INSERT INTO scripts_fts(rowid, path, name, description, tags) SELECT id, path, name, description, tags FROM scripts")

    # Recreate Triggers for new FTS schema
    cursor.execute("DROP TRIGGER IF EXISTS scripts_ai")
    cursor.execute("""
    CREATE TRIGGER scripts_ai AFTER INSERT ON scripts BEGIN
        INSERT INTO scripts_fts(rowid, path, name, description, tags) VALUES (new.id, new.path, new.name, new.description, new.tags);
    END;
    """)

    cursor.execute("DROP TRIGGER IF EXISTS scripts_ad")
    cursor.execute("""
    CREATE TRIGGER scripts_ad AFTER DELETE ON scripts BEGIN
        INSERT INTO scripts_fts(scripts_fts, rowid, path, name, description, tags) VALUES('delete', old.id, old.path, old.name, old.description, old.tags);
    END;
    """)

    cursor.execute("DROP TRIGGER IF EXISTS scripts_au")
    cursor.execute("""
    CREATE TRIGGER scripts_au AFTER UPDATE ON scripts BEGIN
        INSERT INTO scripts_fts(scripts_fts, rowid, path, name, description, tags) VALUES('delete', old.id, old.path, old.name, old.description, old.tags);
        INSERT INTO scripts_fts(rowid, path, name, description, tags) VALUES (new.id, new.path, new.name, new.description, new.tags);
    END;
    """)

    conn.commit()
    conn.close()
    print("✨ Migration complete.")

if __name__ == "__main__":
    migrate()
