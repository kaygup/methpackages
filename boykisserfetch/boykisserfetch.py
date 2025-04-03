#!/usr/bin/env python3

import os
import platform
import subprocess
import re
from datetime import datetime

# Trans flag colors in ANSI format
COLORS = [
    "\033[38;5;81m",  # Light Blue
    "\033[38;5;211m", # Pink
    "\033[38;5;255m", # White
    "\033[38;5;211m", # Pink
    "\033[38;5;81m"   # Light Blue
]
RESET = "\033[0m"

# ASCII art
BOY_ASCII = """
⠀⠀⠀⢰⠶⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠶⠲⣄⠀
⠀⠀⣠⡟⠀⠈⠙⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡶⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠾⠋⠁⠀⠀⢽⡄
⠀⠀⡿⠀⠀⠀⠀⠀⠉⠷⣄⣀⣤⠤⠤⠤⠤⢤⣷⡀⠙⢷⡄⠀⠀⠀⠀⣠⠞⠉⠀⠀⠀⠀⠀⠈⡇
⠀⢰⡇⠀⠀⠀⠀⠀⠀⠀⠉⠳⣄⠀⠀⠀⠀⠀⠈⠁⠀⠀⠹⣦⠀⣠⡞⠁⠀⠀⠀⠀⠀⠀⠀⠀⡗
⠀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣻⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣏
⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡇
⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠂
⠀⢿⠀⠀⠀⠀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣤⣤⣤⡀⠀⠀⠀⠀⠀⣸⠇⠀
⠀⠘⣇⠀⠀⠀⠀⠉⠉⠛⠛⢿⣶⣦⠀⠀⠀⠀⠀⠀⢴⣾⣟⣛⡋⠋⠉⠉⠁⠀⠀⠀⠀⣴⠏⠀⠀
⢀⣀⠙⢷⡄⠀⠀⣀⣤⣶⣾⠿⠋⠁⠀⢴⠶⠶⠄⠀⠀⠉⠙⠻⠿⣿⣷⣶⡄⠀⠀⡴⠾⠛⠛⣹⠇
⢸⡍⠉⠉⠉⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⣬⠷⣆⣠⡤⠄⢀⣤⠞⠁⠀
⠈⠻⣆⡀⠶⢻⣇⡴⠖⠀⠀⠀⣴⡀⣀⡴⠚⠳⠦⣤⣤⠾⠀⠀⠀⠀⠀⠘⠟⠋⠀⠀⠀⢻⣄⠀⠀
⠀⠀⣼⠃⠀⠀⠉⠁⠀⠀⠀⠀⠈⠉⢻⡆⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⠀
⠀⢠⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡀⠀⠀⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⣀⡿⠧⠿⠿⠟⠀⠀
⠀⣾⡴⠖⠛⠳⢦⣿⣶⣄⣀⠀⠀⠀⠀⠘⢷⣀⠀⣸⠃⠀⠀⠀⣀⣀⣤⠶⠚⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⢷⡀⠈⠻⠦⠀⠀⠀⠀⠉⠉⠁⠀⠀⠀⠀⠹⣆⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡴⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠛⠛⢲⡗⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠋⠀⠀⠀⠀⠀⠀⠀
"""

def get_system_info():
    """Get system information"""
    info = {}
    
    # Hostname and username
    info["user"] = os.getenv("USER", "unknown")
    info["hostname"] = platform.node()
    
    # OS Information
    info["os"] = platform.system()
    info["kernel"] = platform.release()
    
    # Uptime
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.read().split()[0])
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            info["uptime"] = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    except:
        info["uptime"] = "Unknown"
    
    # Shell
    info["shell"] = os.path.basename(os.getenv("SHELL", "unknown"))
    
    # Desktop Environment
    info["de"] = os.getenv("XDG_CURRENT_DESKTOP", "Unknown")
    
    # Terminal
    info["terminal"] = os.getenv("TERM", "Unknown")
    
    # CPU
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpu_info = f.read()
        model_name = re.search(r"model name\s*:\s*(.*)", cpu_info)
        if model_name:
            info["cpu"] = model_name.group(1)
        else:
            info["cpu"] = "Unknown"
    except:
        info["cpu"] = "Unknown"
    
    # Memory
    try:
        with open("/proc/meminfo", "r") as f:
            mem_info = f.read()
        total_memory = re.search(r"MemTotal:\s*(\d+)", mem_info)
        if total_memory:
            mem_kb = int(total_memory.group(1))
            info["memory"] = f"{mem_kb // 1024} MB"
        else:
            info["memory"] = "Unknown"
    except:
        info["memory"] = "Unknown"
    
    return info

def display_fetch():
    info = get_system_info()
    
    # Split the ASCII art into lines
    ascii_lines = BOY_ASCII.strip().split('\n')
    
    # Prepare the system info lines
    info_lines = [
        f"{info['user']}@{info['hostname']}",
        f"OS: {info['os']}",
        f"Kernel: {info['kernel']}",
        f"Uptime: {info['uptime']}",
        f"Shell: {info['shell']}",
        f"DE: {info['de']}",
        f"Terminal: {info['terminal']}",
        f"CPU: {info['cpu']}",
        f"Memory: {info['memory']}",
    ]
    
    # Calculate how many color blocks we need
    color_count = max(len(ascii_lines), len(info_lines))
    
    # Generate color distribution
    color_indices = []
    for i in range(color_count):
        idx = int(i * len(COLORS) / color_count)
        color_indices.append(idx)
    
    # Print the fetch display
    print()  # Empty line for better spacing
    
    for i in range(max(len(ascii_lines), len(info_lines))):
        if i < len(ascii_lines):
            ascii_line = ascii_lines[i]
        else:
            ascii_line = ""
            
        if i < len(info_lines):
            info_line = info_lines[i]
        else:
            info_line = ""
            
        color = COLORS[color_indices[i % len(COLORS)]]
        print(f"{color}{ascii_line}{' ' * (40 - len(ascii_line))}{info_line}{RESET}")
    
    print()  # Empty line for better spacing

if __name__ == "__main__":
    display_fetch()
