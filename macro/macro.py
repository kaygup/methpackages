#!/usr/bin/env python3
"""
PyTermEdit - A simple terminal-based Python code editor
"""

import curses
import os
import sys
import re
from pathlib import Path

class TextBuffer:
    def __init__(self, filename=None):
        self.lines = [""]
        self.filename = filename
        self.modified = False
        self.syntax_highlighting = True
        
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                self.lines = [line.rstrip('\n') for line in f.readlines()]
            
            # Ensure there's at least one line
            if not self.lines:
                self.lines = [""]
                
            self.filename = filename
            self.modified = False
            return True
        except Exception as e:
            return False
    
    def save_file(self, filename=None):
        if filename:
            self.filename = filename
        
        if not self.filename:
            return False
        
        try:
            with open(self.filename, 'w') as f:
                for line in self.lines:
                    f.write(line + '\n')
            self.modified = False
            return True
        except Exception as e:
            return False
    
    def insert_char(self, y, x, char):
        # Expand lines if needed
        while y >= len(self.lines):
            self.lines.append("")
        
        line = self.lines[y]
        # Expand line if needed
        if x > len(line):
            line += " " * (x - len(line))
            
        self.lines[y] = line[:x] + char + line[x:]
        self.modified = True
    
    def insert_line(self, y):
        current_line = self.lines[y]
        cursor_x = self.cursor_x
        
        # Split the line at cursor position
        self.lines[y] = current_line[:cursor_x]
        self.lines.insert(y + 1, current_line[cursor_x:])
        self.modified = True
        
    def delete_char(self, y, x):
        if y < len(self.lines):
            line = self.lines[y]
            if x < len(line):
                self.lines[y] = line[:x] + line[x+1:]
                self.modified = True
            elif x == len(line) and y < len(self.lines) - 1:
                # Join with next line if at end of line
                self.lines[y] += self.lines[y+1]
                self.lines.pop(y+1)
                self.modified = True
    
    def backspace(self, y, x):
        if x > 0:
            line = self.lines[y]
            self.lines[y] = line[:x-1] + line[x:]
            self.modified = True
            return (y, x-1)
        elif y > 0:
            # Move to end of previous line
            prev_line = self.lines[y-1]
            prev_line_length = len(prev_line)
            self.lines[y-1] += self.lines[y]
            self.lines.pop(y)
            self.modified = True
            return (y-1, prev_line_length)
        return (y, x)

class PythonSyntaxHighlighter:
    def __init__(self):
        # Define color pairs for syntax highlighting
        self.COLOR_DEFAULT = 0
        self.COLOR_KEYWORD = 1
        self.COLOR_STRING = 2
        self.COLOR_COMMENT = 3
        self.COLOR_FUNCTION = 4
        self.COLOR_NUMBER = 5
        
        # Python keywords
        self.keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue", 
            "def", "del", "elif", "else", "except", "False", "finally", "for", 
            "from", "global", "if", "import", "in", "is", "lambda", "None", 
            "nonlocal", "not", "or", "pass", "raise", "return", "True", "try", 
            "while", "with", "yield"
        ]
        
        # Regex patterns
        self.patterns = {
            'keyword': r'\b(' + '|'.join(self.keywords) + r')\b',
            'string': r'(["\'])(?:(?=(\\?))\2.)*?\1',
            'comment': r'#.*$',
            'function': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            'number': r'\b\d+\.?\d*\b'
        }
        
        # Compiled regex patterns
        self.compiled_patterns = {k: re.compile(v) for k, v in self.patterns.items()}
    
    def setup_colors(self, stdscr):
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        
        # Set up color pairs
        curses.init_pair(self.COLOR_DEFAULT, -1, -1)  # Default: terminal default
        curses.init_pair(self.COLOR_KEYWORD, curses.COLOR_BLUE, -1)  # Keywords: blue
        curses.init_pair(self.COLOR_STRING, curses.COLOR_GREEN, -1)  # Strings: green
        curses.init_pair(self.COLOR_COMMENT, curses.COLOR_CYAN, -1)  # Comments: cyan
        curses.init_pair(self.COLOR_FUNCTION, curses.COLOR_MAGENTA, -1)  # Functions: magenta
        curses.init_pair(self.COLOR_NUMBER, curses.COLOR_RED, -1)  # Numbers: red
    
    def highlight_line(self, stdscr, y, x, line, cur_y, selected=False):
        # Start with a clean line
        stdscr.move(y, x)
        stdscr.clrtoeol()
        
        # Add highlighted text segments
        if selected:
            stdscr.attron(curses.A_REVERSE)
        
        # Find all matches and their positions
        matches = []
        for token_type, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(line):
                start, end = match.span()
                color_pair = getattr(self, f"COLOR_{token_type.upper()}")
                matches.append((start, end, color_pair))
        
        # Sort matches by start position
        matches.sort(key=lambda x: x[0])
        
        # Handle overlapping matches by giving precedence to later patterns
        non_overlapping = []
        for match in matches:
            start, end, color = match
            # Check if this match overlaps with any already added
            overlap = False
            for i, (s, e, c) in enumerate(non_overlapping):
                if start < e and end > s:  # Overlap
                    overlap = True
                    # Split the existing match if needed
                    if start > s:
                        non_overlapping[i] = (s, start, c)
                        if end < e:
                            non_overlapping.append((end, e, c))
                    elif end < e:
                        non_overlapping[i] = (end, e, c)
                    else:
                        non_overlapping.pop(i)
                    # Add this match
                    non_overlapping.append(match)
                    break
            if not overlap:
                non_overlapping.append(match)
        
        # Sort again after resolving overlaps
        non_overlapping.sort(key=lambda x: x[0])
        
        # Add default color for parts without matches
        current_pos = 0
        segments = []
        for start, end, color in non_overlapping:
            if start > current_pos:
                segments.append((current_pos, start, self.COLOR_DEFAULT))
            segments.append((start, end, color))
            current_pos = end
        if current_pos < len(line):
            segments.append((current_pos, len(line), self.COLOR_DEFAULT))
        
        # Display the segments
        for start, end, color in sorted(segments, key=lambda x: x[0]):
            segment = line[start:end]
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(segment)
            stdscr.attroff(curses.color_pair(color))
        
        if selected:
            stdscr.attroff(curses.A_REVERSE)


