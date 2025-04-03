#!/usr/bin/env python3

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk

class TkEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("TkEdit - Simple Text Editor")
        self.filename = None
        self.setup_ui()
        
    def setup_ui(self):
        # Set window size and make it resizable
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        
        # Create menu bar
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create text widget with scrollbar
        self.create_text_area()
        
        # Create status bar
        self.create_status_bar()
        
        # Set keyboard shortcuts
        self.bind_shortcuts()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Format menu
        format_menu = tk.Menu(menubar, tearoff=0)
        format_menu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
        
        # Font submenu
        font_menu = tk.Menu(format_menu, tearoff=0)
        font_menu.add_command(label="Increase Font Size", command=self.increase_font_size, accelerator="Ctrl++")
        font_menu.add_command(label="Decrease Font Size", command=self.decrease_font_size, accelerator="Ctrl+-")
        font_menu.add_separator()
        
        # Add common fonts
        self.font_var = tk.StringVar()
        self.font_var.set("TkDefaultFont")
        for font_name in ["TkDefaultFont", "Courier", "Helvetica", "Times"]:
            font_menu.add_radiobutton(
                label=font_name, 
                variable=self.font_var, 
                value=font_name,
                command=self.change_font
            )
        
        format_menu.add_cascade(label="Font", menu=font_menu)
        menubar.add_cascade(label="Format", menu=format_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky="ew")
        
        # New button
        new_btn = ttk.Button(toolbar, text="New", command=self.new_file)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Open button
        open_btn = ttk.Button(toolbar, text="Open", command=self.open_file)
        open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Save button
        save_btn = ttk.Button(toolbar, text="Save", command=self.save_file)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, pady=2, fill="y")
        
        # Cut button
        cut_btn = ttk.Button(toolbar, text="Cut", command=self.cut_text)
        cut_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Copy button
        copy_btn = ttk.Button(toolbar, text="Copy", command=self.copy_text)
        copy_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Paste button
        paste_btn = ttk.Button(toolbar, text="Paste", command=self.paste_text)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)
    
    def create_text_area(self):
        # Create frame for text area and scrollbar
        text_frame = ttk.Frame(self.root)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        # Create a scrollbar
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create a horizontalscrollbar
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Create the text widget
        self.text_area = tk.Text(
            text_frame, 
            wrap="none", 
            undo=True,
            font=("TkDefaultFont", 12),
            yscrollcommand=scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.text_area.grid(row=0, column=0, sticky="nsew")
        
        # Configure scrollbars
        scrollbar.config(command=self.text_area.yview)
        h_scrollbar.config(command=self.text_area.xview)
        
        # Set focus to the text area
        self.text_area.focus_set()
        
        # Configure tags for syntax highlighting (basic example)
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("string", foreground="green")
        self.text_area.tag_configure("comment", foreground="gray")
    
    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            anchor="w", 
            relief="sunken"
        )
        status_bar.grid(row=2, column=0, sticky="ew")
        
        # Update cursor position in status bar
        self.text_area.bind("<KeyRelease>", self.update_status)
        self.text_area.bind("<ButtonRelease-1>", self.update_status)
    
    def bind_shortcuts(self):
        # File operations
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_as())
        self.root.bind("<Control-q>", lambda event: self.exit_app())
        
        # Edit operations
        self.root.bind("<Control-a>", lambda event: self.select_all())
        
        # Format operations
        self.root.bind("<Control-plus>", lambda event: self.increase_font_size())
        self.root.bind("<Control-minus>", lambda event: self.decrease_font_size())
    
    def new_file(self):
        if self.check_save():
            self.text_area.delete(1.0, tk.END)
            self.filename = None
            self.root.title("TkEdit - New File")
            self.status_var.set("New file created")
    
    def open_file(self):
        if self.check_save():
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Text files", "*.txt"), 
                    ("Python files", "*.py"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                try:
                    with open(file_path, "r") as file:
                        file_content = file.read()
                    
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, file_content)
                    self.filename = file_path
                    self.root.title(f"TkEdit - {os.path.basename(file_path)}")
                    self.status_var.set(f"Opened {file_path}")
                    
                    # Basic syntax highlighting for Python files
                    if file_path.endswith(".py"):
                        self.highlight_python_syntax()
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        if self.filename:
            try:
                with open(self.filename, "w") as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.status_var.set(f"Saved {self.filename}")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        else:
            return self.save_as()
    
    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"), 
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.filename = file_path
            self.root.title(f"TkEdit - {os.path.basename(file_path)}")
            return self.save_file()
        
        return False
    
    def check_save(self):
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Do you want to save changes?"
            )
            
            if response is None:  # Cancel
                return False
            elif response:  # Yes
                return self.save_file()
            else:  # No
                return True
        return True
    
    def exit_app(self):
        if self.check_save():
            self.root.destroy()
    
    def cut_text(self):
        if self.text_area.tag_ranges(tk.SEL):
            self.copy_text()
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.status_var.set("Cut selection")
    
    def copy_text(self):
        if self.text_area.tag_ranges(tk.SEL):
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.status_var.set("Copied selection")
    
    def paste_text(self):
        try:
            text = self.root.clipboard_get()
            if self.text_area.tag_ranges(tk.SEL):
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, text)
            self.status_var.set("Pasted text")
        except tk.TclError:
            pass
    
    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        self.status_var.set("Selected all text")
    
    def toggle_word_wrap(self):
        current_wrap = self.text_area.cget("wrap")
        new_wrap = "word" if current_wrap == "none" else "none"
        self.text_area.configure(wrap=new_wrap)
        wrap_status = "on" if new_wrap == "word" else "off"
        self.status_var.set(f"Word wrap: {wrap_status}")
    
    def increase_font_size(self):
        current_font = font.Font(font=self.text_area["font"])
        size = current_font.actual()["size"] + 2
        self.text_area.configure(font=(current_font.actual()["family"], size))
        self.status_var.set(f"Font size: {size}")
    
    def decrease_font_size(self):
        current_font = font.Font(font=self.text_area["font"])
        size = max(8, current_font.actual()["size"] - 2)
        self.text_area.configure(font=(current_font.actual()["family"], size))
        self.status_var.set(f"Font size: {size}")
    
    def change_font(self):
        font_name = self.font_var.get()
        current_font = font.Font(font=self.text_area["font"])
        size = current_font.actual()["size"]
        self.text_area.configure(font=(font_name, size))
        self.status_var.set(f"Font: {font_name}")
    
    def update_status(self, event=None):
        position = self.text_area.index(tk.INSERT).split(".")
        line, column = position[0], position[1]
        self.status_var.set(f"Line: {line} | Column: {column}")
    
    def highlight_python_syntax(self):
        # Basic Python syntax highlighting (simplified)
        # This is a very basic implementation - a real one would be more complex
        content = self.text_area.get(1.0, tk.END)
        
        # Clear existing tags
        for tag in ["keyword", "string", "comment"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)
        
        # Simple keywords
        keywords = ["import", "from", "def", "class", "if", "elif", "else", 
                   "while", "for", "try", "except", "finally", "return", 
                   "with", "as", "in", "is", "not", "and", "or", "True", 
                   "False", "None"]
        
        for keyword in keywords:
            start_index = "1.0"
            while True:
                start_index = self.text_area.search(r'\y' + keyword + r'\y', start_index, tk.END, regexp=True)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(keyword)}c"
                self.text_area.tag_add("keyword", start_index, end_index)
                start_index = end_index
    
    def show_about(self):
        messagebox.showinfo(
            "About TkEdit",
            "TkEdit - A Simple Text Editor\n\n"
            "Created with Python and Tkinter\n"
            "Part of the meth package manager demo"
        )

def main():
    root = tk.Tk()
    editor = TkEditor(root)
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                editor.text_area.delete(1.0, tk.END)
                editor.text_area.insert(1.0, file.read())
            editor.filename = filename
            root.title(f"TkEdit - {os.path.basename(filename)}")
            
            # Basic syntax highlighting for Python files
            if filename.endswith(".py"):
                editor.highlight_python_syntax()
    
    root.mainloop()

if __name__ == "__main__":
    main()
