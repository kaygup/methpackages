#!/usr/bin/env python3
import tkinter as tk
import argparse
import os
import sys
import subprocess

def create_watermark_window():
    # Create a transparent window
    root = tk.Tk()
    root.title("")
    root.attributes("-alpha", 0.7)  # Semi-transparent
    root.attributes("-topmost", True)  # Always on top
    root.overrideredirect(True)  # Remove window decorations
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate position (bottom right corner)
    window_width = 300
    window_height = 50
    x_position = screen_width - window_width - 20
    y_position = screen_height - window_height - 40
    
    # Set window position and size
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    # Create label with the text
    label = tk.Label(
        root, 
        text="Activate Linux\nGo to your settings to activate Linux",
        fg="#999999",  # Windows watermark color (light gray)
        bg="black",
        font=("Segoe UI", 8)
    )
    label.pack(fill=tk.BOTH, expand=True)
    
    return root

def create_autostart_entry(enable=True):
    """Create or remove autostart entry in user's config"""
    autostart_dir = os.path.expanduser("~/.config/autostart")
    autostart_file = os.path.join(autostart_dir, "linuxact.desktop")
    
    if enable:
        # Create autostart directory if it doesn't exist
        os.makedirs(autostart_dir, exist_ok=True)
        
        # Create desktop entry
        with open(autostart_file, "w") as f:
            f.write("""[Desktop Entry]
Type=Application
Name=Linux Activation Watermark
Exec=linuxact --on
Terminal=false
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
""")
    else:
        # Remove autostart file if it exists
        if os.path.exists(autostart_file):
            os.remove(autostart_file)

def is_running():
    """Check if the watermark is already running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "linuxact --on"],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="Linux Activation Watermark")
    parser.add_argument("--on", action="store_true", help="Enable the watermark")
    parser.add_argument("--off", action="store_true", help="Disable the watermark")
    parser.add_argument("--autostart", action="store_true", help="Enable autostart")
    parser.add_argument("--no-autostart", action="store_true", help="Disable autostart")
    
    args = parser.parse_args()
    
    if args.on:
        if is_running():
            print("Linux Activation Watermark is already running")
            sys.exit(0)
            
        print("Starting Linux Activation Watermark")
        root = create_watermark_window()
        root.mainloop()
        
    elif args.off:
        print("Stopping Linux Activation Watermark")
        subprocess.run(["pkill", "-f", "linuxact --on"])
        
    elif args.autostart:
        create_autostart_entry(True)
        print("Linux Activation Watermark added to autostart")
        
    elif args.no_autostart:
        create_autostart_entry(False)
        print("Linux Activation Watermark removed from autostart")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
