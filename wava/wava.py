#!/usr/bin/env python3

import os
import sys
import time
import math
import curses
import numpy as np
import pyaudio
import signal
from argparse import ArgumentParser

class AudioVisualizer:
    def __init__(self, 
                 rate=44100, 
                 chunk_size=1024, 
                 device_index=None,
                 wave_count=32,
                 sensitivity=5.0,
                 falloff=0.9,
                 color_scheme="rainbow"):
        self.rate = rate
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.wave_count = wave_count
        self.sensitivity = sensitivity
        self.falloff = falloff
        self.color_scheme = color_scheme
        self.running = True
        self.audio = None
        self.stream = None
        self.screen = None
        self.init_audio()
        
    def init_audio(self):
        """Initialize PyAudio"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Get default input device if none specified
            if self.device_index is None:
                self.device_index = self.audio.get_default_input_device_info()['index']
                
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self.device_index
            )
        except Exception as e:
            print(f"Error initializing audio: {e}")
            if self.audio:
                self.audio.terminate()
            sys.exit(1)
    
    def start(self):
        """Start the visualizer"""
        # Set up signal handler for clean exit
        signal.signal(signal.SIGINT, self.handle_interrupt)
        
        # Initialize curses
        self.screen = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.screen.nodelay(True)
        self.screen.keypad(True)
        
        # Initialize color pairs if terminal supports colors
        if curses.has_colors() and curses.can_change_color():
            for i in range(1, 8):
                curses.init_pair(i, i, -1)
        
        # Main loop
        fft_data = np.zeros(self.wave_count)
        try:
            while self.running:
                # Handle key presses
                ch = self.screen.getch()
                if ch == ord('q'):
                    break
                elif ch == ord('+') or ch == ord('='):
                    self.sensitivity = min(20.0, self.sensitivity + 0.5)
                elif ch == ord('-'):
                    self.sensitivity = max(0.5, self.sensitivity - 0.5)
                
                # Get audio data
                try:
                    data = np.frombuffer(self.stream.read(self.chunk_size, exception_on_overflow=False), dtype=np.float32)
                    # Apply FFT
                    fft = np.abs(np.fft.rfft(data))
                    # Compress to desired number of frequency bands
                    fft = np.abs(fft[:self.chunk_size//2])
                    bands = np.array_split(fft, self.wave_count)
                    new_fft = np.array([np.mean(band) for band in bands])
                    
                    # Apply sensitivity and falloff
                    fft_data = np.maximum(new_fft * self.sensitivity, fft_data * self.falloff)
                except Exception as e:
                    # Just keep going if there's a read error
                    pass
                
                # Draw the visualizer
                self.draw_visualizer(fft_data)
                
                # Sleep a bit to reduce CPU usage
                time.sleep(0.03)
                
        finally:
            self.cleanup()
    
    def draw_visualizer(self, fft_data):
        """Draw the wave-based visualizer"""
        # Get terminal dimensions
        max_y, max_x = self.screen.getmaxyx()
        
        # Clear the screen
        self.screen.clear()
        
        # Draw title and controls
        title = "NOX AUDIO VISUALIZER"
        if max_x > len(title) + 4:
            self.screen.addstr(0, (max_x - len(title)) // 2, title, curses.A_BOLD)
        
        if max_y > 3:
            controls = "q: quit | +/-: adjust sensitivity"
            if max_x > len(controls) + 4:
                self.screen.addstr(max_y - 1, (max_x - len(controls)) // 2, controls)
        
        # Normalize FFT data for display
        max_amplitude = np.max(fft_data) if np.max(fft_data) > 0 else 1
        normalized_fft = fft_data / max_amplitude
        
        # Available height for visualization
        viz_height = max_y - 3
        
        # Draw each wave (horizontal line)
        if viz_height >= self.wave_count:
            spacing = viz_height // self.wave_count
            for i, amp in enumerate(normalized_fft):
                y_pos = 2 + i * spacing
                if 2 <= y_pos < max_y - 1:
                    # Calculate wave points
                    wave_points = []
                    for x in range(max_x):
                        # Create a sine wave pattern that scales with amplitude
                        sine_val = math.sin(x / 4) * amp * (max_x // 8)
                        wave_points.append(int(sine_val))
                    
                    # Draw the wave
                    for x in range(max_x):
                        if 0 <= x < max_x and 0 <= y_pos + wave_points[x] < max_y:
                            # Choose color based on amplitude and position
                            if self.color_scheme == "rainbow":
                                color = (i % 7) + 1  # Rainbow colors (1-7)
                            else:
                                color = int(amp * 7) + 1  # Intensity-based colors
                                
                            try:
                                self.screen.addch(y_pos + wave_points[x], x, '■', curses.color_pair(color))
                            except curses.error:
                                # This can happen when trying to write to the bottom-right corner
                                pass
        
        # Refresh the screen
        self.screen.refresh()
    
    def handle_interrupt(self, sig, frame):
        """Handle keyboard interrupt"""
        self.running = False
    
    def cleanup(self):
        """Clean up resources"""
        # Close the curses window
        if self.screen:
            curses.nocbreak()
            self.screen.keypad(False)
            curses.echo()
            curses.endwin()
        
        # Close audio resources
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

def list_audio_devices():
    """List available audio input devices"""
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    
    print("Available audio input devices:")
    print("-" * 40)
    
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:  # Input device
            print(f"Device {i}: {device_info['name']}")
            print(f"  Input channels: {device_info['maxInputChannels']}")
            print(f"  Default sample rate: {device_info['defaultSampleRate']}")
            print("-" * 40)
    
    p.terminate()
    
def main():
    parser = ArgumentParser(description="NOX - Terminal Audio Visualizer")
    parser.add_argument("-d", "--device", type=int, help="Audio input device index")
    parser.add_argument("-r", "--rate", type=int, default=44100, help="Sample rate")
    parser.add_argument("-c", "--chunk", type=int, default=1024, help="Chunk size")
    parser.add_argument("-w", "--waves", type=int, default=32, help="Number of wave lines")
    parser.add_argument("-s", "--sensitivity", type=float, default=5.0, help="Visualization sensitivity")
    parser.add_argument("-f", "--falloff", type=float, default=0.9, help="Visualization falloff rate")
    parser.add_argument("--color", choices=["rainbow", "amplitude"], default="rainbow", help="Color scheme")
    parser.add_argument("-l", "--list-devices", action="store_true", help="List available audio devices and exit")
    
    args = parser.parse_args()
    
    if args.list_devices:
        list_audio_devices()
        return
    
    visualizer = AudioVisualizer(
        rate=args.rate,
        chunk_size=args.chunk,
        device_index=args.device,
        wave_count=args.waves,
        sensitivity=args.sensitivity,
        falloff=args.falloff,
        color_scheme=args.color
    )
    
    visualizer.start()

if __name__ == "__main__":
    main()
