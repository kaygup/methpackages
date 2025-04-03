#!/usr/bin/env python3
"""
GitTree - A terminal animation showing a growing tree
"""

import os
import random
import time
import curses
import signal
import sys
from math import sin, cos, pi

# Terminal colors
class Colors:
    GREEN = 1
    BROWN = 2
    LIGHT_GREEN = 3
    YELLOW = 4
    RED = 5
    CYAN = 6
    MAGENTA = 7

# Tree parts
class TreeParts:
    TRUNK = ["|", "\\", "/"]
    BRANCH = ["\\", "/", "-", "_"]
    LEAF = ["*", "o", "•", "✿", "✽", "❀", "✸", "♠", "✧"]
    FRUIT = ["@", "O", "●", "○", "◍", "◉"]

class Tree:
    def __init__(self, max_height=20, max_width=60):
        self.max_height = max_height
        self.max_width = max_width
        self.trunk = []
        self.branches = []
        self.leaves = []
        self.fruits = []
        self.growth_stage = 0
        self.max_growth = 100
        self.season = 0  # 0: spring, 1: summer, 2: fall, 3: winter
        self.season_counter = 0
        
    def grow(self):
        # Advance growth stage
        self.growth_stage += 1
        
        # Handle seasons
        self.season_counter += 1
        if self.season_counter >= 100:
            self.season = (self.season + 1) % 4
            self.season_counter = 0
        
        # Grow trunk
        if self.growth_stage % 3 == 0 and len(self.trunk) < self.max_height:
            height = len(self.trunk)
            # Start at the bottom center
            x = self.max_width // 2
            # Add some natural variation
            x_offset = random.randint(-1, 1) if height > 2 else 0
            self.trunk.append((height, x + x_offset, random.choice(TreeParts.TRUNK)))
        
        # Add branches
        if self.growth_stage > 10 and random.random() < 0.15:
            if len(self.trunk) > 3:  # Only add branches if trunk exists
                # Pick a random position on the trunk
                trunk_pos = random.randint(3, len(self.trunk) - 1)
                y, x, _ = self.trunk[trunk_pos]
                
                # Branch direction (-1 left, 1 right)
                direction = random.choice([-1, 1])
                length = random.randint(2, 5)
                
                for i in range(1, length + 1):
                    # Branch with some randomness
                    branch_y = y - random.randint(0, 1)
                    branch_x = x + (i * direction)
                    
                    # Don't branch outside screen
                    if 0 <= branch_x < self.max_width:
                        self.branches.append((branch_y, branch_x, random.choice(TreeParts.BRANCH)))
        
        # Add leaves
        if self.growth_stage > 20 and self.season != 3:  # No leaves in winter
            if random.random() < 0.3:
                if len(self.branches) > 0:
                    # Add leaves near branches
                    branch = random.choice(self.branches)
                    y, x, _ = branch
                    
                    leaf_y = y + random.randint(-1, 1)
                    leaf_x = x + random.randint(-1, 1)
                    
                    # Don't place leaves outside screen
                    if 0 <= leaf_y < self.max_height and 0 <= leaf_x < self.max_width:
                        leaf_char = random.choice(TreeParts.LEAF)
                        self.leaves.append((leaf_y, leaf_x, leaf_char))
        
        # Add fruits in summer
        if self.season == 1 and self.growth_stage > 50:
            if random.random() < 0.05:
                if len(self.branches) > 0:
                    branch = random.choice(self.branches)
                    y, x, _ = branch
                    
                    fruit_y = y + random.randint(-1, 1)
                    fruit_x = x + random.randint(-1, 1)
                    
                    if 0 <= fruit_y < self.max_height and 0 <= fruit_x < self.max_width:
                        fruit_char = random.choice(TreeParts.FRUIT)
                        self.fruits.append((fruit_y, fruit_x, fruit_char))
        
        # Fall season - randomly remove leaves
        if self.season == 2 and len(self.leaves) > 0:
            if random.random() < 0.1:
                self.leaves.pop(random.randint(0, len(self.leaves) - 1))
        
        # Winter - clear leaves and fruits
        if self.season == 3:
            self.leaves = []
            self.fruits = []

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(Colors.GREEN, curses.COLOR_GREEN, -1)
    curses.init_pair(Colors.BROWN, curses.COLOR_YELLOW, -1)
    curses.init_pair(Colors.LIGHT_GREEN, curses.COLOR_CYAN, -1)
    curses.init_pair(Colors.YELLOW, curses.COLOR_YELLOW, -1)
    curses.init_pair(Colors.RED, curses.COLOR_RED, -1)
    curses.init_pair(Colors.CYAN, curses.COLOR_CYAN, -1)
    curses.init_pair(Colors.MAGENTA, curses.COLOR_MAGENTA, -1)

