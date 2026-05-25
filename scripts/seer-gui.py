import customtkinter as ctk
import os
from pathlib import Path
import threading

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue") 

class SeerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Seer : Astral Dashboard")
        self.geometry("900x600")
        self.configure(fg_color="#1a1b26") 

        # --- Top Header Frame ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="💡 ASTRAL DASHBOARD", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#a9b1d6"
        )
        self.title_label.pack(side="left")

        self.intent_entry = ctk.CTkEntry(
            self.header_frame,
            placeholder_text="Whisper your intent (e.g., /home/user/projects)...",
            width=350,
            height=35,
            corner_radius=15,
            border_width=2,
            border_color="#7aa2f7", 
            fg_color="#1f2335",
            text_color="#c0caf5"
        )
        self.intent_entry.pack(side="right")
        self.intent_entry.bind("<Return>", self.start_scan_thread)

        # --- Main Content Area ---
        self.main_display = ctk.CTkTextbox(
            self,
            corner_radius=10,
            border_width=1,
            border_color="#3b4261",
            fg_color="#16161e",
            text_color="#7dcfff",
            font=ctk.CTkFont(family="Courier", size=14)
        )
        self.main_display.pack(expand=True, fill="both", padx=20, pady=10)
        
        self.main_display.insert("0.0", "System idle. Whisper a directory path above and press Enter to initiate Seer.\n")
        self.main_display.configure(state="disabled") 

        # --- Footer Status Bar ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=20, pady=(10, 20))

        self.status_label = ctk.CTkLabel(
            self.footer_frame, 
            text="status: awaiting orders | 0 scripts found", 
            font=ctk.CTkFont(size=12),
            text_color="#565f89"
        )
        self.status_label.pack(side="right")

    def start_scan_thread(self, event):
        """Runs the scan in a background thread so the GUI doesn't freeze."""
        target_dir = self.intent_entry.get().strip()
        if not target_dir:
            target_dir = "." 
            
        if not os.path.isdir(target_dir):
            self.update_display(f"⚠️ Error: Directory '{target_dir}' does not exist.\n")
            return

        self.status_label.configure(text=f"status: scanning {target_dir}... | 0 scripts found")
        self.update_display(f"🔮 Seer is scanning path: {os.path.abspath(target_dir)}\n" + "-" * 60 + "\n", clear=True)
        
        # Dispatch the actual search to prevent locking up the UI
        threading.Thread(target=self.run_scan, args=(target_dir,), daemon=True).start()

    def run_scan(self, target_dir):
        """The core engine that hunts down the scripts."""
        script_extensions = {'.py', '.fish', '.sh', '.bash', '.rb', '.js'}
        found_count = 0
        
        for root, _, files in os.walk(target_dir):
            for file in files:
                file_path = Path(root) / file
                # Check for extension or executable status
                if file_path.suffix in script_extensions or (os.access(file_path, os.X_OK) and not file_path.suffix):
                    found_count += 1
                    # Update the text box safely from the thread
                    self.main_display.after(0, self.append_result, str(file_path))
                    
        # Update final status
        self.status_label.after(0, lambda: self.status_label.configure(text=f"status: scan complete | {found_count} scripts found"))
        self.main_display.after(0, self.append_result, f"\n{'-'*60}\n✔️ Seer found {found_count} scripts.")

    def update_display(self, text, clear=False):
        self.main_display.configure(state="normal")
        if clear:
            self.main_display.delete("0.0", "end")
        self.main_display.insert("end", text)
        self.main_display.configure(state="disabled")

    def append_result(self, text):
        self.main_display.configure(state="normal")
        self.main_display.insert("end", f"📄 {text}\n")
        self.main_display.see("end") # Auto-scroll to bottom
        self.main_display.configure(state="disabled")

if __name__ == "__main__":
    app = SeerDashboard()
    app.mainloop()