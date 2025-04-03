#!/usr/bin/env python3
import math
import time
import os
import sys
import random
import curses
from curses import wrapper

class Point3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        
    def rotateX(self, angle):
        """ Rotate the point around the X axis by the given angle in radians. """
        y = self.y * math.cos(angle) - self.z * math.sin(angle)
        z = self.y * math.sin(angle) + self.z * math.cos(angle)
        return Point3D(self.x, y, z)
    
    def rotateY(self, angle):
        """ Rotate the point around the Y axis by the given angle in radians. """
        x = self.z * math.sin(angle) + self.x * math.cos(angle)
        z = self.z * math.cos(angle) - self.x * math.sin(angle)
        return Point3D(x, self.y, z)
    
    def rotateZ(self, angle):
        """ Rotate the point around the Z axis by the given angle in radians. """
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Point3D(x, y, self.z)
    
    def project(self, win_width, win_height, fov, distance):
        """ Transforms this 3D point to 2D using a perspective projection. """
        factor = fov / (distance + self.z)
        x = self.x * factor + win_width / 2
        y = -self.y * factor + win_height / 2
        return Point3D(x, y, self.z)

def get_penguin_vertices():
    # A simplified 3D model of a penguin
    vertices = [
        # Body
        Point3D(-3, -3, 0), Point3D(3, -3, 0), Point3D(3, 3, 0), Point3D(-3, 3, 0),
        Point3D(-2, -2, 4), Point3D(2, -2, 4), Point3D(2, 2, 4), Point3D(-2, 2, 4),
        
        # Head
        Point3D(-2, -6, 2), Point3D(2, -6, 2), Point3D(2, -3, 2), Point3D(-2, -3, 2),
        Point3D(-1.5, -5.5, 4), Point3D(1.5, -5.5, 4), Point3D(1.5, -3.5, 4), Point3D(-1.5, -3.5, 4),
        
        # Beak
        Point3D(-0.5, -6.5, 3), Point3D(0.5, -6.5, 3), Point3D(0, -7, 3.5),
        
        # Left Wing
        Point3D(-3, -2, 1), Point3D(-4, -1, 1), Point3D(-4, 1, 1), Point3D(-3, 2, 1),
        
        # Right Wing
        Point3D(3, -2, 1), Point3D(4, -1, 1), Point3D(4, 1, 1), Point3D(3, 2, 1),
        
        # Feet
        Point3D(-1.5, 3, 0), Point3D(-2, 4, 0), Point3D(-1, 4, 0),
        Point3D(1.5, 3, 0), Point3D(2, 4, 0), Point3D(1, 4, 0)
    ]
    return vertices

def get_penguin_faces():
    # Define the faces using the vertices indices
    faces = [
        # Body
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 7, 3), (1, 5, 6, 2), (0, 1, 5, 4), (3, 2, 6, 7),
        
        # Head
        (8, 9, 10, 11), (12, 13, 14, 15), (8, 12, 15, 11), (9, 13, 14, 10), (8, 9, 13, 12), (11, 10, 14, 15),
        
        # Beak
        (16, 17, 18),
        
        # Left Wing
        (20, 21, 22, 23),
        
        # Right Wing
        (24, 25, 26, 27),
        
        # Feet
        (28, 29, 30), (31, 32, 33)
    ]
    return faces

def get_penguin_colors():
    # Define colors for each face
    colors = [
        1, 1, 1, 1, 1, 1,  # Body (black)
        1, 1, 1, 1, 1, 1,  # Head (black)
        3,                  # Beak (yellow)
        1,                  # Left Wing (black)
        1,                  # Right Wing (black)
        3, 3                # Feet (yellow)
    ]
    return colors

