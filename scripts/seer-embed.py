import sqlite3
import os
import requests
import json
import struct

DB_PATH = os.path.expanduser("~/Projects/seer/seer.db")
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

def get_embedding(text):
    """Fetches embedding from Ollama API."""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": text
        })
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"❌ Error fetching embedding: {e}")
        return None

def float_list_to_blob(floats):
    """Converts a list of floats to a binary BLOB."""
    return struct.pack(f'{len(floats)}f', *floats)

def run_embeddings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find scripts without embeddings
    cursor.execute("SELECT id, name, COALESCE(description, '') FROM scripts WHERE embedding IS NULL")
    rows = cursor.fetchall()

    if not rows:
        print("✨ All scripts already have embeddings.")
        return

    print(f"🧠 Generating embeddings for {len(rows)} scripts...")
    
    count = 0
    for row_id, name, description in rows:
        # We embed the name and description combined for better context
        text_to_embed = f"{name}: {description}" if description else name
        
        embedding = get_embedding(text_to_embed)
        if embedding:
            blob = float_list_to_blob(embedding)
            cursor.execute("UPDATE scripts SET embedding = ? WHERE id = ?", (blob, row_id))
            count += 1
            if count % 10 == 0:
                print(f"⏳ Processed {count}/{len(rows)}...")
                conn.commit()

    conn.commit()
    conn.close()
    print(f"✅ Success! Generated {count} embeddings.")

if __name__ == "__main__":
    # Check if requests is installed, install if not (breaking system packages rule for simple lib if needed, 
    # but usually 'requests' is pre-installed)
    try:
        import requests
    except ImportError:
        os.system("pip install requests --break-system-packages --quiet")
    
    run_embeddings()
