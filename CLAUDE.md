# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Seer Is

A SQLite-powered script management engine. Users fuzzy-find and execute scripts from across their filesystem via a fish shell TUI (`fzf`), a REST API, and a React web dashboard. The project has three runtime layers: the fish CLI, a Python backend (FastAPI + indexer), and an optional React dashboard.

All paths in scripts are hardcoded to `~/Projects/seer/` — this is intentional for a personal tool.

## Commands

### Python Backend

```bash
# Initialize the database (first-time setup)
python3 scripts/init_db.py

# Index/re-scan scripts into the database
python3 scripts/seer-index.py

# Run schema migrations (adds columns, recreates FTS/triggers)
python3 scripts/migrate_db.py

# Generate embeddings for semantic search (requires Ollama running)
python3 scripts/seer-embed.py

# Start the REST API (port 8888)
python3 scripts/seer-api.py

# Export metadata to seer-metadata.json for cross-machine sync
python3 scripts/seer-sync.py
# Import from seer-metadata.json
python3 scripts/seer-sync.py import

# Auto-backup a script to Chronos vault
python3 scripts/seer-chronos.py backup <script_path>
```

### Web Dashboard

```bash
cd seer-dashboard
npm install
npm run dev      # Vite dev server
npm run build    # TypeScript compile + Vite build
```

The dashboard requires the API server running on port 8888.

### Fish Shell

```fish
# Source the main function (typically done in config.fish)
source ~/Projects/seer/scripts/seer.fish

seer          # Open the TUI
seer-refresh  # Re-index scripts
```

### Systemd Service (The Familiar)

```bash
# Install the watcher service (re-indexes every 60s)
cp assets/seer-watcher.service ~/.config/systemd/user/
systemctl --user enable --now seer-watcher.service
```

## Architecture

### Data Flow

```
Filesystem → seer-index.py → seer.db (SQLite)
                                 ↓
                         seer-embed.py → embedding BLOBs (Ollama: nomic-embed-text)
                                 ↓
               ┌──────────────────────────────────────┐
               │           seer.fish (TUI)            │  ← fzf, direct SQLite queries
               │           seer-api.py (REST)         │  ← FastAPI, port 8888
               │           seer-dashboard/ (React)    │  ← fetches from API
               └──────────────────────────────────────┘
```

### Database Schema (`seer.db`)

- `scripts` table — core metadata: `path`, `name`, `extension`, `shebang`, `description`, `run_count`, `last_run`, `mtime`, `tags`, `linked_configs`, `embedding` (BLOB)
- `scripts_fts` — FTS5 virtual table (content-backed from `scripts`), synced via three triggers (`scripts_ai`, `scripts_ad`, `scripts_au`)
- Migrations are additive `ALTER TABLE` statements in `migrate_db.py`; running it is idempotent

### Indexer (`seer-index.py`)

Walks `ACTIVE_DIRS` (`~/Projects`, `~/scripts`, `~/bin`, `~/.local/bin`, `~/.gemini/extensions`, `~/Jules_Projects`), skipping `EXCLUDED_DIRS`. Detects scripts by extension (`.sh`, `.py`, `.fish`, `.ts`, etc.) or by executable bit + shebang. Metadata (description, tags, linked configs) is parsed from the first 15 lines of each file.

To add a description or tags to a script that Seer will index, put them in comments near the top:
```
# Description text here (first non-shebang comment becomes description)
# Tags: tag1, tag2, tag3
```

### Semantic Search

`seer-embed.py` generates embeddings via Ollama (`nomic-embed-text`) and stores float vectors as packed binary BLOBs (`struct.pack`). `seer-search.py` computes cosine similarity at query time — no vector extension needed.

Requires Ollama running locally at `http://localhost:11434` with `nomic-embed-text` pulled.

### AI Healer (`seer-healer.py`)

When a script exits non-zero from the TUI, the user can pipe stderr to this script. It tries Gemini CLI first, falls back to Ollama (`llama3`). Neither is required — it degrades gracefully.

### Chronos (`seer-chronos.py`)

Every script execution auto-backs up the script file to `~/.seer-chronos/vault/` (a bare git repo). Only commits when the file actually changed (`git status --porcelain`).

### REST API (`seer-api.py`)

- `GET /scripts` — list top 50 by `run_count`, or FTS5 search with `?query=`
- `POST /execute` — runs script in background via `subprocess.Popen`, returns immediately

### Web Dashboard (`seer-dashboard/`)

React 19 + TypeScript + Vite. No router — single-page app. Framer Motion for card animations. All data from the API at `http://localhost:8888` (hardcoded). Tauri is listed as a dev dependency but the desktop build is not yet wired up.

### Cross-Machine Sync (`seer-sync.py`)

Exports `name → {tags, description, run_count}` to `seer-metadata.json` for committing to Git. Import merges by script name, taking the higher `run_count`.
