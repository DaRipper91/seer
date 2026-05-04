from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import sqlite3
import os
import subprocess

app = FastAPI(title="Seer: The Wand & Word API", description="Mystical execution endpoint for the Eye of Automation")
DB_PATH = os.path.expanduser("~/Projects/seer/seer.db")

class ExecuteRequest(BaseModel):
    path: str
    args: list[str] = []

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.get("/scripts")
def get_scripts(query: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if query:
        cursor.execute("SELECT name, description, tags, path, run_count FROM scripts_fts WHERE scripts_fts MATCH ? ORDER BY rank LIMIT 20", (query,))
    else:
        cursor.execute("SELECT name, description, tags, path, run_count FROM scripts ORDER BY run_count DESC LIMIT 50")
        
    results = cursor.fetchall()
    conn.close()
    return {"scripts": results}

def run_script_background(path: str, args: list[str]):
    if path.endswith(".fish"):
        cmd = ["fish", path] + args
    elif path.endswith(".py"):
        cmd = ["python3", path] + args
    else:
        cmd = ["bash", path] + args
        
    try:
        # Run detached in background
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Update run count
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE scripts SET run_count = run_count + 1, last_run = CURRENT_TIMESTAMP WHERE path = ?", (path,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"API Error running script: {e}")

@app.post("/execute")
def execute_script(req: ExecuteRequest, background_tasks: BackgroundTasks):
    if not os.path.exists(req.path):
        raise HTTPException(status_code=404, detail="Script not found.")
        
    background_tasks.add_task(run_script_background, req.path, req.args)
    return {"status": "Incantation casting in background...", "path": req.path}

if __name__ == "__main__":
    import uvicorn
    print("🔮 The Wand is active. Listening on port 8888...")
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="warning")
