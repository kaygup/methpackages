#!/usr/bin/env python3
import curses
import random
import time
from curses import wrapper

def main(stdscr):
    # Setup
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    
    # Initialize colors if terminal supports them
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Light water
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Deep water
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Foam/bubbles
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Plants
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Sunlight
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Waterfall parameters
    waterfall_width = min(width - 4, 60)  # Width of waterfall
    waterfall_left = (width - waterfall_width) // 2  # Center the waterfall
    waterfall_right = waterfall_left + waterfall_width
    waterfall_top = 2  # Top of the waterfall
    pool_top = height - 10  # Top of the pool
    
    # Create water particles
    particles = []
    for i in range(waterfall_width * 8):  # More particles for denser waterfall
        x = random.randint(waterfall_left, waterfall_right - 1)
        y = random.randint(waterfall_top, pool_top)
        speed = random.uniform(0.5, 1.5)
        particles.append({"x": x, "y": y, "speed": speed, "char": "│", "color": 1})
    
    # Create bubbles/foam
    bubbles = []
    for i in range(waterfall_width):
        x = random.randint(waterfall_left, waterfall_right - 1)
        y = random.randint(pool_top, height - 2)
        speed = random.uniform(0.1, 0.3)
        bubbles.append({"x": x, "y": y, "speed": speed, "char": random.choice(['o', 'O', '°', '*']), "color": 3})
    
    # Create rocks for the waterfall to flow around
    rocks = []
    for i in range(waterfall_width // 5):
        x = random.randint(waterfall_left + 1, waterfall_right - 2)
        y = random.randint(waterfall_top + 5, pool_top - 5)
        size = random.randint(1, 3)
        rocks.append({"x": x, "y": y, "size": size})
    
    # Create sunlight rays
    sunlight = []
    for i in range(5):
        x = random.randint(waterfall_left - 10, waterfall_right + 10)
        y = random.randint(waterfall_top, waterfall_top + 5)
        length = random.randint(3, 8)
        sunlight.append({"x": x, "y": y, "length": length})
    
    # Create plants (decorative elements)
    plants = []
    for i in range(10):
        x = random.randint(waterfall_left - 15, waterfall_right + 15)
        if x < waterfall_left - 2 or x > waterfall_right + 2:  # Only place plants away from the main waterfall
            y = random.randint(pool_top, height - 2)
            plant_type = random.choice(['╿', '┤', '╽', '╾'])
            plants.append({"x": x, "y": y, "type": plant_type})
    
    # Draw banks and cliff
    def draw_static_elements():
        # Draw cliff top (where waterfall starts)
        for x in range(waterfall_left - 2, waterfall_right + 2):
            stdscr.addstr(waterfall_top - 1, x, "═", curses.A_BOLD)
        
        # Draw left bank
        for y in range(waterfall_top, pool_top):
            stdscr.addstr(y, waterfall_left - 2, "║", curses.A_BOLD)
        
        # Draw right bank
        for y in range(waterfall_top, pool_top):
            stdscr.addstr(y, waterfall_right + 1, "║", curses.A_BOLD)
        
        # Draw the pool borders
        for x in range(waterfall_left - 15, waterfall_right + 15):
            if x <= waterfall_left - 2 or x >= waterfall_right + 2:
                stdscr.addstr(pool_top, x, "═", curses.A_BOLD)
        
        # Draw pool left and right extended sides
        for y in range(pool_top + 1, height - 1):
            stdscr.addstr(y, waterfall_left - 15, "║", curses.A_BOLD)
            stdscr.addstr(y, waterfall_right + 14, "║", curses.A_BOLD)
        
        # Draw pool bottom
        for x in range(waterfall_left - 15, waterfall_right + 15):
            stdscr.addstr(height - 1, x, "═", curses.A_BOLD)
        
        # Add some decorative rocks
        for rock in rocks:
            if rock["size"] == 1:
                try:
                    stdscr.addstr(rock["y"], rock["x"], "◊", curses.A_BOLD)
                except curses.error:
                    pass
            elif rock["size"] == 2:
                try:
                    stdscr.addstr(rock["y"], rock["x"], "◈", curses.A_BOLD)
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(rock["y"] - 1, rock["x"], "╱╲", curses.A_BOLD)
                    stdscr.addstr(rock["y"], rock["x"], "╲╱", curses.A_BOLD)
                except curses.error:
                    pass
        
        # Draw plants
        for plant in plants:
            try:
                stdscr.addstr(plant["y"], plant["x"], plant["type"], 
                             curses.color_pair(4) | curses.A_BOLD)
            except curses.error:
                pass
        
        # Draw sunlight rays
        for ray in sunlight:
            for i in range(ray["length"]):
                try:
                    stdscr.addstr(ray["y"] + i, ray["x"], "╲", 
                                 curses.color_pair(5))
                except curses.error:
                    pass
    
    # Title
    title = "Cascading Waterfall"
    try:
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
    except curses.error:
        pass
    
    # Instruction
    instruction = "Press 'q' to quit"
    try:
        stdscr.addstr(height - 1, 2, instruction)
    except curses.error:
        pass
    
    # Animation loop
    frame = 0
    running = True
    while running:
        # Check for key press
        stdscr.nodelay(True)
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            running = False
            break
        
        stdscr.clear()
        
        # Draw static elements
        draw_static_elements()
        
        # Fill the pool with water
        for y in range(pool_top + 1, height - 1):
            for x in range(waterfall_left - 14, waterfall_right + 14):
                if (x > waterfall_left - 15 and x < waterfall_right + 14):
                    water_char = random.choice(['≈', '~', '≈', '~', ' '])
                    color = 2 if random.random() > 0.7 else 1
                    try:
                        stdscr.addstr(y, x, water_char, curses.color_pair(color))
                    except curses.error:
                        pass
        
        # Update and draw water particles
        for p in particles:
            p["y"] += p["speed"]
            
            # If reached the pool, reset to top of waterfall
            if p["y"] >= pool_top:
                p["y"] = waterfall_top
                p["x"] = random.randint(waterfall_left, waterfall_right - 1)
            
            # If particle hits a rock, make it flow around
            for rock in rocks:
                rock_range = 1 if rock["size"] == 1 else 2 if rock["size"] == 2 else 3
                if (abs(p["x"] - rock["x"]) < rock_range and 
                    abs(p["y"] - rock["y"]) < rock_range):
                    # Flow around rock
                    if p["x"] < rock["x"]:
                        p["x"] -= 0.5
                    else:
                        p["x"] += 0.5
            
            # Keep particles within waterfall bounds
            p["x"] = max(waterfall_left, min(waterfall_right - 1, p["x"]))
            
            # Draw the particle
            water_chars = ['│', '╽', '╿', '║']
            p["char"] = random.choice(water_chars)
            try:
                stdscr.addstr(int(p["y"]), int(p["x"]), p["char"], 
                             curses.color_pair(p["color"]))
            except curses.error:
                pass
        
        # Update and draw bubbles/foam
        for b in bubbles:
            # Bubbles move upward and side to side slightly
            b["y"] -= b["speed"]
            if random.random() > 0.7:
                b["x"] += random.choice([-0.2, 0.2])
            
            # If bubble reaches top of pool, create new bubble
            if b["y"] < pool_top or b["y"] > height - 2:
                b["y"] = random.randint(pool_top + 1, height - 2)
                b["x"] = random.randint(waterfall_left, waterfall_right - 1)
            
            # Keep bubbles within bounds
            b["x"] = max(waterfall_left - 14, min(waterfall_right + 13, b["x"]))
            
            # Draw the bubble
            try:
                stdscr.addstr(int(b["y"]), int(b["x"]), b["char"], 
                             curses.color_pair(b["color"]))
            except curses.error:
                pass
        
        # Add splashing effect at the base of the waterfall
        if frame % 2 == 0:
            for i in range(10):
                splash_x = random.randint(waterfall_left, waterfall_right - 1)
                splash_chars = ["*", ".", "o", "'"]
                try:
                    stdscr.addstr(pool_top, splash_x, random.choice(splash_chars), 
                                 curses.color_pair(3) | curses.A_BOLD)
                except curses.error:
                    pass
        
        # Update frame counter
        frame += 1
        
        # Render the screen
        stdscr.refresh()
        
        # Control animation speed
        time.sleep(0.05)

if __name__ == "__main__":
    try:
        wrapper(main)
    except KeyboardInterrupt:
        print("Exiting waterfall animation...")
