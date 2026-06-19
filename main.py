
import difflib
import os
import sys
import tkinter as tk


class DiffApprovalApp(tk.Tk):
    def __init__(self, src_file, dest_file, diff_lines):
        super().__init__()

        # Assign file targets parsed from command line arguments
        self.src_file = src_file
        self.dest_file = dest_file
        self.diff_lines = diff_lines

        # Window Setup (Borderless)
        self.width = 660
        self.height = 540
        self.overrideredirect(True)
        self.configure(bg="#121212")
        
        # Pop the window directly on top of VS Code / terminal environment
        self.attributes("-topmost", True)
        self.center_window()

        # Mouse offset variables for window dragging
        self._offsetx = 0
        self._offsety = 0

        # Colors
        self.bg_tab = "#181818"
        self.bg_box = "#1a1a1a"
        self.theme_gray = "#2d2d30"
        self.hover_gray = "#3e3e42"
        self.text_main = "#d4d4d4"

        # Cross-platform font detection strings
        if sys.platform == "darwin":  
            ui_font_family = "SF Pro Display"
            code_font_family = "Menlo"
        elif sys.platform == "win32": 
            ui_font_family = "Segoe UI"
            code_font_family = "Consolas"
        else:                         
            ui_font_family = "Ubuntu"
            code_font_family = "Liberation Mono"

        self.font_ui_normal = (ui_font_family, 11)
        self.font_code = (code_font_family, 11)

        # 1. WINDOW LAYOUT GRID DEFINITION
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        # 2. CUSTOM TITLE / DRAG BAR (ROW 0)
        self.top_bar = tk.Frame(self, bg=self.bg_tab, height=35)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.pack_propagate(False)

        # Title Label showing exact dynamic files being processed
        lbl_title = tk.Label(self.top_bar, text=f"", bg=self.bg_tab, fg="#ffffff", font=self.font_ui_normal)
        # lbl_title = tk.Label(self.top_bar, text="")
        lbl_title.pack(side="left", padx=10)

        # Close Window Button (✕)
        btn_close = tk.Button(self.top_bar, text="✕", bg=self.bg_tab, fg="#ffffff", activebackground="#e81123", activeforeground="#ffffff", font=self.font_ui_normal, bd=0, relief="flat", cursor="hand2", command=self.destroy, padx=12)
        btn_close.pack(side="right", fill="y")

        # Bind dragging to the top bar and title label
        for widget in (self.top_bar, lbl_title):
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

        # 3. MAIN CONTENT CONTAINER (ROW 1)
        main_content = tk.Frame(self, bg="#121212", padx=20, pady=15)
        main_content.grid(row=1, column=0, sticky="nsew")
        main_content.grid_rowconfigure(1, weight=1) 
        main_content.grid_columnconfigure(0, weight=1)

        # lbl_prompt = tk.Label(main_content, text=f"Review changes to overwrite {os.path.basename(self.src_file)} with content from {os.path.basename(self.dest_file)}:", bg="#121212", fg=self.text_main, font=self.font_ui_normal)
        lbl_prompt = tk.Label(main_content, text=f"Review security changes to overwrite {os.path.basename(self.src_file)}", bg="#121212", fg=self.text_main, font=self.font_ui_normal)
        lbl_prompt.grid(row=0, column=0, sticky="w", pady=10)

        # Code Diff Display Window
        self.diff_box = tk.Text(main_content, bg=self.bg_box, fg=self.text_main, font=self.font_code, bd=1, relief="solid", highlightthickness=0)
        self.diff_box.grid(row=1, column=0, sticky="nsew", pady=10)

        # Configure custom text highlights for our Diff view
        self.diff_box.tag_config("removed", foreground="#f14c4c", background="#3b1d1d")
        self.diff_box.tag_config("added", foreground="#23d160", background="#1b3b1f")
        self.diff_box.tag_config("header", foreground="#858585")

        # Inject the parsed pre-check diff data
        self.populate_file_diff()

        # 4. USER INTERACTION FOOTER (ROW 2)
        footer_frame = tk.Frame(self, bg="#121212", padx=20, pady=20)
        footer_frame.grid(row=2, column=0, sticky="ew")
        footer_frame.grid_columnconfigure(0, weight=1)

        # Prompt Question Label
        self.lbl_question = tk.Label(
            footer_frame, 
            text=f"Do you approve updating {os.path.basename(self.src_file)} with these changes [y/n]?", 
            bg="#121212", fg="#ffffff", font=self.font_ui_normal
        )
        self.lbl_question.grid(row=0, column=0, columnspan=2, sticky="w", pady=10)

        # User Entry Input Text Box
        self.user_input = tk.Entry(
            footer_frame, bg="#252526", fg=self.text_main,
            insertbackground="#ffffff", font=self.font_code,
            bd=1, relief="solid", highlightthickness=0
        )
        self.user_input.grid(row=1, column=0, sticky="ew", ipady=6, padx=(0, 10))
        self.user_input.focus_set()
        
        self.user_input.bind("<Return>", self.evaluate_input)

        # Submit Action Button
        self.btn_submit = tk.Button(
            footer_frame, text="Submit", bg=self.theme_gray, fg="#ffffff",
            activebackground=self.hover_gray, activeforeground="#ffffff",
            font=self.font_ui_normal, bd=0, relief="flat", cursor="hand2", 
            command=self.evaluate_input, padx=25, pady=5
        )
        self.btn_submit.grid(row=1, column=1, sticky="ns")

        # Initialize automatic timeout
        self.timeout_tracker = self.after(300000, self.handle_timeout)

    def populate_file_diff(self):
        """Colorizes the pre-calculated diff lines into the display window."""
        for line in self.diff_lines:
            if line.startswith('-') and not line.startswith('---'):
                self.diff_box.insert("end", f"{line}\n", "removed")
            elif line.startswith('+') and not line.startswith('+++'):
                self.diff_box.insert("end", f"{line}\n", "added")
            elif line.startswith('@'):
                self.diff_box.insert("end", f"{line}\n", "header")
            else:
                self.diff_box.insert("end", f"{line}\n")

        self.diff_box.config(state="disabled")

    def center_window(self):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def do_move(self, event):
        x = self.winfo_x() + event.x - self._offsetx
        y = self.winfo_y() + event.y - self._offsety
        self.geometry(f"+{x}+{y}")

    def evaluate_input(self, event=None):
        raw_text = self.user_input.get().strip().lower()
        
        if raw_text in ['y', 'yes']:
            self.after_cancel(self.timeout_tracker)
            if os.path.exists(self.dest_file):
                try:
                    with open(self.dest_file, "r", encoding="utf-8") as f_src:
                        content = f_src.read()
                    with open(self.src_file, "w", encoding="utf-8") as f_dest:
                        f_dest.write(content)
                    print(f"Workflow Status: Approved. {os.path.basename(self.src_file)} successfully updated.")
                except Exception as e:
                    print(f"Error executing file copy transaction: {e}")
            else:
                print(f"Workflow Status: Error, target source data file missing during sync execution.")
            self.destroy()
            
        elif raw_text in ['n', 'no']:
            self.after_cancel(self.timeout_tracker)
            print("Workflow Status: Changes Ignored. File system untouched.")
            self.destroy()
            
        else:
            self.lbl_question.config(
                text="Invalid input! Please type 'y' or 'n'. Do you approve [y/n]?", 
                fg="#f14c4c"
            )
            self.user_input.delete(0, tk.END)

    def handle_timeout(self):
        print("Workflow Status: Execution Timeout. User response window expired.")
        self.destroy()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("\nUsage: python script_name.py <file_to_overwrite> <file_with_new_changes>")
        print("Example: python script_name.py foo.txt foo1.txt\n")
        sys.exit(1)

    file_to_overwrite = sys.argv[1]
    file_with_changes = sys.argv[2]

    # 1. Check if files exist before processing
    if not os.path.exists(file_to_overwrite) or not os.path.exists(file_with_changes):
        print(f"Error: Ensure both '{file_to_overwrite}' and '{file_with_changes}' exist.")
        sys.exit(1)

    # 2. Read contents for checking
    with open(file_to_overwrite, "r", encoding="utf-8", errors="ignore") as f:
        src_lines = f.readlines()
    with open(file_with_changes, "r", encoding="utf-8", errors="ignore") as f:
        dest_lines = f.readlines()

    # 3. Generate unified diff
    diff_generator = difflib.unified_diff(
        src_lines, dest_lines, 
        fromfile=file_to_overwrite, tofile=file_with_changes, 
        lineterm=''
    )
    computed_diff = list(diff_generator)

    # 4. SILENT TERMINATION CHECK: If list is empty, files are identical
    if not computed_diff:
        print("No differences found. Closing cleanly without actions.")
        sys.exit(0)

    # High-DPI Windows Scaling Fix
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # Start the application only if changes exist
    app = DiffApprovalApp(file_to_overwrite, file_with_changes, computed_diff)
    app.mainloop()
