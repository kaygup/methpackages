#!/usr/bin/env python3
import os
import time
import math
import signal
import numpy as np
import curses
import argparse
from threading import Thread
import sounddevice as sd

class AudioWaveVisualizer:
    def __init__(self, device=None, buffer_size=1024, sample_rate=44100, n_channels=2, fps=30):
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.n_channels = n_channels
        self.device = device
        self.fps = fps
        self.running = True
        self.audio_data = np.zeros((buffer_size, n_channels))
        self.screen = None
        
        # Wave visualization parameters
        self.amplitude_scale = 0.8
        self.wave_length = 30
        self.wave_speed = 0.05
        self.time = 0
        
        # Color palette (8-bit colors)
        self.colors = {
            'background': 0,
            'wave': [1, 2, 3, 4],  # Different colors for wave intensities
            'text': 7
        }
        
        # Parse arguments
        self.parse_args()
    
    def parse_args(self):
        parser = argparse.ArgumentParser(description='Terminal Audio Wave Visualizer (nox)')
        parser.add_argument('-d', '--device', type=int, help='Audio input device (numeric ID)')
        parser.add_argument('-b', '--buffer', type=int, default=self.buffer_size, 
                            help='Buffer size')
        parser.add_argument('-r', '--rate', type=int, default=self.sample_rate, 
                            help='Sample rate')
        parser.add_argument('-c', '--channels', type=int, default=self.n_channels, 
                            help='Number of channels')
        parser.add_argument('-f', '--fps', type=int, default=self.fps,
                            help='Frames per second')
        parser.add_argument('-l', '--list', action='store_true',
                            help='List available audio devices and exit')
        
        args = parser.parse_args()
        
        if args.list:
            print("Available audio input devices:")
            print(sd.query_devices())
            exit(0)
        
        if args.device is not None:
            self.device = args.device
        if args.buffer:
            self.buffer_size = args.buffer
        if args.rate:
            self.sample_rate = args.rate
        if args.channels:
            self.n_channels = args.channels
        if args.fps:
            self.fps = args.fps
    
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=os.sys.stderr)
        self.audio_data = indata.copy()
    
    def start_audio_stream(self):
        try:
            self.stream = sd.InputStream(
                device=self.device,
                channels=self.n_channels,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                callback=self.audio_callback
            )
            self.stream.start()
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            exit(1)
    
    def stop_audio_stream(self):
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
    
    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_BLUE, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_GREEN, -1)
        curses.init_pair(4, curses.COLOR_MAGENTA, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
    
    def draw_wave(self):
        try:
            if self.screen is None:
                return
                
            height, width = self.screen.getmaxyx()
            mid_h = height // 2
            
            # Clear screen
            self.screen.clear()
            
            # Update time for wave animation
            self.time += self.wave_speed
            
            # Get audio amplitude (average of channels)
            if self.n_channels > 1:
                amplitude = np.mean(np.abs(self.audio_data), axis=1)
            else:
                amplitude = np.abs(self.audio_data[:, 0])
                
            # Normalize and smooth the amplitude
            amplitude = np.convolve(amplitude, np.ones(5)/5, mode='same')
            max_amp = max(0.01, np.max(amplitude))
            amplitude = amplitude / max_amp
            
            # Draw the waveform
            points_per_col = len(amplitude) // width if width > 0 else 1
            if points_per_col < 1:
                points_per_col = 1
                
            for x in range(width):
                # Calculate wave height based on audio amplitude and sine wave
                idx_start = x * points_per_col
                idx_end = (x + 1) * points_per_col
                
                if idx_start >= len(amplitude):
                    break
                    
                idx_end = min(idx_end, len(amplitude))
                avg_amp = np.mean(amplitude[idx_start:idx_end])
                
                # Create a wave effect by combining audio amplitude with sine waves
                wave1 = math.sin(x * 0.1 + self.time) * self.wave_length * 0.3
                wave2 = math.sin(x * 0.05 - self.time * 1.5) * self.wave_length * 0.2
                wave3 = math.sin(x * 0.02 + self.time * 0.7) * self.wave_length * 0.1
                
                wave_height = (wave1 + wave2 + wave3) * (0.5 + avg_amp)
                
                # Scale by amplitude and screen height
                y_offset = int(wave_height * self.amplitude_scale)
                
                # Choose color based on amplitude
                color_idx = min(3, int(avg_amp * 4))
                attr = curses.color_pair(self.colors['wave'][color_idx])
                
                # Draw wave character
                y_pos = mid_h + y_offset
                if 0 <= y_pos < height and x < width - 1:
                    self.screen.addch(y_pos, x, '~', attr)
            
            # Draw info text
            info_text = f"nox audio visualizer | Press 'q' to quit"
            if len(info_text) < width:
                self.screen.addstr(0, 0, info_text, curses.color_pair(self.colors['text']))
                
            self.screen.refresh()
            
        except curses.error:
            # Ignore curses errors that might occur during resize
            pass
    
    def curses_main(self, stdscr):
        self.screen = stdscr
        
        # Set up curses
        curses.curs_set(0)  # Hide cursor
        stdscr.timeout(1000 // self.fps)  # Set refresh rate
        stdscr.clear()
        
        # Initialize colors
        self.init_colors()
        
        # Start audio capture
        self.start_audio_stream()
        
        # Main loop
        while self.running:
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    self.running = False
                    break
                    
                self.draw_wave()
                time.sleep(1.0 / self.fps)  # Cap the frame rate
                
            except KeyboardInterrupt:
                self.running = False
                break
    
    def run(self):
        # Set up signal handler for clean exit
        def signal_handler(sig, frame):
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            curses.wrapper(self.curses_main)
        finally:
            self.stop_audio_stream()
            print("Audio visualizer stopped.")

if __name__ == "__main__":
    visualizer = AudioWaveVisualizer()
    visualizer.run()
