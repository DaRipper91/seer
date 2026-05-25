import customtkinter as ctk
import os
import datetime
import json
import threading
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SCRIPT_EXTENSIONS = {'.py', '.fish', '.sh', '.bash', '.rb', '.js', '.ts', '.lua', '.pl'}


class SeerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Seer : Astral Dashboard 2.0")
        self.geometry("1000x680")
        self.configure(fg_color="#1a1b26")

        self.found_scripts = []

        self._build_header()
        self._build_inputs()
        self._build_results()
        self._build_footer()

    def _build_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(20, 6))

        ctk.CTkLabel(
            frame,
            text="🔮 SEER : ASTRAL DASHBOARD 2.0",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#af87ff",
        ).pack(side="left")

        ctk.CTkLabel(
            frame,
            text="can view in Aether?",
            font=ctk.CTkFont(size=11),
            text_color="#565f89",
        ).pack(side="right")

    def _build_inputs(self):
        frame = ctk.CTkFrame(self, fg_color="#1f2335", corner_radius=10)
        frame.pack(fill="x", padx=20, pady=(0, 10))

        entry_cfg = dict(height=36, corner_radius=8, border_width=2,
                         border_color="#7aa2f7", fg_color="#16161e", text_color="#c0caf5")

        self.path_entry = ctk.CTkEntry(
            frame, placeholder_text="Path to scan...", width=380, **entry_cfg)
        self.path_entry.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")

        self.grep_entry = ctk.CTkEntry(
            frame, placeholder_text="Whisper ancient text (grep)...", width=380, **entry_cfg)
        self.grep_entry.grid(row=0, column=1, padx=(0, 8), pady=12, sticky="w")

        self.scan_btn = ctk.CTkButton(
            frame, text="Scan", width=90, height=36, corner_radius=8,
            fg_color="#7aa2f7", hover_color="#5f87d7", text_color="#1a1b26",
            font=ctk.CTkFont(weight="bold"),
            command=self.start_scan_thread,
        )
        self.scan_btn.grid(row=0, column=2, padx=(0, 12), pady=12)

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
        self.main_display.insert("0.0", "System idle. Enter a path and press Scan.\n")
        self.main_display.configure(state="disabled")

    def _build_footer(self):
        frame = ctk.CTkFrame(self, fg_color="#1f2335", corner_radius=0, height=46)
        frame.pack(fill="x", side="bottom")
        frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            frame,
            text="status: awaiting orders | 0 scripts found",
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
        target_dir = self.path_entry.get().strip() or "."
        grep_term = self.grep_entry.get().strip()

        if not os.path.isdir(target_dir):
            self._write(f"⚠️  Directory '{target_dir}' does not exist.\n", clear=True)
            return

        self.found_scripts = []
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.status_label.configure(text=f"status: scanning... | 0 scripts found")
        self._write(
            f"🔮 Scanning: {os.path.abspath(target_dir)}"
            + (f"  |  grep: '{grep_term}'" if grep_term else "")
            + f"\n{'─' * 70}\n",
            clear=True,
        )

        threading.Thread(
            target=self._run_scan, args=(target_dir, grep_term), daemon=True
        ).start()

    def _run_scan(self, target_dir, grep_term):
        found = []

        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                       {'node_modules', '__pycache__', '.git', 'venv', '.cargo'}]

            for file in files:
                path = Path(root) / file
                if not self._is_script(path):
                    continue

                if grep_term and not self._grep(path, grep_term):
                    continue

                found.append(path)
                self.main_display.after(0, self._append, str(path))

        self.found_scripts = found
        count = len(found)
        self.main_display.after(
            0, self._append, f"\n{'─' * 70}\n✔️  Seer found {count} script(s)."
        )
        self.status_label.after(
            0, lambda: self.status_label.configure(
                text=f"status: scan complete | {count} scripts found"
            )
        )
        self.scan_btn.after(0, lambda: self.scan_btn.configure(state="normal", text="Scan"))

    def _is_script(self, path: Path) -> bool:
        if path.suffix in SCRIPT_EXTENSIONS:
            return True
        try:
            if os.access(path, os.X_OK) and not path.suffix:
                with open(path, 'rb') as f:
                    return f.read(2) == b'#!'
        except Exception:
            pass
        return False

    def _grep(self, path: Path, term: str) -> bool:
        try:
            return term.lower() in path.read_text(errors='ignore').lower()
        except Exception:
            return False

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
        for path in self.found_scripts:
            out = self._build_doc(path, doc_dir)
            self.main_display.after(0, self._append, f"📖 {out}")
        self.main_display.after(0, self._append, f"\n✔️  All docs forged → {doc_dir}")

    def _build_doc(self, path: Path, doc_dir: Path) -> str:
        try:
            content = path.read_text(errors='ignore')
            lines = content.splitlines()
        except Exception:
            return f"(could not read {path.name})"

        description, dependencies = "No description found.", []

        if path.suffix == '.py':
            if '"""' in content:
                try:
                    description = content.split('"""')[1].strip().splitlines()[0]
                except IndexError:
                    pass
            dependencies = [
                l.replace('import ', '').replace('from ', '').split()[0]
                for l in lines if l.startswith('import ') or l.startswith('from ')
            ]
        elif path.suffix in {'.fish', '.sh', '.bash'}:
            comments = [l.lstrip('#').strip() for l in lines
                        if l.startswith('#') and not l.startswith('#!')]
            if comments:
                description = ' '.join(comments[:3])

        doc_path = doc_dir / f"{path.stem}_man.md"
        doc_path.write_text(
            f"# {path.name.upper()} Manual\n\n"
            f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}  \n"
            f"**Path:** `{path.absolute()}`  \n"
            f"**Type:** `{path.suffix or 'executable'}`\n\n"
            f"---\n\n"
            f"## Purpose\n{description}\n\n"
            f"## Dependencies\n"
            f"{', '.join(set(dependencies)) if dependencies else 'None detected.'}\n\n"
            f"## Usage\n```bash\n./{path.name}\n```\n"
        )
        return str(doc_path) + "\n"

    # ------------------------------------------------------------------ export

    def export_report(self):
        if not self.found_scripts:
            self._write("\n⚠️  No scripts to export. Run a scan first.\n")
            return

        out_path = Path.home() / "Projects" / "seer" / f"seer_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            "generated": datetime.datetime.now().isoformat(),
            "total": len(self.found_scripts),
            "scripts": [str(p) for p in self.found_scripts],
        }
        out_path.write_text(json.dumps(report, indent=2))
        self._write(f"\n📊 Report exported → {out_path}\n")

    # ------------------------------------------------------------------ helpers

    def _write(self, text, clear=False):
        self.main_display.configure(state="normal")
        if clear:
            self.main_display.delete("0.0", "end")
        self.main_display.insert("end", text)
        self.main_display.configure(state="disabled")

    def _append(self, text):
        self.main_display.configure(state="normal")
        self.main_display.insert("end", f"  {text}\n")
        self.main_display.see("end")
        self.main_display.configure(state="disabled")


if __name__ == "__main__":
    app = SeerDashboard()
    app.mainloop()
