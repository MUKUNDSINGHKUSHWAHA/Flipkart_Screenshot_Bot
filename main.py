import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
from utils import sanitize_filename, create_output_folder
from PIL import Image
from Input_reader import read_keywords
from screenshot import capture_long_screenshot
from driver_setup import setup_mobile_driver
import threading

class FlipkartScreenshotBot:
    def __init__(self, root):
        # Color scheme - defined FIRST
        self.BG_COLOR = "#F4F4F9"
        self.FRAME_BG = "#F4F4F9"
        self.FRAME_BORDER = "#BDC3C7"
        self.HEADER_BG = "#232F3E"  
        self.HEADER_FG = "#FFFFFF"
        self.BUTTON_BG = "#FF9900" 
        self.BUTTON_FG = "#000000"
        self.BUTTON_HOVER = "#FF8C00"  # Darker orange
        self.ACCENT_COLOR = "#146EB4" 
        self.ACCENT_HOVER = "#0F5B9E"
        self.STATUS_FG = "#2C3E50"
        self.FOOTER_BG = "#D6DBDF"
        self.FONT_FAMILY = "Segoe UI"
        self.SUCCESS_COLOR = "#00A65A"
        self.DROP_HIGHLIGHT = "#E1E8ED"
        
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        # Configure root window
        self.root.title("Flipkart Screenshot Bot")
        self.root.geometry("600x550")
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)
        
        # Header Frame
        header_frame = tk.Frame(self.root, bg=self.HEADER_BG, height=80)
        header_frame.pack(fill=tk.X)
        
        tk.Label(
            header_frame,
            text="Flipkart Screenshot Bot",
            font=(self.FONT_FAMILY, 20, "bold"),
            bg=self.HEADER_BG,
            fg=self.HEADER_FG
        ).pack(pady=20)
        
        # Main Content Frame
        main_frame = tk.Frame(self.root, bg=self.FRAME_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File Selection Section with drag and drop
        file_frame = tk.LabelFrame(
            main_frame,
            text=" File Selection ",
            font=(self.FONT_FAMILY, 12),
            bg=self.FRAME_BG,
            fg=self.STATUS_FG,
            bd=2,
            relief=tk.GROOVE
        )
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Configure drag and drop
        file_frame.drop_target_register(DND_FILES)
        file_frame.dnd_bind('<<Drop>>', self.on_drop)
        file_frame.dnd_bind('<<DragEnter>>', lambda e: self.on_drag_enter(e, file_frame))
        file_frame.dnd_bind('<<DragLeave>>', lambda e: self.on_drag_leave(e, file_frame))
        
        # File path variables
        self.file_path = tk.StringVar()
        self.file_name = tk.StringVar()
        self.save_folder = tk.StringVar()
        self.save_folder.set("")
        
        # Upload Button
        upload_btn = tk.Button(
            file_frame,
            text="📁 Upload File (Excel/CSV)",
            command=self.upload_file,
            bg=self.BUTTON_BG,
            fg=self.BUTTON_FG,
            font=(self.FONT_FAMILY, 11, "bold"),
            bd=1,
            relief=tk.RAISED,
            padx=15,
            pady=5,
            activebackground=self.BUTTON_HOVER,
            activeforeground=self.BUTTON_FG
        )
        upload_btn.pack(pady=10)
        
        # Drag and drop hint
        tk.Label(
            file_frame,
            text="--- or drag & drop file here ---",
            fg="#7F8C8D",
            bg=self.FRAME_BG,
            font=(self.FONT_FAMILY, 9, "italic")
        ).pack(pady=(0, 10))
        
        # File info display
        self.file_info_label = tk.Label(
            file_frame,
            textvariable=self.file_name,
            wraplength=500,
            fg=self.SUCCESS_COLOR,
            bg=self.FRAME_BG,
            font=(self.FONT_FAMILY, 10)
        )
        self.file_info_label.pack(pady=(0, 5))
        
        tk.Label(
            file_frame,
            textvariable=self.file_path,
            wraplength=500,
            fg="#7F8C8D",
            bg=self.FRAME_BG,
            font=(self.FONT_FAMILY, 8)
        ).pack()

        # Save Folder Selection
        save_frame = tk.Frame(main_frame, bg=self.FRAME_BG)
        save_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(save_frame, text="Save screenshots/results to:", bg=self.FRAME_BG, fg=self.STATUS_FG, font=(self.FONT_FAMILY, 10)).pack(side=tk.LEFT)
        tk.Label(save_frame, textvariable=self.save_folder, bg=self.FRAME_BG, fg="#7F8C8D", font=(self.FONT_FAMILY, 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(save_frame, text="Choose Save Folder", command=self.choose_save_folder, bg=self.BUTTON_BG, fg=self.BUTTON_FG, font=(self.FONT_FAMILY, 9), bd=1, relief=tk.RAISED, padx=8, pady=2, activebackground=self.BUTTON_HOVER, activeforeground=self.BUTTON_FG).pack(side=tk.LEFT, padx=10)
        
        # Start Button
        start_btn = tk.Button(
            main_frame,
            text="📸 Capture Screenshots",
            command=self.start_job,
            bg=self.ACCENT_COLOR,
            fg=self.HEADER_FG,
            font=(self.FONT_FAMILY, 12, "bold"),
            bd=1,
            relief=tk.RAISED,
            padx=20,
            pady=8,
            activebackground=self.ACCENT_HOVER,
            activeforeground=self.HEADER_FG
        )
        start_btn.pack(pady=15)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            main_frame,
            orient='horizontal',
            length=500,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(10, 5))
        
        # Status Label
        self.status_label = tk.Label(
            main_frame,
            text="Ready to start. Please upload a file with keywords.",
            wraplength=500,
            fg=self.STATUS_FG,
            bg=self.FRAME_BG,
            font=(self.FONT_FAMILY, 10)
        )
        self.status_label.pack(pady=10)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg=self.FOOTER_BG, height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Attribution text
        tk.Label(
            footer_frame,
            text="Flipkart Screenshot Bot | Developed By Mukund Singh",
            bg=self.FOOTER_BG,
            fg=self.STATUS_FG,
            font=(self.FONT_FAMILY, 8)
        ).pack()
        
        # Add hover effects
        upload_btn.bind("<Enter>", lambda e: upload_btn.config(bg=self.BUTTON_HOVER))
        upload_btn.bind("<Leave>", lambda e: upload_btn.config(bg=self.BUTTON_BG))
        
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg=self.ACCENT_HOVER))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=self.ACCENT_COLOR))
    
    def on_drag_enter(self, event, widget):
        widget.config(bg=self.DROP_HIGHLIGHT)
        self.file_info_label.config(text="Drop Excel/CSV file here...", fg=self.ACCENT_COLOR)
    
    def on_drag_leave(self, event, widget):
        widget.config(bg=self.FRAME_BG)
        if not self.file_path.get():
            self.file_info_label.config(text="", fg="green")
    
    def on_drop(self, event):
        # Get the dropped file path
        path = event.data.strip()
        
        # Remove curly braces if present (Windows adds them)
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        
        # Check if file has correct extension
        if not (path.lower().endswith('.xlsx') or path.lower().endswith('.xls') or path.lower().endswith('.csv')):
            self.status_label.config(text="Invalid file: Please drop an Excel or CSV file", fg="red")
            return
        
        self.process_file(path)
    
    def upload_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel or CSV", "*.xlsx *.xls *.csv")])
        if path:
            self.process_file(path)
    
    def process_file(self, path):
        self.file_path.set(path)
        self.file_name.set(f"Selected: {os.path.basename(path)}")
        self.status_label.config(text="File selected. Click 'Capture Screenshots' to begin.", fg="green")
    
    def choose_save_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_folder.set(folder)
            self.status_label.config(text="Save folder selected. Ready to start.", fg="green")

    def run_process(self, file_path, save_folder):
        keywords = read_keywords(file_path)
        output_folder = create_output_folder(save_folder)
        summary = []
        failed = []
        
        total = len(keywords)
        completed = 0

        def update_progress():
            percent = int((completed / total) * 100)
            self.progress_bar['value'] = percent
            self.progress_bar.update()
            self.status_label.config(text=f"Processing: {completed}/{total} keywords ({percent}%)", fg=self.ACCENT_COLOR)

        driver = setup_mobile_driver()
        for keyword in keywords:
            try:
                status, filename, notes = capture_long_screenshot(driver, keyword, output_folder)
                if status == "Success":
                    summary.append([keyword, status, filename, ""])
                else:
                    summary.append([keyword, "Failed", "", notes])
                    failed.append(keyword)
            except Exception as e:
                summary.append([keyword, "Failed", "", str(e)])
                failed.append(keyword)
            
            completed += 1
            self.root.after(100, update_progress)
        
        driver.quit()

        summary_df = pd.DataFrame(summary, columns=["Keyword", "Status", "FileName", "Notes"])
        summary_df.to_csv(os.path.join(output_folder, "summary.csv"), index=False)

        if failed:
            failed_df = pd.DataFrame(failed, columns=["Failed Keywords"])
            failed_df.to_excel(os.path.join(output_folder, "failed_keywords.xlsx"), index=False)

        return output_folder
    
    def start_job(self):
        file_path = self.file_path.get()
        save_folder = self.save_folder.get()
        if not file_path:
            self.status_label.config(text="No file selected. Please select an Excel or CSV file.", fg="red")
            return
        if not save_folder:
            self.choose_save_folder()
            save_folder = self.save_folder.get()
            if not save_folder:
                self.status_label.config(text="No folder selected. Please select a folder to save screenshots/results.", fg="red")
                return
        self.status_label.config(text="Processing started...", fg=self.ACCENT_COLOR)
        self.progress_bar['value'] = 0
        
        def run_in_thread():
            try:
                folder = self.run_process(file_path, save_folder)
                self.status_label.config(
                    text=f"✅ Screenshots completed! Results saved to: {folder}",
                    fg=self.SUCCESS_COLOR
                )
                self.progress_bar['value'] = 100
            except Exception as e:
                self.status_label.config(
                    text=f"❌ Error occurred: {str(e)}",
                    fg="red"
                )
                self.progress_bar['value'] = 0
        threading.Thread(target=run_in_thread, daemon=True).start()

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD's Tk for drag and drop
    app = FlipkartScreenshotBot(root)
    root.mainloop()
