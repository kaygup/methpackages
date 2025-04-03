#!/usr/bin/env python3
"""
Terminal File Explorer with Package Manager Integration for Linux
"""

import os
import sys
import curses
import subprocess
import shutil
from datetime import datetime

class FileExplorer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_path = os.path.expanduser("~")
        self.cursor_pos = 0
        self.offset = 0
        self.max_items = curses.LINES - 7  # Reserve space for header and footer
        self.items = []
        self.clipboard = None
        self.clipboard_op = None  # 'copy' or 'cut'
        self.search_string = ""
        self.search_mode = False
        self.package_manager = self.detect_package_manager()
        self.setup_colors()
        self.load_items()
        
    def setup_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLUE, -1)  # Directories
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Executable files
        curses.init_pair(3, curses.COLOR_MAGENTA, -1)  # Symlinks
        curses.init_pair(4, curses.COLOR_RED, -1)  # Error messages
        curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Highlighted items
        curses.init_pair(6, curses.COLOR_CYAN, -1)  # Headers
        
    def detect_package_manager(self):
        # Check for common package managers
        package_managers = [
            ("apt", "apt list --installed", "apt show", "apt install", "apt remove"),
            ("dnf", "dnf list installed", "dnf info", "dnf install", "dnf remove"),
            ("pacman", "pacman -Q", "pacman -Qi", "pacman -S", "pacman -R"),
            ("zypper", "zypper search --installed-only", "zypper info", "zypper install", "zypper remove"),
            ("emerge", "emerge -ep world", "emerge -pv", "emerge", "emerge --unmerge")
        ]
        
        for pm, list_cmd, info_cmd, install_cmd, remove_cmd in package_managers:
            if shutil.which(pm):
                return {
                    "name": pm,
                    "list_cmd": list_cmd,
                    "info_cmd": info_cmd,
                    "install_cmd": install_cmd, 
                    "remove_cmd": remove_cmd
                }
        
        # Default to apt if nothing is found
        return {
            "name": "apt",
            "list_cmd": "apt list --installed",
            "info_cmd": "apt show",
            "install_cmd": "apt install",
            "remove_cmd": "apt remove"
        }
    
    def load_items(self):
        self.items = [".."]
        try:
            items = os.listdir(self.current_path)
            # Show directories first, then files
            dirs = sorted([item for item in items if os.path.isdir(os.path.join(self.current_path, item))])
            files = sorted([item for item in items if not os.path.isdir(os.path.join(self.current_path, item))])
            self.items.extend(dirs + files)
        except PermissionError:
            self.show_error("Permission denied: Cannot access this directory")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
            
        # Filter items if search is active
        if self.search_string:
            self.items = [".."] + [item for item in self.items[1:] if self.search_string.lower() in item.lower()]
        
        # Reset cursor position
        if self.cursor_pos >= len(self.items):
            self.cursor_pos = 0 if len(self.items) > 0 else 0
            self.offset = 0
    
    def draw(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxlines(), self.stdscr.getmaxyx()[1]
        
        # Draw title bar
        title = f" File Explorer - {self.package_manager['name'].upper()} Package Manager "
        self.stdscr.addstr(0, (w - len(title)) // 2, title, curses.color_pair(6) | curses.A_BOLD)
        
        # Draw current path
        path_display = self.current_path
        if len(path_display) > w - 2:
            path_display = "..." + path_display[-(w-5):]
        self.stdscr.addstr(1, 0, path_display, curses.A_BOLD)
        
        # Draw separator
        self.stdscr.addstr(2, 0, "─" * w)
        
        # Draw items
        for i in range(min(self.max_items, len(self.items))):
            idx = i + self.offset
            if idx >= len(self.items):
                break
                
            item = self.items[idx]
            full_path = os.path.join(self.current_path, item) if item != ".." else os.path.dirname(self.current_path)
            
            # Determine item type and color
            attr = curses.A_NORMAL
            if idx == self.cursor_pos:
                attr |= curses.A_REVERSE
                
            if item == "..":
                attr |= curses.color_pair(1)  # Blue for parent directory
                display_name = "[Parent Directory]"
            elif os.path.isdir(full_path):
                attr |= curses.color_pair(1)  # Blue for directories
                display_name = f"[{item}]"
            elif os.path.islink(full_path):
                attr |= curses.color_pair(3)  # Magenta for symlinks
                display_name = f"{item} -> {os.readlink(full_path)}"
            elif os.access(full_path, os.X_OK):
                attr |= curses.color_pair(2)  # Green for executables
                display_name = item
            else:
                display_name = item
                
            # Format file size and date
            if item != ".." and os.path.exists(full_path):
                try:
                    stats = os.stat(full_path)
                    size = self.format_size(stats.st_size)
                    date = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                    info = f"{size:>8} {date}"
                    
                    # Truncate name if needed
                    max_name_len = w - len(info) - 3
                    if len(display_name) > max_name_len:
                        display_name = display_name[:max_name_len-3] + "..."
                        
                    self.stdscr.addstr(i+3, 0, f" {display_name}", attr)
                    self.stdscr.addstr(i+3, w - len(info) - 1, info)
                except:
                    self.stdscr.addstr(i+3, 0, f" {display_name}", attr)
            else:
                self.stdscr.addstr(i+3, 0, f" {display_name}", attr)
                
        # Draw status bar
        self.stdscr.addstr(h-3, 0, "─" * w)
        
        # Draw search box if in search mode
        if self.search_mode:
            self.stdscr.addstr(h-2, 0, f"Search: {self.search_string}")
        else:
            # Draw commands help
            commands = "F1:Help | F2:Rename | F3:View | F4:Edit | F5:Copy | F6:Move | F7:Mkdir | F8:Delete | F10:Quit"
            if len(commands) > w:
                commands = commands[:w-3] + "..."
            self.stdscr.addstr(h-2, 0, commands)
            
        # Draw package manager info
        pm_info = f"Package Manager: {self.package_manager['name'].upper()} | P:Search Packages | I:Install | R:Remove"
        if len(pm_info) > w:
            pm_info = pm_info[:w-3] + "..."
        self.stdscr.addstr(h-1, 0, pm_info)
        
        self.stdscr.refresh()
    
    def format_size(self, size):
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024:
                if unit == 'B':
                    return f"{size}{unit}"
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}P"
    
    def move_cursor(self, direction):
        if direction == "up":
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                if self.cursor_pos < self.offset:
                    self.offset = self.cursor_pos
        elif direction == "down":
            if self.cursor_pos < len(self.items) - 1:
                self.cursor_pos += 1
                if self.cursor_pos >= self.offset + self.max_items:
                    self.offset = self.cursor_pos - self.max_items + 1
        elif direction == "home":
            self.cursor_pos = 0
            self.offset = 0
        elif direction == "end":
            self.cursor_pos = len(self.items) - 1
            if len(self.items) > self.max_items:
                self.offset = len(self.items) - self.max_items
            else:
                self.offset = 0
        elif direction == "page_up":
            self.cursor_pos -= self.max_items
            if self.cursor_pos < 0:
                self.cursor_pos = 0
            self.offset -= self.max_items
            if self.offset < 0:
                self.offset = 0
        elif direction == "page_down":
            self.cursor_pos += self.max_items
            if self.cursor_pos >= len(self.items):
                self.cursor_pos = len(self.items) - 1
            if self.cursor_pos >= self.offset + self.max_items:
                self.offset = self.cursor_pos - self.max_items + 1
                if self.offset + self.max_items > len(self.items):
                    self.offset = max(0, len(self.items) - self.max_items)
    
    def enter_directory(self):
        if not self.items:
            return
            
        selected = self.items[self.cursor_pos]
        if selected == "..":
            self.current_path = os.path.dirname(self.current_path)
        else:
            full_path = os.path.join(self.current_path, selected)
            if os.path.isdir(full_path):
                self.current_path = full_path
            elif os.path.isfile(full_path):
                self.view_file(full_path)
                
        self.cursor_pos = 0
        self.offset = 0
        self.load_items()
    
    def view_file(self, filepath):
        # Save terminal state
        curses.endwin()
        
        # Use appropriate viewer based on file type
        if self.is_text_file(filepath):
            less_path = shutil.which('less') or shutil.which('more') or 'cat'
            os.system(f"{less_path} '{filepath}'")
        else:
            print(f"Binary file: {filepath}")
            input("Press Enter to continue...")
            
        # Restore terminal state
        curses.initscr()
        curses.curs_set(0)
        
    def is_text_file(self, filepath):
        """Check if file is a text file"""
        try:
            with open(filepath, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' not in chunk
        except:
            return False
    
    def edit_file(self):
        if not self.items:
            return
            
        selected = self.items[self.cursor_pos]
        if selected != "..":
            full_path = os.path.join(self.current_path, selected)
            if os.path.isfile(full_path):
                # Find an editor
                editor = os.environ.get('EDITOR', 'nano')
                if not shutil.which(editor):
                    editor = shutil.which('nano') or shutil.which('vim') or shutil.which('vi')
                
                if editor:
                    curses.endwin()
                    os.system(f"{editor} '{full_path}'")
                    curses.initscr()
                    curses.curs_set(0)
                else:
                    self.show_error("No text editor found")
    
    def show_error(self, message):
        h, w = self.stdscr.getmaxlines(), self.stdscr.getmaxyx()[1]
        self.stdscr.addstr(h-4, 0, " " * w)
        self.stdscr.addstr(h-4, 0, message, curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.refresh()
        self.stdscr.getch()  # Wait for key press
    
    def show_help(self):
        help_text = [
            "File Explorer Commands:",
            "",
            "Navigation:",
            "  Arrow keys    - Move cursor",
            "  Enter         - Open directory/file",
            "  Backspace     - Go to parent directory",
            "  Home/End      - Jump to first/last item",
            "  PgUp/PgDown   - Scroll page up/down",
            "",
            "File Operations:",
            "  F2            - Rename file/directory",
            "  F3            - View file content",
            "  F4            - Edit file",
            "  F5            - Copy file/directory",
            "  F6            - Move file/directory",
            "  F7            - Create directory",
            "  F8/Del        - Delete file/directory",
            "  /             - Search in current directory",
            "",
            "Package Manager:",
            "  P             - Search installed packages",
            "  I             - Install new package",
            "  R             - Remove package",
            "",
            "Other:",
            "  F10/Q         - Quit",
            "",
            "Press any key to continue..."
        ]
        
        curses.endwin()
        for line in help_text:
            print(line)
        input()  # Wait for a keypress
        curses.initscr()
        curses.curs_set(0)
    
    def create_directory(self):
        curses.echo()
        curses.curs_set(1)
        h = self.stdscr.getmaxlines()
        self.stdscr.addstr(h-4, 0, "Enter directory name: ")
        self.stdscr.clrtoeol()
        
        dirname = self.stdscr.getstr().decode('utf-8')
        if dirname:
            try:
                os.mkdir(os.path.join(self.current_path, dirname))
                self.load_items()
            except Exception as e:
                self.show_error(f"Could not create directory: {str(e)}")
                
        curses.noecho()
        curses.curs_set(0)
    
    def delete_item(self):
        if not self.items or self.cursor_pos == 0:  # Don't allow deleting ".."
            return
            
        selected = self.items[self.cursor_pos]
        full_path = os.path.join(self.current_path, selected)
        
        h = self.stdscr.getmaxlines()
        self.stdscr.addstr(h-4, 0, f"Delete {selected}? (y/n): ")
        self.stdscr.clrtoeol()
        
        c = self.stdscr.getch()
        if c == ord('y') or c == ord('Y'):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.unlink(full_path)
                self.load_items()
            except Exception as e:
                self.show_error(f"Could not delete: {str(e)}")
    
    def rename_item(self):
        if not self.items or self.cursor_pos == 0:  # Don't allow renaming ".."
            return
            
        selected = self.items[self.cursor_pos]
        full_path = os.path.join(self.current_path, selected)
        
        curses.echo()
        curses.curs_set(1)
        h = self.stdscr.getmaxlines()
        self.stdscr.addstr(h-4, 0, f"Rename {selected} to: ")
        self.stdscr.clrtoeol()
        
        new_name = self.stdscr.getstr().decode('utf-8')
        if new_name:
            try:
                new_path = os.path.join(self.current_path, new_name)
                os.rename(full_path, new_path)
                self.load_items()
            except Exception as e:
                self.show_error(f"Could not rename: {str(e)}")
                
        curses.noecho()
        curses.curs_set(0)
    
    def copy_item(self):
        if not self.items or self.cursor_pos == 0:  # Don't allow copying ".."
            return
            
        selected = self.items[self.cursor_pos]
        self.clipboard = os.path.join(self.current_path, selected)
        self.clipboard_op = 'copy'
        
        h = self.stdscr.getmaxlines()
        self.stdscr.addstr(h-4, 0, f"Copied {selected} to clipboard")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
    
    def move_item(self):
        if not self.items or self.cursor_pos == 0:  # Don't allow moving ".."
            return
            
        selected = self.items[self.cursor_pos]
        self.clipboard = os.path.join(self.current_path, selected)
        self.clipboard_op = 'cut'
        
        h = self.stdscr.getmaxlines()
        self.stdscr.addstr(h-4, 0, f"Cut {selected} to clipboard")
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
    
    def paste_item(self):
        if not self.clipboard:
            return
            
        dest_dir = self.current_path
        basename = os.path.basename(self.clipboard)
        destination = os.path.join(dest_dir, basename)
        
        # Check if destination already exists
        if os.path.exists(destination):
            h = self.stdscr.getmaxlines()
            self.stdscr.addstr(h-4, 0, f"{basename} already exists. Overwrite? (y/n): ")
            self.stdscr.clrtoeol()
            
            c = self.stdscr.getch()
            if c != ord('y') and c != ord('Y'):
                return
        
        try:
            if self.clipboard_op == 'copy':
                if os.path.isdir(self.clipboard):
                    shutil.copytree(self.clipboard, destination)
                else:
                    shutil.copy2(self.clipboard, destination)
            elif self.clipboard_op == 'cut':
                shutil.move(self.clipboard, destination)
                self.clipboard = None
            
            self.load_items()
        except Exception as e:
            self.show_error(f"Could not paste: {str(e)}")
    
    def search_files(self):
        self.search_mode = True
        self.search_string = ""
        h = self.stdscr.getmaxlines()
        
        curses.echo()
        curses.curs_set(1)
        
        while True:
            self.stdscr.addstr(h-2, 0, f"Search: {self.search_string}")
            self.stdscr.clrtoeol()
            self.stdscr.move(h-2, 8 + len(self.search_string))
            
            c = self.stdscr.getch()
            
            if c == 27:  # Escape
                self.search_mode = False
                self.search_string = ""
                break
            elif c == 10 or c == 13:  # Enter
                self.search_mode = False
                break
            elif c == 8 or c == 127:  # Backspace
                if self.search_string:
                    self.search_string = self.search_string[:-1]
                    self.load_items()
            elif c >= 32 and c < 127:  # Printable characters
                self.search_string += chr(c)
                self.load_items()
        
        curses.noecho()
        curses.curs_set(0)
    
    def package_search(self):
        curses.endwin()
        print(f"Searching installed packages with {self.package_manager['name']}...")
        os.system(self.package_manager['list_cmd'])
        input("\nPress Enter to continue...")
        curses.initscr()
        curses.curs_set(0)
    
    def package_install(self):
        curses.echo()
        curses.curs_set(1)
        h = self.stdscr.getmaxlines()
        self.stdscr.addstr(h-4, 0, "Enter package name to install: ")
        self.stdscr.clrtoeol()
        
        package = self.stdscr.getstr().decode('utf-8')
        
        if package:
            curses.endwin()
            print(f"Installing {package} using {self.package_manager['name']}...")
            os.system(f"sudo {self.package_manager['install_cmd']} {package}")
            input("\nPress Enter to continue...")
            curses.initscr()
            curses.curs_set(0)
            
        curses.noecho()
        curses.curs_set(0)
    
    def package_remove(self):
        curses.echo()
        curses.curs_set(1)
        h = self.stdscr.getmaxlines()
        self.stdscr.addstr(h-4, 0, "Enter package name to remove: ")
        self.stdscr.clrtoeol()
        
        package = self.stdscr.getstr().decode('utf-8')
        
        if package:
            curses.endwin()
            print(f"Removing {package} using {self.package_manager['name']}...")
            os.system(f"sudo {self.package_manager['remove_cmd']} {package}")
            input("\nPress Enter to continue...")
            curses.initscr()
            curses.curs_set(0)
            
        curses.noecho()
        curses.curs_set(0)
    
    def run(self):
        curses.curs_set(0)  # Hide cursor
        
        while True:
            self.draw()
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP:
                self.move_cursor("up")
            elif key == curses.KEY_DOWN:
                self.move_cursor("down")
            elif key == curses.KEY_LEFT or key == 8 or key == 127:  # Left arrow or Backspace
                self.current_path = os.path.dirname(self.current_path)
                self.cursor_pos = 0
                self.offset = 0
                self.load_items()
            elif key == curses.KEY_RIGHT or key == 10 or key == 13:  # Right arrow or Enter
                self.enter_directory()
            elif key == curses.KEY_HOME:
                self.move_cursor("home")
            elif key == curses.KEY_END:
                self.move_cursor("end")
            elif key == curses.KEY_PPAGE:  # Page Up
                self.move_cursor("page_up")
            elif key == curses.KEY_NPAGE:  # Page Down
                self.move_cursor("page_down")
            elif key == curses.KEY_F1:  # F1 - Help
                self.show_help()
            elif key == curses.KEY_F2:  # F2 - Rename
                self.rename_item()
            elif key == curses.KEY_F3:  # F3 - View
                if self.items and self.cursor_pos > 0:
                    full_path = os.path.join(self.current_path, self.items[self.cursor_pos])
                    if os.path.isfile(full_path):
                        self.view_file(full_path)
            elif key == curses.KEY_F4:  # F4 - Edit
                self.edit_file()
            elif key == curses.KEY_F5:  # F5 - Copy
                self.copy_item()
            elif key == curses.KEY_F6:  # F6 - Move/Cut
                self.move_item()
            elif key == curses.KEY_F7:  # F7 - Create Directory
                self.create_directory()
            elif key == curses.KEY_F8 or key == curses.KEY_DC:  # F8 or Delete - Delete
                self.delete_item()
            elif key == curses.KEY_F10 or key == ord('q') or key == ord('Q'):  # F10 or Q - Quit
                break
            elif key == ord('p') or key == ord('P'):  # P - Package search
                self.package_search()
            elif key == ord('i') or key == ord('I'):  # I - Package install
                self.package_install()
            elif key == ord('r') or key == ord('R'):  # R - Package remove
                self.package_remove()
            elif key == ord('v'):  # V - Paste
                self.paste_item()
            elif key == ord('/'):  # / - Search
                self.search_files()

def main(stdscr):
    # Setup terminal
    curses.curs_set(0)  # Hide cursor
    explorer = FileExplorer(stdscr)
    explorer.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
