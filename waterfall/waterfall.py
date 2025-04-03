#!/usr/bin/env python3
import curses
import random
import time
import math
from collections import deque

def main(stdscr):
    # Initialize colors
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
    
    # Hide cursor
    curses.curs_set(0)
    
    # Get terminal dimensions
    max_y, max_x = stdscr.getmaxyx()
    
    # Set up the waterfall
    waterfall_width = max_x - 4
    waterfall_x = 2
    
    # Water animation parameters
    water_frames = []
    for i in range(6):
        frame = []
        for x in range(waterfall_width):
            frame.append(max_y // 2 + int(math.sin(x / 5 + i / 2) * 2))
        water_frames.append(frame)
    
    # Falling water particles
    water_particles = []
    
    # Foam particles at base of waterfall
    foam_particles = []
    
    # Bubbles floating up
    bubbles = []
    
    # Splash particles
    splash_particles = []
    
    # Rocks at the base
    rocks = []
    for i in range(waterfall_width // 8):
        x = random.randint(waterfall_x, waterfall_x + waterfall_width - 1)
        y = max_y - 2 - random.randint(0, 2)
        size = random.randint(1, 3)
        rocks.append((x, y, size))
    
    # Water pool at the bottom
    pool_level = max_y - 4
    
    # Animation frame counter
    frame_count = 0
    water_frame_idx = 0
    
    while True:
        stdscr.clear()
        frame_count += 1
        
        # Draw sky
        for y in range(pool_level - 15):
            for x in range(max_x):
                if random.random() < 0.001:
                    stdscr.addch(y, x, '*', curses.color_pair(15))  # White stars
        
        # Draw waterfall top (where water flows from)
        water_top = water_frames[water_frame_idx]
        water_frame_idx = (water_frame_idx + 1) % len(water_frames)
        
        for x in range(waterfall_width):
            water_top_y = water_top[x]
            stdscr.addch(water_top_y, waterfall_x + x, '~', curses.color_pair(39))  # Light blue
            
            # Add new water particles
            if random.random() < 0.3:
                water_particles.append([waterfall_x + x, water_top_y + 1, 0])
        
        # Draw main waterfall stream
        for x in range(waterfall_width):
            for y in range(water_top[x] + 1, pool_level):
                intensity = 1.0 - (y - water_top[x]) / (pool_level - water_top[x])
                char = '|'
                if random.random() < 0.05:
                    char = random.choice(['.', ':', '|'])
                
                # Different shades of blue based on intensity
                color = 33 + int(intensity * 6)  # Range from darker to lighter blue
                if y > pool_level - 3:
                    color = 45  # Splash zone
                
                stdscr.addch(y, waterfall_x + x, char, curses.color_pair(color))
                
                # Add bubbles near the sides occasionally
                if (x < 3 or x > waterfall_width - 4) and random.random() < 0.01:
                    bubbles.append([waterfall_x + x, y, random.choice(['o', 'O', '°']), 0])
        
        # Update and draw water particles
        new_particles = []
        for particle in water_particles:
            x, y, age = particle
            y += random.choice([0, 1])
            x += random.choice([-1, 0, 0, 0, 1])
            age += 1
            
            if y < pool_level and 0 <= x < max_x and age < 20:
                try:
                    stdscr.addch(y, x, '.', curses.color_pair(45))
                    new_particles.append([x, y, age])
                except:
                    pass  # Ignore if we're trying to write outside bounds
            elif y >= pool_level - 1:
                # Create foam when hitting the water
                if random.random() < 0.3:
                    foam_particles.append([x, pool_level - 1, 0])
                # Create splash
                if random.random() < 0.2:
                    velocity_x = random.uniform(-1.5, 1.5)
                    velocity_y = random.uniform(-2.0, -1.0)
                    splash_particles.append([x, pool_level - 1, velocity_x, velocity_y, 0])
        water_particles = new_particles
        
        # Update and draw foam particles
        new_foam = []
        for particle in foam_particles:
            x, y, age = particle
            age += 1
            x += random.choice([-1, 0, 0, 0, 1])
            
            if age < 15 and 0 <= x < max_x:
                try:
                    char = random.choice(['~', '°', '·'])
                    stdscr.addch(y, x, char, curses.color_pair(15))
                    new_foam.append([x, y, age])
                except:
                    pass  # Ignore if we're trying to write outside bounds
        foam_particles = new_foam
        
        # Update and draw bubbles
        new_bubbles = []
        for bubble in bubbles:
            x, y, char, age = bubble
            y -= random.choice([0, 0, 1])
            x += random.choice([-1, 0, 0, 1])
            age += 1
            
            if y > water_top[min(max(0, x - waterfall_x), waterfall_width - 1)] and age < 30:
                try:
                    stdscr.addch(y, x, char, curses.color_pair(15))
                    new_bubbles.append([x, y, char, age])
                except:
                    pass  # Ignore if we're trying to write outside bounds
        bubbles = new_bubbles
        
        # Update and draw splash particles
        new_splash = []
        for particle in splash_particles:
            x, y, vx, vy, age = particle
            x += vx
            y += vy
            vy += 0.2  # Gravity
            age += 1
            
            if 0 <= int(x) < max_x and 0 <= int(y) < max_y and y < pool_level and age < 10:
                try:
                    stdscr.addch(int(y), int(x), '.', curses.color_pair(15))
                    new_splash.append([x, y, vx, vy, age])
                except:
                    pass  # Ignore if we're trying to write outside bounds
        splash_particles = new_splash
        
        # Draw rocks
        for rock in rocks:
            x, y, size = rock
            for dy in range(size):
                for dx in range(size * 2):
                    try:
                        if 0 <= y - dy < max_y and 0 <= x + dx - size < max_x:
                            rock_char = '#' if dy == 0 else '/'
                            stdscr.addch(y - dy, x + dx - size, rock_char, curses.color_pair(8))
                    except:
                        pass  # Ignore if we're trying to write outside bounds
        
        # Draw water pool
        for y in range(pool_level, max_y):
            for x in range(max_x):
                char = '~'
                if (x + y + frame_count) % 6 == 0:
                    char = '≈'
                elif (x + y + frame_count) % 6 == 3:
                    char = '~'
                
                # Add ripples near waterfall center
                center_dist = abs(x - (waterfall_x + waterfall_width // 2))
                if center_dist < waterfall_width // 2:
                    ripple_prob = 0.2 - (center_dist / (waterfall_width // 2)) * 0.2
                    if random.random() < ripple_prob:
                        char = '≈'
                
                try:
                    stdscr.addch(y, x, char, curses.color_pair(32))
                except:
                    pass  # Ignore if we're trying to write outside bounds
        
        # Add random bubbles in pool
        for _ in range(2):
            if random.random() < 0.1:
                x = random.randint(0, max_x - 1)
                y = random.randint(pool_level, max_y - 1)
                try:
                    stdscr.addch(y, x, random.choice(['o', 'O', '°']), curses.color_pair(15))
                except:
                    pass  # Ignore if we're trying to write outside bounds
        
        # Draw waterfall banks
        for y in range(0, pool_level):
            # Left bank
            bank_char = '/'
            stdscr.addch(y, waterfall_x - 1, bank_char, curses.color_pair(2))
            # Right bank
            bank_char = '\\'
            stdscr.addch(y, waterfall_x + waterfall_width, bank_char, curses.color_pair(2))
        
        # Draw title
        title = "WATERFALL"
        if max_x >= len(title) + 4:
            for i, char in enumerate(title):
                try:
                    stdscr.addch(1, (max_x - len(title)) // 2 + i, char, curses.A_BOLD | curses.color_pair(14))
                except:
                    pass
        
        # Instructions
        instructions = "Press 'q' to exit"
        if max_x >= len(instructions) + 4:
            for i, char in enumerate(instructions):
                try:
                    stdscr.addch(max_y - 1, (max_x - len(instructions)) // 2 + i, char, curses.color_pair(15))
                except:
                    pass
        
        stdscr.refresh()
        
        # Handle input
        stdscr.timeout(50)  # 50ms delay for animation speed
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == curses.KEY_RESIZE:
            max_y, max_x = stdscr.getmaxyx()
            waterfall_width = min(max_x - 4, waterfall_width)
            pool_level = max_y - 4
            # Reinitialize water frames for new width
            water_frames = []
            for i in range(6):
                frame = []
                for x in range(waterfall_width):
                    frame.append(max_y // 2 + int(math.sin(x / 5 + i / 2) * 2))
                water_frames.append(frame)

if __name__ == "__main__":
    try:
        # Initialize curses
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    finally:
        print("Thank you for watching the waterfall!")
