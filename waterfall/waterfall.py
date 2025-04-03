#!/usr/bin/env python3
"""
A colorful terminal waterfall animation for decoration
"""

import curses
import random
import time
import argparse
import signal
import sys

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit gracefully"""
    curses.endwin()
    sys.exit(0)

class WaterfallAnimation:
    def __init__(self, stdscr, speed=0.05, density=0.2):
        self.stdscr = stdscr
        self.speed = speed
        self.density = density
        self.setup_screen()
        self.setup_colors()
        self.initialize_drops()

    def setup_screen(self):
        """Configure the screen settings"""
        curses.curs_set(0)  # Hide cursor
        self.stdscr.timeout(0)  # Non-blocking input
        self.height, self.width = self.stdscr.getmaxyx()
        self.stdscr.clear()

    def setup_colors(self):
        """Initialize color pairs"""
        curses.start_color()
        curses.use_default_colors()
        
        # Create a blue-to-cyan gradient
        self.color_pairs = []
        for i in range(1, 8):
            # Gradient from darker blue to lighter cyan
            curses.init_pair(i, i % 8, -1)
            self.color_pairs.append(curses.color_pair(i))

    def initialize_drops(self):
        """Create the initial water drops"""
        self.drops = []
        num_drops = int(self.width * self.density)
        
        for _ in range(num_drops):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            length = random.randint(2, 6)
            speed = random.uniform(0.2, 1.0)
            self.drops.append({
                'x': x,
                'y': y,
                'length': length,
                'speed': speed,
                'counter': 0,
                'char': random.choice(['~', '≈', '≋', '≣', '⋮', '⫶', '◦'])
            })

    def update_drops(self):
        """Update the position of each drop"""
        for drop in self.drops:
            drop['counter'] += drop['speed']
            
            if drop['counter'] >= 1:
                drop['y'] += 1
                drop['counter'] = 0
                
                # If drop goes off screen, reset it at the top
                if drop['y'] >= self.height:
                    drop['y'] = 0
                    drop['x'] = random.randint(0, self.width - 1)

    def draw_drops(self):
        """Draw all water drops on the screen"""
        self.stdscr.clear()
        
        for drop in self.drops:
            x, y = drop['x'], drop['y']
            
            # Draw the drop and its trail with color gradient
            for i in range(drop['length']):
                trail_y = y - i
                
                if 0 <= trail_y < self.height and 0 <= x < self.width:
                    # Use different colors for different parts of the trail
                    color = self.color_pairs[min(i, len(self.color_pairs) - 1)]
                    
                    # Main character for the drop head
                    if i == 0:
                        self.stdscr.addstr(trail_y, x, drop['char'], color | curses.A_BOLD)
                    # Trail fades out
                    else:
                        intensity = drop['length'] - i
                        trail_char = '·' if i < drop['length'] - 1 else ' '
                        if random.random() < intensity / drop['length']:
                            self.stdscr.addstr(trail_y, x, trail_char, color)
        
        self.stdscr.refresh()

    def add_ripples(self):
        """Occasionally add ripple effects where drops hit surfaces"""
        for drop in self.drops:
            # Random chance to create a ripple at the bottom
            if drop['y'] == self.height - 1 and random.random() < 0.1:
                ripple_x = drop['x']
                for offset in [-2, -1, 1, 2]:
                    if 0 <= ripple_x + offset < self.width:
                        char = '○' if abs(offset) == 2 else '◎'
                        self.stdscr.addstr(
                            drop['y'], 
                            ripple_x + offset, 
                            char, 
                            random.choice(self.color_pairs)
                        )

    def run(self):
        """Main animation loop"""
        while True:
            # Check for key press to exit
            key = self.stdscr.getch()
            if key == ord('q'):
                break
                
            self.update_drops()
            self.draw_drops()
            self.add_ripples()
            
            time.sleep(self.speed)

def main(stdscr):
    parser = argparse.ArgumentParser(description="Terminal Waterfall Animation")
    parser.add_argument("--speed", type=float, default=0.05, 
                        help="Animation speed (lower is faster)")
    parser.add_argument("--density", type=float, default=0.2, 
                        help="Density of drops (0.0-1.0)")
    
    # Parse arguments without the script name
    args = parser.parse_args()
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the animation
    animation = WaterfallAnimation(stdscr, args.speed, args.density)
    animation.run()

if __name__ == "__main__":
    curses.wrapper(main)
