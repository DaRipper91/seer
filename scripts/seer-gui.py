import customtkinter as ctk
import sqlite3
import socket
import os
import datetime
import json
import threading
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DB_PATH = Path.home() / "Projects" / "seer" / "seer.db"


class SeerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Seer : Astral Dashboard 2.0")
        self.geometry("1000x700")
        self.configure(fg_color="#1a1b26")

        self.found_scripts: list[dict] = []

        self._build_header()
        self._build_inputs()
        self._build_results()
        self._build_footer()

        # Load full DB on start
        self.after(100, self.start_scan_thread)

    def _build_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(20, 6))

        ctk.CTkLabel(
            frame,
            text="🔮 SEER : ASTRAL DASHBOARD 2.0",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#af87ff",
        ).pack(side="left")

        self.db_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#565f89",
        )
        self.db_label.pack(side="right")

    def _build_inputs(self):
        frame = ctk.CTkFrame(self, fg_color="#1f2335", corner_radius=10)
        frame.pack(fill="x", padx=20, pady=(0, 10))

        entry_cfg = dict(
            height=36, corner_radius=8, border_width=2,
            border_color="#7aa2f7", fg_color="#16161e", text_color="#c0caf5",
        )

        self.path_entry = ctk.CTkEntry(
            frame, placeholder_text="Filter by path prefix...", width=360, **entry_cfg)
        self.path_entry.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")

        self.grep_entry = ctk.CTkEntry(
            frame, placeholder_text="Whisper ancient text (search name/desc/tags)...",
            width=400, **entry_cfg)
        self.grep_entry.grid(row=0, column=1, padx=(0, 8), pady=12, sticky="w")

        self.scan_btn = ctk.CTkButton(
            frame, text="Scan", width=90, height=36, corner_radius=8,
            fg_color="#7aa2f7", hover_color="#5f87d7", text_color="#1a1b26",
            font=ctk.CTkFont(weight="bold"),
            command=self.start_scan_thread,
        )
        self.scan_btn.grid(row=0, column=2, padx=(0, 12), pady=12)

        # --- Aether Bridge row ---
        self.aether_entry = ctk.CTkEntry(
            frame, placeholder_text="Selected ritual path (auto-fills from top result)...",
            width=660, **entry_cfg)
        self.aether_entry.grid(row=1, column=0, columnspan=2, padx=(12, 8), pady=(0, 10), sticky="w")

        btn_cfg = dict(height=32, corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"))

        ctk.CTkButton(
            frame, text="⬡ Open in Aether", width=155, **btn_cfg,
            fg_color="#1a0835", hover_color="#2d0f5a", text_color="#c44dff",
            border_width=1, border_color="#c44dff",
            command=lambda: self._send_to_aether("open_file", self.aether_entry.get().strip()),
        ).grid(row=1, column=2, padx=(0, 6), pady=(0, 10), sticky="e")

        ctk.CTkButton(
            frame, text="▶ Run in Aether", width=145, **btn_cfg,
            fg_color="#0a1a0a", hover_color="#1a3a1a", text_color="#7dcfff",
            border_width=1, border_color="#7dcfff",
            command=lambda: self._send_to_aether("run", self.aether_entry.get().strip()),
        ).grid(row=1, column=3, padx=(0, 12), pady=(0, 10), sticky="e")

        self.path_entry.bind("<Return>", lambda e: self.start_scan_thread())
        self.grep_entry.bind("<Return>", lambda e: self.start_scan_thread())

    def _build_results(self):
        ctk.CTkLabel(
            self,
            text="  Detected Rituals",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#565f89",
            anchor="w",
        ).pack(fill="x", padx=20)

        self.main_display = ctk.CTkTextbox(
            self,
            corner_radius=10,
            border_width=1,
            border_color="#3b4261",
            fg_color="#16161e",
            text_color="#7dcfff",
            font=ctk.CTkFont(family="Courier", size=13),
        )
        self.main_display.pack(expand=True, fill="both", padx=20, pady=(4, 10))
        self.main_display.insert("0.0", "Consulting the Oracle...\n")
        self.main_display.configure(state="disabled")

        # Click on a path line → auto-fill the Aether bridge entry
        self.main_display._textbox.bind("<Button-1>", self._on_result_click)

    def _build_footer(self):
        frame = ctk.CTkFrame(self, fg_color="#1f2335", corner_radius=0, height=46)
        frame.pack(fill="x", side="bottom")
        frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            frame,
            text="status: awaiting orders",
            font=ctk.CTkFont(size=11),
            text_color="#565f89",
        )
        self.status_label.pack(side="left", padx=16)

        ctk.CTkButton(
            frame, text="Export Report", width=110, height=30, corner_radius=6,
            fg_color="#2a2d3e", hover_color="#3b4261", text_color="#a9b1d6",
            command=self.export_report,
        ).pack(side="right", padx=(0, 12), pady=8)

        ctk.CTkButton(
            frame, text="Forge All Docs", width=120, height=30, corner_radius=6,
            fg_color="#af87ff", hover_color="#875faf", text_color="#1a1b26",
            font=ctk.CTkFont(weight="bold"),
            command=self.forge_all_docs,
        ).pack(side="right", padx=(0, 6), pady=8)

    # ------------------------------------------------------------------ scan

    def start_scan_thread(self):
        path_filter = self.path_entry.get().strip()
        grep_term = self.grep_entry.get().strip()

        self.found_scripts = []
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.status_label.configure(text="status: consulting the oracle...")
        self._write("", clear=True)

        threading.Thread(
            target=self._run_scan, args=(path_filter, grep_term), daemon=True
        ).start()

    def _run_scan(self, path_filter: str, grep_term: str):
        if not DB_PATH.exists():
            self.main_display.after(
                0, self._write,
                f"⚠️  Database not found at {DB_PATH}\n"
                "Run python3 scripts/init_db.py then seer-index.py first.\n"
            )
            self._reset_btn()
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            conditions, params = [], []

            if path_filter:
                abs_prefix = str(Path(path_filter).expanduser().resolve())
                conditions.append("s.path LIKE ?")
                params.append(f"{abs_prefix}%")

            if grep_term:
                # Try FTS5 first for speed; fall back to LIKE on failure
                try:
                    fts_query = """
                        SELECT s.path, s.name, s.description, s.tags,
                               s.run_count, s.last_run, s.extension
                        FROM scripts s
                        JOIN scripts_fts f ON s.id = f.rowid
                        WHERE scripts_fts MATCH ?
                    """
                    fts_params = [grep_term]
                    if path_filter:
                        abs_prefix = str(Path(path_filter).expanduser().resolve())
                        fts_query += " AND s.path LIKE ?"
                        fts_params.append(f"{abs_prefix}%")
                    fts_query += " ORDER BY rank LIMIT 500"
                    cursor.execute(fts_query, fts_params)
                except sqlite3.OperationalError:
                    like = f"%{grep_term}%"
                    conditions.append("(s.name LIKE ? OR s.description LIKE ? OR s.tags LIKE ?)")
                    params.extend([like, like, like])
                    cursor.execute(self._base_query(conditions), params)
            else:
                cursor.execute(self._base_query(conditions), params)

            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
        except Exception as e:
            self.main_display.after(0, self._write, f"⚠️  DB error: {e}\n")
            self._reset_btn()
            return

        self.found_scripts = rows
        count = len(rows)

        header = (
            f"🔮 Oracle consulted — {count} ritual(s) found"
            + (f"  |  path: {path_filter}" if path_filter else "")
            + (f"  |  search: '{grep_term}'" if grep_term else "")
            + f"\n{'─' * 70}\n"
        )
        self.main_display.after(0, self._write, header, True)

        for script in rows:
            self.main_display.after(0, self._append_script, script)

        # Auto-fill Aether bridge with the top result
        if rows:
            top_path = rows[0].get("path", "")
            self.aether_entry.after(0, lambda: (
                self.aether_entry.delete(0, "end"),
                self.aether_entry.insert(0, top_path),
            ))

        self.status_label.after(
            0, lambda: self.status_label.configure(
                text=f"status: complete | {count} scripts"
            )
        )
        self.db_label.after(
            0, lambda: self.db_label.configure(
                text=f"seer.db  ·  {DB_PATH}"
            )
        )
        self._reset_btn()

    def _base_query(self, conditions: list[str]) -> str:
        base = """
            SELECT s.path, s.name, s.description, s.tags,
                   s.run_count, s.last_run, s.extension
            FROM scripts s
        """
        if conditions:
            base += " WHERE " + " AND ".join(conditions)
        base += " ORDER BY s.run_count DESC, s.last_run DESC, s.name ASC LIMIT 2000"
        return base

    def _reset_btn(self):
        self.scan_btn.after(
            0, lambda: self.scan_btn.configure(state="normal", text="Scan")
        )

    # ------------------------------------------------------------------ display

    def _append_script(self, s: dict):
        name = s.get("name", "unknown")
        path = s.get("path", "")
        desc = s.get("description") or ""
        tags = s.get("tags") or ""
        runs = s.get("run_count", 0)
        last = s.get("last_run") or "never"

        meta = f"▸ {runs} run{'s' if runs != 1 else ''} | last: {last}"
        tag_line = f"  ↳ tags: {tags}" if tags.strip() else ""
        desc_line = f"  ↳ {desc[:120]}" if desc.strip() else ""

        self.main_display.configure(state="normal")
        self.main_display.insert("end", f"\n📄 {name:<45} {meta}\n")
        if desc_line:
            self.main_display.insert("end", f"{desc_line}\n")
        if tag_line:
            self.main_display.insert("end", f"{tag_line}\n")
        self.main_display.insert("end", f"   {path}\n")
        self.main_display.see("end")
        self.main_display.configure(state="disabled")

    def _on_result_click(self, event):
        """When user clicks a path line in results, populate the Aether bridge entry."""
        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")
        line = widget.get(f"{index} linestart", f"{index} lineend").strip()
        # Path lines start with '/' or '~/' after stripping
        if line.startswith("/") or line.startswith("~/"):
            self.aether_entry.delete(0, "end")
            self.aether_entry.insert(0, line)

    def _write(self, text, clear=False):
        self.main_display.configure(state="normal")
        if clear:
            self.main_display.delete("0.0", "end")
        self.main_display.insert("end", text)
        self.main_display.configure(state="disabled")

    # ------------------------------------------------------------------ aether bridge

    def _send_to_aether(self, action: str, path: str):
        if not path:
            self._write("\n⚠️  No path selected for Aether.\n")
            return

        payload = json.dumps({"action": action, "path": path}).encode()
        sock_path = "/tmp/aether-ide"

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(sock_path)
                s.sendall(payload)
            verb = "Opened" if action == "open_file" else "Running"
            self._write(f"\n⬡ {verb} in Aether: {path}\n")
        except FileNotFoundError:
            self._write("\n⚠️  Aether is not running — launch it first.\n")
        except ConnectionRefusedError:
            self._write("\n⚠️  Aether socket refused connection — is Aether open?\n")
        except Exception as e:
            self._write(f"\n⚠️  Aether bridge error: {e}\n")

    # ------------------------------------------------------------------ docs

    def forge_all_docs(self):
        if not self.found_scripts:
            self._write("\n⚠️  No scripts loaded. Run a scan first.\n")
            return
        self._write(f"\n📜 Forging docs for {len(self.found_scripts)} script(s)...\n")
        threading.Thread(target=self._forge_all, daemon=True).start()

    def _forge_all(self):
        doc_dir = Path.home() / "Projects" / "seer" / "seer_manuals"
        doc_dir.mkdir(parents=True, exist_ok=True)
        for s in self.found_scripts:
            out = self._build_doc(s, doc_dir)
            self.main_display.after(0, self._write, f"  📖 {out}\n")
        self.main_display.after(0, self._write, f"\n✔️  All docs forged → {doc_dir}\n")

    def _build_doc(self, s: dict, doc_dir: Path) -> str:
        path = Path(s.get("path", ""))
        name = s.get("name", path.name)
        description = s.get("description") or "No description found."
        tags = s.get("tags") or "None"
        runs = s.get("run_count", 0)
        ext = s.get("extension") or path.suffix or "executable"

        dependencies = []
        try:
            content = path.read_text(errors="ignore")
            lines = content.splitlines()
            if ext == ".py":
                dependencies = [
                    l.replace("import ", "").replace("from ", "").split()[0]
                    for l in lines if l.startswith("import ") or l.startswith("from ")
                ]
        except Exception:
            pass

        doc_path = doc_dir / f"{path.stem}_man.md"
        doc_path.write_text(
            f"# {name.upper()} Manual\n\n"
            f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  \n"
            f"**Path:** `{path}`  \n"
            f"**Type:** `{ext}`  \n"
            f"**Run count:** {runs}  \n"
            f"**Tags:** {tags}\n\n"
            f"---\n\n"
            f"## Purpose\n{description}\n\n"
            f"## Dependencies\n"
            f"{', '.join(set(dependencies)) if dependencies else 'None detected.'}\n\n"
            f"## Usage\n```bash\n./{name}\n```\n"
        )
        return str(doc_path)

    # ------------------------------------------------------------------ export

    def export_report(self):
        if not self.found_scripts:
            self._write("\n⚠️  No scripts to export. Run a scan first.\n")
            return

        out_path = (
            Path.home() / "Projects" / "seer"
            / f"seer_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report = {
            "generated": datetime.datetime.now().isoformat(),
            "total": len(self.found_scripts),
            "scripts": [
                {
                    "name": s.get("name"),
                    "path": s.get("path"),
                    "description": s.get("description"),
                    "tags": s.get("tags"),
                    "run_count": s.get("run_count"),
                    "last_run": s.get("last_run"),
                }
                for s in self.found_scripts
            ],
        }
        out_path.write_text(json.dumps(report, indent=2))
        self._write(f"\n📊 Report exported → {out_path}\n")


if __name__ == "__main__":
    app = SeerDashboard()
    app.mainloop()
