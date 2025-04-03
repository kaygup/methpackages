#!/usr/bin/env python3
"""
pygif - A simple terminal GIF player
Usage: pygif <gif_url>
"""

import sys
import time
import tempfile
import os
import urllib.request
from PIL import Image
import curses
import argparse

def download_gif(url, temp_dir):
    """Download a GIF from a URL to a temporary file."""
    try:
        temp_file = os.path.join(temp_dir, "temp_gif.gif")
        
        # Create a request with a User-Agent header to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        
        # Download the file
        with urllib.request.urlopen(req) as response, open(temp_file, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        
        return temp_file
    except Exception as e:
        print(f"Error downloading GIF: {e}")
        print("Tips to resolve:")
        print("- Check if the URL is correct and accessible")
        print("- Some websites block direct image access")
        print("- Try downloading the GIF manually and use the local path instead")
        sys.exit(1)

def get_terminal_size():
    """Get terminal size in characters."""
    return os.get_terminal_size()

def resize_frame(frame, max_width, max_height):
    """Resize a frame to fit terminal dimensions."""
    width, height = frame.width, frame.height
    
    # Calculate aspect ratio
    aspect = width / height
    
    # Adjust for terminal character aspect ratio (characters are taller than wide)
    term_aspect = 0.5  # Approximate width/height ratio of a terminal character
    
    # Calculate new dimensions
    new_width = min(max_width, int(max_height * aspect / term_aspect))
    new_height = min(max_height, int(new_width * term_aspect / aspect))
    
    return frame.resize((new_width, new_height), Image.LANCZOS)

def convert_to_ascii(frame):
    """Convert frame to ASCII art."""
    # Convert to grayscale
    frame = frame.convert("L")
    
    width, height = frame.size
    ascii_frame = []
    
    # ASCII character set from dark to light
    ascii_chars = " .:-=+*#%@"
    max_val = 255
    
    for y in range(height):
        line = ""
        for x in range(width):
            pixel_value = frame.getpixel((x, y))
            # Map pixel value to ASCII character
            index = int(pixel_value * (len(ascii_chars) - 1) / max_val)
            line += ascii_chars[index]
        ascii_frame.append(line)
    
    return ascii_frame

def play_gif(stdscr, gif_path):
    """Play GIF in terminal using curses."""
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    
    # Get terminal dimensions
    term_height, term_width = stdscr.getmaxyx()
    
    try:
        # Open GIF file
        gif = Image.open(gif_path)
        
        # Loop control
        running = True
        
        while running:
            try:
                # Loop through all frames
                for frame_index in range(gif.n_frames):
                    gif.seek(frame_index)
                    
                    # Get frame duration in milliseconds (default to 100ms if not available)
                    duration = gif.info.get('duration', 100) / 1000
                    
                    # Resize frame to fit terminal
                    resized_frame = resize_frame(gif, term_width, term_height - 1)
                    
                    # Convert to ASCII
                    ascii_frame = convert_to_ascii(resized_frame)
                    
                    # Clear screen
                    stdscr.clear()
                    
                    # Display ASCII frame
                    for y, line in enumerate(ascii_frame):
                        if y < term_height - 1:  # Avoid writing to the last line
                            stdscr.addstr(y, 0, line[:term_width-1])
                    
                    # Show info at the bottom
                    info_text = f"Frame {frame_index+1}/{gif.n_frames} - Press 'q' to quit"
                    stdscr.addstr(term_height-1, 0, info_text[:term_width-1])
                    
                    # Refresh screen
                    stdscr.refresh()
                    
                    # Check for quit key
                    stdscr.nodelay(True)
                    key = stdscr.getch()
                    if key == ord('q'):
                        running = False
                        break
                    
                    # Wait for frame duration
                    time.sleep(duration)
                    
            except KeyboardInterrupt:
                running = False
                break
                
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Error playing GIF: {e}")
        stdscr.refresh()
        stdscr.getch()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Play GIFs in terminal")
    parser.add_argument("url", help="URL or local path of the GIF to play")
    args = parser.parse_args()
    
    if not args.url:
        print("Usage: pygif <gif_url_or_path>")
        sys.exit(1)
    
    # Check if input is a URL or local file
    if args.url.startswith(('http://', 'https://')):
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download GIF
            gif_path = download_gif(args.url, temp_dir)
            
            # Play GIF
            curses.wrapper(play_gif, gif_path)
    else:
        # Assume it's a local file
        if not os.path.exists(args.url):
            print(f"Error: File '{args.url}' not found")
            sys.exit(1)
        
        # Play GIF
        curses.wrapper(play_gif, args.url)

if __name__ == "__main__":
    main()
