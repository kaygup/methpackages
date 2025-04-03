#!/usr/bin/env python3
"""
NOX - Volume Control Application
A simple Kivy-based volume control application for desktop systems.
"""

import os
import subprocess
import platform
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock

class VolumeControl:
    """Handles system volume operations across different platforms."""
    
    @staticmethod
    def get_current_volume():
        """Get the current system volume level (0-100)."""
        system = platform.system()
        
        if system == "Linux":
            try:
                output = subprocess.check_output(["amixer", "sget", "Master"]).decode()
                volume = int(output.split("[")[1].split("%")[0])
                return volume
            except Exception:
                return 50
        
        elif system == "Darwin":  # macOS
            try:
                output = subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"]).decode()
                return int(output.strip())
            except Exception:
                return 50
                
        elif system == "Windows":
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Convert from logarithmic scale to percentage
                return int(volume.GetMasterVolumeLevelScalar() * 100)
            except Exception:
                return 50
        
        return 50  # Default fallback
    
    @staticmethod
    def set_volume(value):
        """Set system volume (0-100)."""
        system = platform.system()
        
        if system == "Linux":
            try:
                subprocess.call(["amixer", "-q", "sset", "Master", f"{value}%"])
                return True
            except Exception:
                return False
                
        elif system == "Darwin":  # macOS
            try:
                subprocess.call(["osascript", "-e", f"set volume output volume {value}"])
                return True
            except Exception:
                return False
                
        elif system == "Windows":
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Convert percentage to logarithmic scale
                volume.SetMasterVolumeLevelScalar(value / 100, None)
                return True
            except Exception:
                return False
                
        return False  # Could not set volume

    @staticmethod
    def toggle_mute():
        """Toggle mute state."""
        system = platform.system()
        
        if system == "Linux":
            try:
                subprocess.call(["amixer", "-q", "set", "Master", "toggle"])
                return True
            except Exception:
                return False
                
        elif system == "Darwin":  # macOS
            try:
                current_mute = subprocess.check_output(["osascript", "-e", 
                    "output muted of (get volume settings)"]).decode().strip()
                
                if current_mute == "false":
                    subprocess.call(["osascript", "-e", "set volume with output muted"])
                else:
                    subprocess.call(["osascript", "-e", "set volume without output muted"])
                return True
            except Exception:
                return False
                
        elif system == "Windows":
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                current_mute = volume.GetMute()
                volume.SetMute(not current_mute, None)
                return True
            except Exception:
                return False
                
        return False  # Could not toggle mute

class VolumeControlApp(App):
    def build(self):
        # Set window properties
        self.title = 'NOX Volume Control'
        Window.size = (400, 300)
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Add title label
        title_layout = BoxLayout(size_hint_y=0.2)
        title_label = Label(
            text='NOX Volume Control',
            font_size='24sp',
            bold=True,
            color=(0.9, 0.9, 0.9, 1)
        )
        title_layout.add_widget(title_label)
        layout.add_widget(title_layout)
        
        # Volume slider
        slider_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        # Volume icon
        volume_icon = Image(
            source='',  # No source needed, we'll draw it programmatically
            size_hint_x=0.15
        )
        slider_layout.add_widget(volume_icon)
        
        # Slider
        self.volume_slider = Slider(
            min=0,
            max=100,
            value=VolumeControl.get_current_volume(),
            step=1,
            cursor_size=(20, 20),
            size_hint_x=0.7
        )
        self.volume_slider.bind(value=self.on_volume_change)
        slider_layout.add_widget(self.volume_slider)
        
        # Volume percentage label
        self.volume_label = Label(
            text=f"{int(self.volume_slider.value)}%",
            size_hint_x=0.15,
            font_size='18sp'
        )
        slider_layout.add_widget(self.volume_label)
        layout.add_widget(slider_layout)
        
        # Buttons layout
        buttons_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        # Mute toggle button
        self.mute_button = Button(
            text="Mute",
            background_color=(0.8, 0.2, 0.2, 1),
            background_normal='',
            bold=True
        )
        self.mute_button.bind(on_release=self.toggle_mute)
        buttons_layout.add_widget(self.mute_button)
        
        # Quick volume buttons
        for vol in [0, 25, 50, 75, 100]:
            btn = Button(
                text=f"{vol}%",
                background_color=(0.2, 0.4, 0.8, 1),
                background_normal='',
                bold=True
            )
            btn.bind(on_release=lambda instance, v=vol: self.set_quick_volume(v))
            buttons_layout.add_widget(btn)
        
        layout.add_widget(buttons_layout)
        
        # System info
        system_info = Label(
            text=f"System: {platform.system()} {platform.release()}",
            size_hint_y=0.1,
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(system_info)
        
        # Schedule periodic volume updates
        Clock.schedule_interval(self.update_volume_display, 1)
        
        return layout
    
    def on_volume_change(self, instance, value):
        """Handle volume slider changes."""
        volume = int(value)
        VolumeControl.set_volume(volume)
        self.volume_label.text = f"{volume}%"
    
    def set_quick_volume(self, volume):
        """Set volume to a specific level quickly."""
        self.volume_slider.value = volume
        VolumeControl.set_volume(volume)
        self.volume_label.text = f"{volume}%"
    
    def toggle_mute(self, instance):
        """Toggle mute state."""
        VolumeControl.toggle_mute()
        # Update the UI after a slight delay to reflect system state
        Clock.schedule_once(self.update_volume_display, 0.1)
    
    def update_volume_display(self, dt):
        """Update the volume display to match system volume."""
        current_volume = VolumeControl.get_current_volume()
        if int(self.volume_slider.value) != current_volume:
            self.volume_slider.value = current_volume
            self.volume_label.text = f"{current_volume}%"

if __name__ == '__main__':
    VolumeControlApp().run()