def draw_penguin(stdscr):
    # Initialize curses colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White on black for body
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Cyan on black for belly
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Yellow on black for beak and feet
    
    # Set up the screen
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Constants for the 3D projection
    fov = 256
    distance = 10
    
    # Get penguin data
    vertices = get_penguin_vertices()
    faces = get_penguin_faces()
    colors = get_penguin_colors()
    
    # Rotation angles
    angleX, angleY, angleZ = 0, 0, 0
    
    # Animation loop
    try:
        while True:
            # Clear screen
            stdscr.clear()
            
            # Display title
            title = "3D ASCII Linux Penguin"
            stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
            
            # Add instructions
            stdscr.addstr(height-2, 2, "Press 'q' to exit", curses.A_DIM)
            
            # Set up rotation angles
            angleX += 0.03
            angleY += 0.05
            angleZ += 0.01
            
            # Calculate rotated 3D points
            t = []
            for v in vertices:
                # Rotate in all 3 axes
                r = v.rotateX(angleX).rotateY(angleY).rotateZ(angleZ)
                # Transform 3D to 2D
                p = r.project(width, height, fov, distance)
                t.append(p)
            
            # Calculate average Z values for each face for depth sorting
            avg_z = []
            for i, face in enumerate(faces):
                z = sum(t[v].z for v in face) / len(face)
                avg_z.append((i, z))
            
            # Sort faces by Z depth (painter's algorithm) - draw furthest first
            for idx, _ in sorted(avg_z, key=lambda x: x[1], reverse=True):
                face = faces[idx]
                color_pair = colors[idx]
                
                # Convert to screen coordinates and draw
                screen_coords = [(int(t[v].x), int(t[v].y)) for v in face]
                
                # Draw faces using ASCII art
                # Simple drawing - connect points with ASCII characters
                if len(face) == 3:  # Triangle
                    draw_line(stdscr, screen_coords[0], screen_coords[1], color_pair)
                    draw_line(stdscr, screen_coords[1], screen_coords[2], color_pair)
                    draw_line(stdscr, screen_coords[2], screen_coords[0], color_pair)
                else:  # Quad
                    draw_line(stdscr, screen_coords[0], screen_coords[1], color_pair)
                    draw_line(stdscr, screen_coords[1], screen_coords[2], color_pair)
                    draw_line(stdscr, screen_coords[2], screen_coords[3], color_pair)
                    draw_line(stdscr, screen_coords[3], screen_coords[0], color_pair)
                    
                    # Fill the face with some ASCII characters
                    fill_face(stdscr, screen_coords, color_pair)
            
            # Refresh the screen
            stdscr.refresh()
            
            # Check for key press
            stdscr.nodelay(True)
            key = stdscr.getch()
            if key == ord('q'):
                break
            
            # Control the speed of animation
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass

def draw_line(stdscr, start, end, color):
    """Draw a line using Bresenham's line algorithm"""
    x1, y1 = start
    x2, y2 = end
    
    # Check if points are within screen boundaries
    height, width = stdscr.getmaxyx()
    if (x1 < 0 or x1 >= width or y1 < 0 or y1 >= height or 
        x2 < 0 or x2 >= width or y2 < 0 or y2 >= height):
        return
    
    # Bresenham's line algorithm
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    while True:
        try:
            # Draw the point with appropriate character and color
            stdscr.addch(y1, x1, get_line_char(dx, dy), curses.color_pair(color))
        except curses.error:
            pass  # Ignore if we try to draw out of bounds
        
        if x1 == x2 and y1 == y2:
            break
        
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def get_line_char(dx, dy):
    """Return appropriate ASCII character based on line slope"""
    if dx > dy * 2:
        return '-'
    elif dy > dx * 2:
        return '|'
    else:
        return '+'

def fill_face(stdscr, coords, color):
    """Simple face filling with ASCII characters"""
    # Calculate bounding box
    x_coords = [x for x, y in coords]
    y_coords = [y for x, y in coords]
    min_x = max(0, min(x_coords))
    max_x = min(stdscr.getmaxyx()[1]-1, max(x_coords))
    min_y = max(0, min(y_coords))
    max_y = min(stdscr.getmaxyx()[0]-1, max(y_coords))
    
    # Simple fill - just add some dots inside the bounding box
    # This is a very simple approach and doesn't check if points are actually inside the polygon
    height, width = stdscr.getmaxyx()
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if y < height and x < width:
                if is_point_in_polygon(x, y, coords) and random.random() > 0.7:
                    try:
                        char = ' ' if color == 1 else ('*' if color == 2 else 'o')
                        stdscr.addch(y, x, char, curses.color_pair(color))
                    except curses.error:
                        pass

def is_point_in_polygon(x, y, polygon):
    """Check if point is inside a polygon using ray casting algorithm"""
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def main():
    # Clear the terminal before starting
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Show the title before entering curses mode
    print("3D ASCII Linux Penguin")
    print("Starting in 1 second...")
    time.sleep(1)
    
    # Start the curses application
    try:
        wrapper(draw_penguin)
    finally:
        # Clear the terminal when exiting
        os.system('clear' if os.name == 'posix' else 'cls')
        print("Thanks for watching the ASCII Penguin!")

if __name__ == "__main__":
    main()
