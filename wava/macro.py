#!/usr/bin/env python3
"""
Macro - A simple terminal-based text editor inspired by GNU nano
"""

import curses
import os
import sys
import re
import signal
import tempfile
import subprocess
from pathlib import Path

class MacroEditor:
    def __init__(self, stdscr, filename=None):
        self.stdscr = stdscr
        self.filename = filename
        self.lines = [''] if filename is None else self.read_file(filename)
        self.y, self.x = 0, 0
        self.top_line = 0
        self.status_message = ""
        self.saved = True
        self.running = True
        self.search_query = ""
        self.clipboard = []
        self.configure_curses()
        self.help_visible = False
        self.marked_line_start = None
        self.marked_column_start = None

    def configure_curses(self):
        curses.curs_set(1)  # Show cursor
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Status bar
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Help bar
        curses.init_pair(3, curses.COLOR_GREEN, -1)                  # Line numbers
        curses.init_pair(4, curses.COLOR_YELLOW, -1)                 # Search highlights
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Selected text
        self.stdscr.timeout(100)  # For handling resize events

    def read_file(self, filename):
        try:
            with open(filename, 'r') as f:
                return f.read().splitlines()
        except FileNotFoundError:
            self.status_message = f"New file: {filename}"
            return ['']
        except Exception as e:
            self.status_message = f"Error opening {filename}: {str(e)}"
            return ['']

    def save_file(self):
        if not self.filename:
            self.get_user_input("Save as: ", self.save_as_callback)
            return
        
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines))
            self.saved = True
            self.status_message = f"Saved {self.filename}"
        except Exception as e:
            self.status_message = f"Error saving {self.filename}: {str(e)}"

    def save_as_callback(self, name):
        if name:
            self.filename = name
            self.save_file()

    def display_help(self):
        self.help_visible = not self.help_visible
        if self.help_visible:
            self.status_message = "Help: Ctrl+X Exit | Ctrl+O Save | Ctrl+G Cancel/Close"
        else:
            self.status_message = ""

    def handle_resize(self):
        y, x = self.stdscr.getmaxyx()
        curses.resize_term(y, x)
        self.stdscr.clear()
        self.stdscr.refresh()

    def get_user_input(self, prompt, callback):
        max_y, max_x = self.stdscr.getmaxyx()
        self.stdscr.addstr(max_y - 1, 0, prompt, curses.color_pair(1))
        self.stdscr.clrtoeol()
        user_input = ""
        cursor_pos = len(prompt)
        
        while True:
            self.stdscr.move(max_y - 1, cursor_pos)
            key = self.stdscr.getch()
            
            if key == ord('\n'):  # Enter
                callback(user_input)
                break
            elif key == 7 or key == 27:  # Ctrl+G or ESC
                callback(None)
                break
            elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
                if user_input:
                    user_input = user_input[:-1]
                    cursor_pos -= 1
                    self.stdscr.addstr(max_y - 1, 0, prompt + user_input + " ")
                    self.stdscr.clrtoeol()
            elif 32 <= key <= 126:  # Printable characters
                user_input += chr(key)
                self.stdscr.addch(max_y - 1, cursor_pos, key)
                cursor_pos += 1
        
        self.render()

    def search_text(self):
        self.get_user_input("Search: ", self.search_callback)
    
    def search_callback(self, query):
        if query is None or query == "":
            return
        
        self.search_query = query
        self.search_forward()
    
    def search_forward(self):
        current_line = self.y
        current_pos = self.x
        
        # First, check the current line from current position
        if current_pos < len(self.lines[current_line]):
            index = self.lines[current_line][current_pos:].find(self.search_query)
            if index != -1:
                self.x = current_pos + index
                self.ensure_cursor_visible()
                self.status_message = f"Found '{self.search_query}'"
                return
        
        # Search remaining lines
        for i in range(current_line + 1, len(self.lines)):
            index = self.lines[i].find(self.search_query)
            if index != -1:
                self.y = i
                self.x = index
                self.ensure_cursor_visible()
                self.status_message = f"Found '{self.search_query}'"
                return
        
        # Search from the beginning if not found
        for i in range(0, current_line + 1):
            start_pos = 0 if i != current_line else current_pos + 1
            if start_pos < len(self.lines[i]):
                index = self.lines[i][start_pos:].find(self.search_query)
                if index != -1:
                    self.y = i
                    self.x = start_pos + index
                    self.ensure_cursor_visible()
                    self.status_message = f"Found '{self.search_query}'"
                    return
        
        self.status_message = f"String not found: {self.search_query}"

    def get_visible_lines_range(self):
        max_y, max_x = self.stdscr.getmaxyx()
        return self.top_line, min(self.top_line + max_y - 3, len(self.lines))

    def ensure_cursor_visible(self):
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Ensure cursor is within file bounds
        if self.y >= len(self.lines):
            self.y = len(self.lines) - 1
        if self.y < 0:
            self.y = 0
        if self.x > len(self.lines[self.y]):
            self.x = len(self.lines[self.y])
        if self.x < 0:
            self.x = 0
            
        # Adjust view to keep cursor visible
        if self.y < self.top_line:
            self.top_line = self.y
        elif self.y >= self.top_line + max_y - 3:
            self.top_line = self.y - (max_y - 4)

    def render(self):
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()
        start_line, end_line = self.get_visible_lines_range()
        
        # Draw editor content
        for i, line_idx in enumerate(range(start_line, end_line)):
            line = self.lines[line_idx]
            # Truncate line if it's longer than the screen width
            if len(line) > max_x - 1:
                displayed_line = line[:max_x - 1]
            else:
                displayed_line = line
            
            # Highlight search matches
            if self.search_query and self.search_query in line:
                pos = 0
                while pos < len(displayed_line):
                    match_pos = displayed_line[pos:].find(self.search_query)
                    if match_pos == -1:
                        break
                    
                    match_pos += pos
                    for j in range(len(self.search_query)):
                        if match_pos + j < max_x - 1:
                            self.stdscr.addch(i, match_pos + j, 
                                             displayed_line[match_pos + j], 
                                             curses.color_pair(4))
                    pos = match_pos + len(self.search_query)
            else:
                self.stdscr.addstr(i, 0, displayed_line)
        
        # Draw title bar
        title = f" Macro - {self.filename or 'New Buffer'} {'*' if not self.saved else ''}"
        title = title[:max_x - 1]
        self.stdscr.addstr(max_y - 2, 0, title, curses.color_pair(1))
        self.stdscr.addstr(max_y - 2, len(title), " " * (max_x - len(title) - 1), curses.color_pair(1))
        
        # Draw status line
        status_text = self.status_message
        line_info = f"Line: {self.y + 1}/{len(self.lines)} Col: {self.x + 1}"
        
        if len(status_text) + len(line_info) >= max_x:
            status_text = status_text[:max_x - len(line_info) - 4] + "... "
        
        self.stdscr.addstr(max_y - 1, 0, status_text, curses.color_pair(1))
        remaining_space = max_x - len(status_text) - len(line_info)
        self.stdscr.addstr(max_y - 1, len(status_text), " " * remaining_space, curses.color_pair(1))
        self.stdscr.addstr(max_y - 1, max_x - len(line_info), line_info, curses.color_pair(1))
        
        # Draw shortcuts bar if help is visible
        if self.help_visible:
            help_text = "^X Exit | ^O Save | ^W Search | ^K Cut | ^U Paste | ^G Cancel"
            if len(help_text) > max_x:
                help_text = help_text[:max_x]
            self.stdscr.addstr(max_y - 3, 0, help_text, curses.color_pair(2))
            self.stdscr.addstr(max_y - 3, len(help_text), " " * (max_x - len(help_text)), curses.color_pair(2))
        
        # Position cursor
        cursor_y = self.y - self.top_line
        cursor_x = min(self.x, max_x - 1)
        self.stdscr.move(cursor_y, cursor_x)

    def handle_input(self):
        key = self.stdscr.getch()
        
        if key == curses.KEY_RESIZE:
            self.handle_resize()
            return

        if key == 24:  # Ctrl+X (Exit)
            if not self.saved:
                self.status_message = "Save modified buffer? (y/n)"
                confirm = self.stdscr.getch()
                if confirm == ord('y') or confirm == ord('Y'):
                    self.save_file()
            self.running = False
            
        elif key == 15:  # Ctrl+O (Save)
            self.save_file()
            
        elif key == 7:  # Ctrl+G (Cancel/Help)
            self.display_help()
            
        elif key == 23:  # Ctrl+W (Search)
            self.search_text()
            
        elif key == 11:  # Ctrl+K (Cut line)
            if self.lines:
                self.clipboard = [self.lines[self.y]]
                if len(self.lines) > 1:
                    self.lines.pop(self.y)
                    if self.y == len(self.lines):
                        self.y -= 1
                else:
                    self.lines[0] = ''
                self.x = 0
                self.saved = False
                self.status_message = "Line cut"
            
        elif key == 21:  # Ctrl+U (Paste)
            if self.clipboard:
                for line in reversed(self.clipboard):
                    self.lines.insert(self.y, line)
                self.saved = False
                self.status_message = "Text pasted"
            
        elif key == curses.KEY_UP:
            if self.y > 0:
                self.y -= 1
                self.x = min(self.x, len(self.lines[self.y]))
                
        elif key == curses.KEY_DOWN:
            if self.y < len(self.lines) - 1:
                self.y += 1
                self.x = min(self.x, len(self.lines[self.y]))
                
        elif key == curses.KEY_LEFT:
            if self.x > 0:
                self.x -= 1
            elif self.y > 0:
                self.y -= 1
                self.x = len(self.lines[self.y])
                
        elif key == curses.KEY_RIGHT:
            if self.x < len(self.lines[self.y]):
                self.x += 1
            elif self.y < len(self.lines) - 1:
                self.y += 1
                self.x = 0
                
        elif key == curses.KEY_HOME or key == 1:  # Home or Ctrl+A
            self.x = 0
            
        elif key == curses.KEY_END or key == 5:  # End or Ctrl+E
            self.x = len(self.lines[self.y])
            
        elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
            if self.x > 0:
                # Delete character at cursor
                self.lines[self.y] = self.lines[self.y][:self.x-1] + self.lines[self.y][self.x:]
                self.x -= 1
                self.saved = False
            elif self.y > 0:
                # Join with previous line
                cursor_pos = len(self.lines[self.y-1])
                self.lines[self.y-1] += self.lines[self.y]
                self.lines.pop(self.y)
                self.y -= 1
                self.x = cursor_pos
                self.saved = False
                
        elif key == 10 or key == 13:  # Enter
            # Split line at cursor
            new_line = self.lines[self.y][self.x:]
            self.lines[self.y] = self.lines[self.y][:self.x]
            self.lines.insert(self.y + 1, new_line)
            self.y += 1
            self.x = 0
            self.saved = False
            
        elif key == 9:  # Tab
            # Insert spaces for tab
            tab_width = 4
            self.lines[self.y] = self.lines[self.y][:self.x] + ' ' * tab_width + self.lines[self.y][self.x:]
            self.x += tab_width
            self.saved = False
            
        elif 32 <= key <= 126:  # Printable characters
            # Insert character at cursor
            self.lines[self.y] = self.lines[self.y][:self.x] + chr(key) + self.lines[self.y][self.x:]
            self.x += 1
            self.saved = False

        self.ensure_cursor_visible()

    def run(self):
        try:
            while self.running:
                self.render()
                self.handle_input()
        except KeyboardInterrupt:
            pass

def main(stdscr):
    # Handle command line args
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Initialize editor
    editor = MacroEditor(stdscr, filename)
    editor.run()

if __name__ == "__main__":
    # Set up signal handler for terminal resize
    signal.signal(signal.SIGWINCH, lambda sig, frame: None)
    
    # Start the curses application
    curses.wrapper(main)