class Editor:
    def __init__(self, stdscr, filename=None):
        self.stdscr = stdscr
        self.text_buffer = TextBuffer(filename)
        self.syntax_highlighter = PythonSyntaxHighlighter()
        
        # Editor state
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.status_message = ""
        self.mode = "NORMAL"  # NORMAL, INSERT, COMMAND
        self.command_buffer = ""
        
        # Set up curses
        curses.curs_set(1)  # Show cursor
        curses.use_default_colors()
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)  # For handling resize events
        
        # Set up syntax highlighting
        self.syntax_highlighter.setup_colors(stdscr)
        
        # Get terminal dimensions
        self.height, self.width = self.stdscr.getmaxyx()

    def run(self):
        while True:
            self.handle_resize()
            self.refresh_screen()
            
            # Get user input
            try:
                ch = self.stdscr.getch()
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                if self.prompt_save_changes():
                    break
                continue
                
            if ch == curses.ERR:
                continue
            
            # Process input based on mode
            if self.mode == "NORMAL":
                if self.handle_normal_mode(ch):
                    break
            elif self.mode == "INSERT":
                if self.handle_insert_mode(ch):
                    break
            elif self.mode == "COMMAND":
                if self.handle_command_mode(ch):
                    break
    
    def handle_resize(self):
        # Check if terminal has been resized
        current_height, current_width = self.stdscr.getmaxyx()
        if current_height != self.height or current_width != self.width:
            self.height, self.width = current_height, current_width
            self.stdscr.clear()
            curses.resizeterm(self.height, self.width)
    
    def refresh_screen(self):
        self.stdscr.clear()
        
        # Calculate visible area
        editor_height = self.height - 2  # Reserve space for status line and command line
        
        # Draw text
        for i in range(editor_height):
            file_line = i + self.scroll_y
            if file_line < len(self.text_buffer.lines):
                line = self.text_buffer.lines[file_line]
                visible_line = line[self.scroll_x:self.scroll_x + self.width]
                
                # Use syntax highlighting if enabled
                if self.text_buffer.syntax_highlighting:
                    self.syntax_highlighter.highlight_line(
                        self.stdscr, i, 0, visible_line, 
                        file_line == self.cursor_y
                    )
                else:
                    self.stdscr.addstr(i, 0, visible_line)
                
                # Draw line numbers (simple version)
                line_num_str = f"{file_line + 1:4d} "
                self.stdscr.addstr(i, 0, line_num_str, curses.A_DIM)
        
        # Draw status line
        status_left = f" {self.mode} | {self.text_buffer.filename or '[No Name]'}"
        status_left += " [+]" if self.text_buffer.modified else ""
        status_right = f"Ln {self.cursor_y + 1}, Col {self.cursor_x + 1} "
        status = status_left + " " * (self.width - len(status_left) - len(status_right) - 1) + status_right
        
        self.stdscr.attron(curses.A_REVERSE)
        self.stdscr.addstr(self.height - 2, 0, status[:self.width])
        self.stdscr.attroff(curses.A_REVERSE)
        
        # Draw command line or message
        if self.mode == "COMMAND":
            self.stdscr.addstr(self.height - 1, 0, ":" + self.command_buffer)
        else:
            self.stdscr.addstr(self.height - 1, 0, self.status_message[:self.width])
        
        # Position cursor
        cursor_screen_y = self.cursor_y - self.scroll_y
        cursor_screen_x = self.cursor_x - self.scroll_x + 5  # +5 for line numbers
        if 0 <= cursor_screen_y < editor_height and 0 <= cursor_screen_x < self.width:
            self.stdscr.move(cursor_screen_y, cursor_screen_x)
        
        self.stdscr.refresh()
    
    def handle_normal_mode(self, ch):
        if ch == ord('i'):
            self.mode = "INSERT"
            self.status_message = "-- INSERT --"
        elif ch == ord(':'):
            self.mode = "COMMAND"
            self.command_buffer = ""
        elif ch == ord('h') or ch == curses.KEY_LEFT:
            self.move_cursor_left()
        elif ch == ord('j') or ch == curses.KEY_DOWN:
            self.move_cursor_down()
        elif ch == ord('k') or ch == curses.KEY_UP:
            self.move_cursor_up()
        elif ch == ord('l') or ch == curses.KEY_RIGHT:
            self.move_cursor_right()
        elif ch == ord('g'):
            # Go to start of file
            self.cursor_y = 0
            self.cursor_x = 0
            self.scroll_y = 0
            self.scroll_x = 0
        elif ch == ord('G'):
            # Go to end of file
            self.cursor_y = len(self.text_buffer.lines) - 1
            self.ensure_cursor_visible()
        elif ch == ord('0'):
            # Go to start of line
            self.cursor_x = 0
            self.scroll_x = 0
        elif ch == ord('$'):
            # Go to end of line
            if self.cursor_y < len(self.text_buffer.lines):
                self.cursor_x = len(self.text_buffer.lines[self.cursor_y])
                self.ensure_cursor_visible()
        
        return False  # Continue editing
    
    def handle_insert_mode(self, ch):
        if ch == 27:  # ESC
            self.mode = "NORMAL"
            self.status_message = ""
            # Adjust cursor position when leaving insert mode
            if self.cursor_y < len(self.text_buffer.lines) and self.cursor_x > 0:
                line_length = len(self.text_buffer.lines[self.cursor_y])
                if line_length > 0 and self.cursor_x == line_length:
                    self.cursor_x -= 1
        elif ch == curses.KEY_LEFT:
            self.move_cursor_left()
        elif ch == curses.KEY_DOWN:
            self.move_cursor_down()
        elif ch == curses.KEY_UP:
            self.move_cursor_up()
        elif ch == curses.KEY_RIGHT:
            self.move_cursor_right()
        elif ch == curses.KEY_BACKSPACE or ch == 127:
            self.handle_backspace()
        elif ch == curses.KEY_DC:  # Delete key
            self.text_buffer.delete_char(self.cursor_y, self.cursor_x)
        elif ch == ord('\n'):
            # Handle enter key: split line at cursor
            if self.cursor_y < len(self.text_buffer.lines):
                line = self.text_buffer.lines[self.cursor_y]
                self.text_buffer.lines[self.cursor_y] = line[:self.cursor_x]
                self.text_buffer.lines.insert(self.cursor_y + 1, line[self.cursor_x:])
                self.text_buffer.modified = True
                self.cursor_y += 1
                self.cursor_x = 0
                self.ensure_cursor_visible()
        elif ch == ord('\t'):
            # Insert 4 spaces for tab
            for _ in range(4):
                self.text_buffer.insert_char(self.cursor_y, self.cursor_x, ' ')
                self.cursor_x += 1
            self.ensure_cursor_visible()
        elif 32 <= ch <= 126:  # Printable ASCII
            self.text_buffer.insert_char(self.cursor_y, self.cursor_x, chr(ch))
            self.cursor_x += 1
            self.ensure_cursor_visible()
        
        return False  # Continue editing
    
    def handle_command_mode(self, ch):
        if ch == 27:  # ESC
            self.mode = "NORMAL"
            self.status_message = ""
        elif ch == curses.KEY_BACKSPACE or ch == 127:
            if self.command_buffer:
                self.command_buffer = self.command_buffer[:-1]
        elif ch == ord('\n'):
            # Execute command
            result = self.execute_command(self.command_buffer)
            self.mode = "NORMAL"
            if result == "EXIT":
                return True  # Exit editor
        elif 32 <= ch <= 126:  # Printable ASCII
            self.command_buffer += chr(ch)
        
        return False  # Continue editing
    
    def execute_command(self, command):
        command = command.strip()
        
        if command == "q":
            if self.text_buffer.modified:
                self.status_message = "No write since last change (add ! to override)"
                return
            return "EXIT"
        elif command == "q!":
            return "EXIT"
        elif command.startswith("w"):
            # Write file
            filename = None
            if len(command) > 1:
                parts = command.split(None, 1)
                if len(parts) > 1:
                    filename = parts[1]
            
            success = self.text_buffer.save_file(filename)
            if success:
                self.status_message = f"Wrote {self.text_buffer.filename}"
            else:
                self.status_message = "Error writing file"
        elif command == "wq" or command == "x":
            # Write and quit
            success = self.text_buffer.save_file()
            if success:
                return "EXIT"
            else:
                self.status_message = "Error writing file"
        elif command.startswith("e "):
            # Edit file
            filename = command[2:].strip()
            if self.text_buffer.modified:
                self.status_message = "No write since last change (add ! to override)"
            else:
                success = self.text_buffer.load_file(filename)
                if success:
                    self.cursor_y = 0
                    self.cursor_x = 0
                    self.scroll_y = 0
                    self.scroll_x = 0
                    self.status_message = f"Loaded {filename}"
                else:
                    self.status_message = f"Error loading {filename}"
        elif command.startswith("e! "):
            # Force edit file
            filename = command[3:].strip()
            success = self.text_buffer.load_file(filename)
            if success:
                self.cursor_y = 0
                self.cursor_x = 0
                self.scroll_y = 0
                self.scroll_x = 0
                self.status_message = f"Loaded {filename}"
            else:
                self.status_message = f"Error loading {filename}"
        elif command == "syn on":
            # Enable syntax highlighting
            self.text_buffer.syntax_highlighting = True
            self.status_message = "Syntax highlighting enabled"
        elif command == "syn off":
            # Disable syntax highlighting
            self.text_buffer.syntax_highlighting = False
            self.status_message = "Syntax highlighting disabled"
        else:
            self.status_message = f"Unknown command: {command}"
    
    def move_cursor_left(self):
        if self.cursor_x > 0:
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            # Move to end of previous line
            self.cursor_y -= 1
            if self.cursor_y < len(self.text_buffer.lines):
                self.cursor_x = len(self.text_buffer.lines[self.cursor_y])
        self.ensure_cursor_visible()
    
    def move_cursor_right(self):
        if self.cursor_y < len(self.text_buffer.lines):
            line_length = len(self.text_buffer.lines[self.cursor_y])
            if self.cursor_x < line_length:
                self.cursor_x += 1
            elif self.cursor_y < len(self.text_buffer.lines) - 1:
                # Move to start of next line
                self.cursor_y += 1
                self.cursor_x = 0
        self.ensure_cursor_visible()
    
    def move_cursor_up(self):
        if self.cursor_y > 0:
            self.cursor_y -= 1
            # Adjust x position if line is shorter
            if self.cursor_y < len(self.text_buffer.lines):
                line_length = len(self.text_buffer.lines[self.cursor_y])
                if self.cursor_x > line_length:
                    self.cursor_x = line_length
        self.ensure_cursor_visible()
    
    def move_cursor_down(self):
        if self.cursor_y < len(self.text_buffer.lines) - 1:
            self.cursor_y += 1
            # Adjust x position if line is shorter
            if self.cursor_y < len(self.text_buffer.lines):
                line_length = len(self.text_buffer.lines[self.cursor_y])
                if self.cursor_x > line_length:
                    self.cursor_x = line_length
        self.ensure_cursor_visible()
    
    def handle_backspace(self):
        if self.cursor_x > 0 or self.cursor_y > 0:
            new_y, new_x = self.text_buffer.backspace(self.cursor_y, self.cursor_x)
            self.cursor_y, self.cursor_x = new_y, new_x
            self.ensure_cursor_visible()
    
    def ensure_cursor_visible(self):
        # Adjust vertical scroll if needed
        editor_height = self.height - 2
        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        elif self.cursor_y >= self.scroll_y + editor_height:
            self.scroll_y = self.cursor_y - editor_height + 1
        
        # Adjust horizontal scroll if needed
        if self.cursor_x < self.scroll_x:
            self.scroll_x = self.cursor_x
        elif self.cursor_x >= self.scroll_x + self.width - 5:  # -5 for line numbers
            self.scroll_x = self.cursor_x - self.width + 6
    
    def prompt_save_changes(self):
        if not self.text_buffer.modified:
            return True
        
        while True:
            self.stdscr.addstr(self.height - 1, 0, "Save changes? (y/n/c): ")
            self.stdscr.clrtoeol()
            self.stdscr.refresh()
            
            ch = self.stdscr.getch()
            if ch == ord('y'):
                success = self.text_buffer.save_file()
                if success:
                    return True
                else:
                    self.status_message = "Error saving file"
                    return False
            elif ch == ord('n'):
                return True
            elif ch == ord('c') or ch == 27:  # ESC
                return False


def main(stdscr):
    # Clear screen
    stdscr.clear()
    
    # Get filename from command line arguments
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    # Create and run editor
    editor = Editor(stdscr, filename)
    editor.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        pass
