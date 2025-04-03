#!/usr/bin/env python3
import curses
import random
import time
import sys

def main(stdscr):
    # Setup terminal
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    
    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_CYAN, -1)      # Light water
    curses.init_pair(2, curses.COLOR_BLUE, -1)      # Deep water
    curses.init_pair(3, curses.COLOR_WHITE, -1)     # Foam/bubbles
    curses.init_pair(4, curses.COLOR_GREEN, -1)     # Plants
    curses.init_pair(5, curses.COLOR_YELLOW, -1)    # Sand/rocks
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Waterfall position and dimensions
    waterfall_width = width // 3
    waterfall_start = (width - waterfall_width) // 2
    waterfall_end = waterfall_start + waterfall_width
    
    # Rock formations
    rocks = []
    for i in range(width // 10):
        rocks.append((random.randint(0, width-1), 
                     random.randint(height-5, height-1)))
    
    # Waterfall flow streams
    streams = []
    for i in range(waterfall_start, waterfall_end):
        streams.append({
            'x': i,
            'y': 1,
            'speed': random.uniform(0.2, 0.6),
            'last_update': 0,
            'char': '|'
        })
    
    # Bubble particles
    bubbles = []
    foam = []
    
    # Main loop
    frame = 0
    try:
        while True:
            # Check for quit key
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    break
            except:
                pass
                
            # Clear screen for new frame
            stdscr.clear()
            
            # Draw landscape
            # Draw sky
            for y in range(height // 6):
                for x in range(width):
                    if random.random() < 0.005:
                        stdscr.addstr(y, x, '*')  # Stars
            
            # Draw waterfall source (river at top)
            for x in range(waterfall_start - 5, waterfall_end + 5):
                if 0 <= x < width:
                    stdscr.addstr(0, x, '~', curses.color_pair(1))
            
            # Draw rock formations
            for rock_x, rock_y in rocks:
                if 0 <= rock_x < width and 0 <= rock_y < height:
                    stdscr.addstr(rock_y, rock_x, '#', curses.color_pair(5))
            
            # Create new bubbles
            if frame % 3 == 0:
                for i in range(waterfall_start, waterfall_end):
                    if random.random() < 0.1:
                        bubbles.append({
                            'x': i,
                            'y': random.randint(5, height - 10),
                            'lifetime': random.randint(5, 20),
                            'char': random.choice(['o', '.', '°'])
                        })
            
            # Process and draw waterfall streams
            current_time = time.time()
            for stream in streams:
                elapsed = current_time - stream.get('last_update', 0)
                if elapsed > stream.get('speed', 0.5):
                    stream['y'] = min(stream['y'] + 1, height - 1)
                    stream['last_update'] = current_time
                
                # Draw stream
                x, y = stream['x'], stream['y']
                for trail_y in range(1, y):
                    if 0 <= x < width and 0 <= trail_y < height:
                        if trail_y < height // 3:
                            color = curses.color_pair(1)  # Light at top
                        else:
                            color = curses.color_pair(2)  # Darker below
                        
                        stdscr.addstr(trail_y, x, stream['char'], color)
                
                # Create foam at the bottom
                if y >= height - 6 and random.random() < 0.2:
                    foam.append({
                        'x': x + random.randint(-2, 2),
                        'y': height - 2,
                        'lifetime': random.randint(5, 15),
                        'char': random.choice(['~', '≈', '≋', '∽'])
                    })
            
            # Process and draw bubbles
            for bubble in bubbles[:]:
                bubble['lifetime'] -= 1
                if bubble['lifetime'] <= 0:
                    bubbles.remove(bubble)
                else:
                    if random.random() < 0.3:
                        # Make bubbles rise slightly and move sideways
                        bubble['y'] = max(1, bubble['y'] - 1)
                        bubble['x'] += random.choice([-1, 0, 1])
                    
                    if 0 <= bubble['x'] < width and 0 <= bubble['y'] < height:
                        stdscr.addstr(bubble['y'], bubble['x'], bubble['char'], curses.color_pair(3))
            
            # Process and draw foam
            for f in foam[:]:
                f['lifetime'] -= 1
                if f['lifetime'] <= 0:
                    foam.remove(f)
                else:
                    if 0 <= f['x'] < width and 0 <= f['y'] < height:
                        stdscr.addstr(f['y'], f['x'], f['char'], curses.color_pair(3))
            
            # Draw splash pool at bottom
            for y in range(height - 3, height):
                for x in range(width):
                    if random.random() < 0.7:
                        char = '~'
                        if y == height - 3 and waterfall_start <= x <= waterfall_end:
                            char = '≈'  # More turbulent under the waterfall
                        if 0 <= x < width and 0 <= y < height:
                            stdscr.addstr(y, x, char, curses.color_pair(1))
            
            # Draw some vegetation
            if frame % 10 == 0:
                for i in range(5):
                    x = random.randint(0, width-1)
                    y = height - 3
                    if random.random() < 0.01 and 0 <= x < width and 0 <= y < height:
                        stdscr.addstr(y, x, random.choice(['╿', '┃', '│']), curses.color_pair(4))
            
            # Update the screen
            stdscr.refresh()
            
            # Control the frame rate
            time.sleep(0.05)
            frame += 1
            
            # Reset streams that reached bottom
            for stream in streams:
                if stream['y'] >= height - 3:
                    stream['y'] = 1
                    stream['speed'] = random.uniform(0.2, 0.6)
                    
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Terminal Waterfall Animation")
        print("---------------------------")
        print("Controls:")
        print("  q     - Quit the animation")
        print("  Ctrl+C - Quit the animation")
        sys.exit(0)
        
    print("Starting waterfall animation... (Press 'q' or Ctrl+C to exit)")
    time.sleep(1)
    curses.wrapper(main)
