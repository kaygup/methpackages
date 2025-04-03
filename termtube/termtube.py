#!/usr/bin/env python3
"""
TermTube - Play YouTube videos in terminal as ASCII art
"""

import os
import sys
import time
import argparse
import urllib.request
import urllib.parse
import json
import re
from subprocess import Popen, PIPE

try:
    import curses
    import pytube
    from PIL import Image
    import numpy as np
except ImportError:
    print("Missing dependencies. Please install required packages:")
    print("pip install pytube pillow numpy")
    sys.exit(1)

class TermTube:
    def __init__(self):
        self.chars = " .,:;irsXA253hMHGS#9B&@"
        self.fps = 15
        self.max_resolution = "720p"  # Default max resolution
        self.is_playing = False
        self.is_paused = False
        self.current_frame = 0
        self.total_frames = 0
        self.frames = []
        self.video_title = ""
        self.video_author = ""
        self.audio_process = None
        self.start_time = 0
        self.width = 80
        self.height = 40

    def extract_video_id(self, url):
        """Extract YouTube video ID from URL"""
        video_id = None
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([^&\n]+)',
            r'(?:youtu\.be\/)([^\?\n]+)',
            r'(?:youtube\.com\/embed\/)([^\?\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
                
        return video_id

    def download_video(self, url):
        """Download YouTube video"""
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")
                
            print(f"Downloading video: {url}")
            yt = pytube.YouTube(url)
            self.video_title = yt.title
            self.video_author = yt.author
            
            # Select video stream with max resolution up to specified max
            streams = yt.streams.filter(progressive=True, file_extension='mp4')
            selected_stream = None
            for stream in streams:
                res = stream.resolution
                if res:
                    res_value = int(res[:-1])  # Remove 'p' from 720p, 1080p, etc.
                    max_res_value = int(self.max_resolution[:-1])
                    if res_value <= max_res_value:
                        if not selected_stream or int(selected_stream.resolution[:-1]) < res_value:
                            selected_stream = stream
            
            if not selected_stream:
                raise ValueError(f"No suitable video stream found within {self.max_resolution} resolution")
                
            print(f"Selected stream: {selected_stream.resolution}")
            temp_dir = os.path.join(os.path.expanduser("~"), ".termtube")
            os.makedirs(temp_dir, exist_ok=True)
            
            video_path = selected_stream.download(output_path=temp_dir, filename="temp_video")
            
            print("Video downloaded successfully!")
            return video_path
            
        except Exception as e:
            print(f"Error downloading video: {e}")
            sys.exit(1)

    def convert_frame_to_ascii(self, img, width, height):
        """Convert PIL image to ASCII art"""
        img = img.resize((width, height))
        img = img.convert('L')  # Convert to grayscale
        pixels = np.array(img)
        ascii_img = ""
        
        for row in pixels:
            for pixel in row:
                ascii_img += self.chars[min(len(self.chars) - 1, int(pixel * len(self.chars) / 256))]
            ascii_img += "\n"
            
        return ascii_img

    def extract_frames(self, video_path, max_frames=None):
        """Extract frames from the video"""
        import cv2
        
        self.frames = []
        cap = cv2.VideoCapture(video_path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        
        # Calculate how many frames to skip to achieve target fps
        target_fps = min(15, self.fps)  # Limit to 15fps for terminal display
        frame_skip = max(1, int(self.fps / target_fps))
        
        print(f"Extracting frames (original FPS: {self.fps}, target FPS: {target_fps})...")
        print(f"Total frames: {self.total_frames}")
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Process only every nth frame
                if frame_count % frame_skip == 0:
                    # Convert cv2 frame to PIL image
                    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    self.frames.append(img)
                    
                    # Display progress
                    sys.stdout.write(f"\rExtracted {len(self.frames)} frames...")
                    sys.stdout.flush()
                    
                    # Limit the number of frames if specified
                    if max_frames and len(self.frames) >= max_frames:
                        break
                        
                frame_count += 1
                
            print(f"\nExtracted {len(self.frames)} frames at {target_fps}fps")
            
        finally:
            cap.release()

    def play_audio(self, video_path):
        """Play audio from the video file"""
        try:
            from ffmpeg import input, output
            audio_cmd = ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', video_path]
            self.audio_process = Popen(audio_cmd)
        except Exception as e:
            print(f"Could not play audio: {e}")

    def display_video(self, stdscr):
        """Display video frames in the terminal"""
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        
        # Get terminal dimensions
        max_y, max_x = stdscr.getmaxlines(), stdscr.getmaxyx()[1]
        self.width = max_x // 2
        self.height = (max_y - 5) // 1  # Leave space for controls
        
        # Calculate frame timing
        frame_time = 1.0 / min(15, self.fps)  # Cap at 15fps for terminal
        
        # Initial screen setup
        stdscr.nodelay(1)  # Non-blocking input
        
        # Display video metadata
        info_win = curses.newwin(3, max_x, 0, 0)
        info_win.addstr(0, 0, f"Title: {self.video_title[:max_x-8]}")
        info_win.addstr(1, 0, f"Author: {self.video_author[:max_x-9]}")
        info_win.refresh()
        
        # Create window for video
        video_win = curses.newwin(self.height, max_x, 3, 0)
        
        # Create window for controls
        control_win = curses.newwin(2, max_x, 3 + self.height, 0)
        controls = "Controls: Space = Pause/Play, Q = Quit, Left/Right = Seek 5 sec"
        control_win.addstr(0, 0, controls[:max_x-1])
        control_win.refresh()
        
        self.is_playing = True
        self.is_paused = False
        self.current_frame = 0
        self.start_time = time.time()
        
        while self.is_playing and self.current_frame < len(self.frames):
            if not self.is_paused:
                # Get current frame and convert to ASCII
                img = self.frames[self.current_frame]
                ascii_frame = self.convert_frame_to_ascii(img, self.width, self.height)
                
                # Display frame
                video_win.clear()
                for i, line in enumerate(ascii_frame.split('\n')):
                    if i < self.height:
                        video_win.addstr(i, 0, line[:max_x-1])
                video_win.refresh()
                
                # Display progress
                progress = min(100, int(100 * self.current_frame / len(self.frames)))
                control_win.addstr(1, 0, f"Progress: {progress}% [{self.current_frame}/{len(self.frames)}]")
                control_win.refresh()
                
                # Move to next frame
                self.current_frame += 1
                
            # Check for user input
            key = stdscr.getch()
            if key == ord('q'):
                self.is_playing = False
            elif key == ord(' '):
                self.is_paused = not self.is_paused
                control_win.addstr(1, max_x - 20, "PAUSED" if self.is_paused else "PLAYING")
                control_win.refresh()
            elif key == curses.KEY_RIGHT:
                # Skip forward 5 seconds
                skip_frames = int(min(15, self.fps) * 5)
                self.current_frame = min(len(self.frames) - 1, self.current_frame + skip_frames)
            elif key == curses.KEY_LEFT:
                # Skip backward 5 seconds
                skip_frames = int(min(15, self.fps) * 5)
                self.current_frame = max(0, self.current_frame - skip_frames)
                
            # Maintain frame rate
            if not self.is_paused:
                elapsed = time.time() - self.start_time
                target_time = self.current_frame * frame_time
                sleep_time = max(0, target_time - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        # Clean up
        if self.audio_process:
            self.audio_process.terminate()

    def play(self, url, max_resolution="720p"):
        """Main function to play YouTube video"""
        self.max_resolution = max_resolution
        
        # Download video
        video_path = self.download_video(url)
        
        # Extract frames
        self.extract_frames(video_path)
        
        if not self.frames:
            print("No frames extracted, cannot play video")
            return
        
        # Play audio in background
        self.play_audio(video_path)
        
        # Display video using curses
        try:
            curses.wrapper(self.display_video)
        except KeyboardInterrupt:
            print("Playback interrupted")
        finally:
            # Clean up
            if self.audio_process:
                self.audio_process.terminate()

def main():
    parser = argparse.ArgumentParser(description="TermTube - YouTube videos in terminal")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-r", "--resolution", default="720p", 
                        choices=["360p", "480p", "720p", "1080p"],
                        help="Maximum video resolution (default: 720p)")
    args = parser.parse_args()
    
    player = TermTube()
    player.play(args.url, args.resolution)

if __name__ == "__main__":
    main()
