import sqlite3
import os
import requests
import struct
import numpy as np
import sys

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
        return None

def blob_to_float_list(blob):
    """Converts a binary BLOB back to a list of floats."""
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))

def cosine_similarity(v1, v2):
    """Calculates cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

def semantic_search(query):
    query_vector = get_embedding(query)
    if not query_vector:
        print("❌ Could not generate embedding for query.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, COALESCE(description, ''), COALESCE(tags, ''), path, COALESCE(linked_configs, ''), run_count, COALESCE(last_run, 'Never'), embedding FROM scripts WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()

    results = []
    for name, description, tags, path, linked_configs, run_count, last_run, blob in rows:
        script_vector = blob_to_float_list(blob)
        similarity = cosine_similarity(query_vector, script_vector)
        results.append((similarity, name, description, tags, path, linked_configs, run_count, last_run))

    # Sort by similarity
    results.sort(key=lambda x: x[0], reverse=True)

    # Print in a format fzf can use: Name | Description | Tags | Path | Configs | Runs | Last Run
    for score, name, desc, tags, path, configs, runs, last in results:
        # Scale score to 0-100 for readability
        score_pct = int(score * 100)
        # We put the score in the name column so the user sees it, but the rest of the columns match exactly.
        print(f"[{score_pct}%] {name} | {desc} | {tags} | {path} | {configs} | {runs} | {last}")

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 seer-search.py <query>")
    else:
        semantic_search(" ".join(sys.argv[1:]))