def get_color_for_season(element_type, season):
    """Return appropriate color based on season and element type"""
    if element_type == "trunk" or element_type == "branch":
        return Colors.BROWN
    
    if element_type == "leaf":
        if season == 0:  # Spring
            return Colors.LIGHT_GREEN
        elif season == 1:  # Summer
            return Colors.GREEN
        elif season == 2:  # Fall
            return random.choice([Colors.YELLOW, Colors.RED])
        else:  # Winter
            return Colors.CYAN
    
    if element_type == "fruit":
        return random.choice([Colors.RED, Colors.YELLOW, Colors.MAGENTA])
    
    return Colors.GREEN

def safe_addstr(stdscr, y, x, char, attr=0):
    """Safely add a string to the screen, checking boundaries"""
    height, width = stdscr.getmaxyx()
    # Check if the position is within bounds (leave the last column alone)
    if 0 <= y < height and 0 <= x < width - 1:
        try:
            stdscr.addstr(y, x, char, attr)
        except curses.error:
            pass  # Ignore errors

def draw_tree(stdscr, tree):
    """Draw the tree on the screen"""
    season_names = ["Spring", "Summer", "Fall", "Winter"]
    
    # Draw season
    safe_addstr(stdscr, 0, 0, f"Season: {season_names[tree.season]}", 
                curses.color_pair(get_color_for_season("leaf", tree.season)))
    
    # Draw trunk
    for y, x, char in tree.trunk:
        safe_addstr(stdscr, y, x, char, curses.color_pair(Colors.BROWN))
    
    # Draw branches
    for y, x, char in tree.branches:
        safe_addstr(stdscr, y, x, char, curses.color_pair(Colors.BROWN))
    
    # Draw leaves
    for y, x, char in tree.leaves:
        safe_addstr(stdscr, y, x, char, curses.color_pair(get_color_for_season("leaf", tree.season)))
    
    # Draw fruits
    for y, x, char in tree.fruits:
        safe_addstr(stdscr, y, x, char, curses.color_pair(get_color_for_season("fruit", tree.season)))

def draw_ground(stdscr, width, height):
    """Draw ground at the bottom of the screen"""
    ground_y = height - 2  # Move up one to avoid the bottom right corner
    for x in range(width - 1):  # Leave the last column alone
        safe_addstr(stdscr, ground_y, x, "_", curses.color_pair(Colors.BROWN))

def draw_info(stdscr, height, width):
    """Draw information text at the bottom"""
    info_text = "Press 'q' to quit | 's' to change season | 'g' to grow faster"
    if height > 3:
        for i, char in enumerate(info_text):
            if i < width - 1:  # Ensure we don't write to the last column
                safe_addstr(stdscr, height - 3, i, char)

def handle_resize(stdscr, tree):
    """Handle terminal resize"""
    height, width = stdscr.getmaxyx()
    tree.max_height = height - 4  # Leave more room for info and ground
    tree.max_width = width - 1  # Stay away from the right edge
    
    # Adjust tree if terminal gets smaller
    tree.trunk = [(y, x, c) for y, x, c in tree.trunk if y < height - 4 and x < width - 1]
    tree.branches = [(y, x, c) for y, x, c in tree.branches if y < height - 4 and x < width - 1]
    tree.leaves = [(y, x, c) for y, x, c in tree.leaves if y < height - 4 and x < width - 1]
    tree.fruits = [(y, x, c) for y, x, c in tree.fruits if y < height - 4 and x < width - 1]

def main(stdscr):
    # Setup
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Set getch timeout
    stdscr.clear()
    
    init_colors()
    
    # Get terminal size
    height, width = stdscr.getmaxyx()
    tree = Tree(height - 4, width - 1)  # Leave room for info and stay away from edges
    
    # Handle signals
    def handle_sigint(sig, frame):
        curses.endwin()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_sigint)
    
    # Main loop
    while True:
        # Check for terminal resize
        new_height, new_width = stdscr.getmaxyx()
        if new_height != height or new_width != width:
            height, width = new_height, new_width
            handle_resize(stdscr, tree)
            stdscr.clear()
        
        # Handle input
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1  # No input available
            
        if key == ord('q'):
            break
        elif key == ord('s'):
            tree.season = (tree.season + 1) % 4
        elif key == ord('g'):
            # Grow faster
            for _ in range(5):
                tree.grow()
        
        try:
            stdscr.clear()
        except curses.error:
            pass  # Ignore clear errors
        
        # Grow the tree
        tree.grow()
        
        # Draw everything
        draw_ground(stdscr, width, height)
        draw_tree(stdscr, tree)
        draw_info(stdscr, height, width)
        
        try:
            stdscr.refresh()
        except curses.error:
            pass  # Ignore refresh errors
            
        time.sleep(0.1)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("Exiting GitTree...")
        sys.exit(0)
    except Exception as e:
        curses.endwin()
        print(f"Error: {e}")
        sys.exit(1)
