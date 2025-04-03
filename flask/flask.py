#!/usr/bin/env python3
"""
Flask - USB ISO Flashing Utility
A simple GUI application for flashing ISO images to USB drives
"""

import os
import sys
import subprocess
import threading
import time
from functools import partial

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.filechooser import FileChooserListView
    from kivy.uix.dropdown import DropDown
    from kivy.uix.progressbar import ProgressBar
    from kivy.clock import Clock
    from kivy.core.window import Window
except ImportError:
    print("Kivy is not installed. Please install it with:")
    print("pip install kivy")
    sys.exit(1)

class FlaskApp(App):
    def __init__(self, **kwargs):
        super(FlaskApp, self).__init__(**kwargs)
        self.title = 'Flask - ISO to USB Flasher'
        self.selected_iso = None
        self.selected_device = None
        self.flashing_thread = None
        self.devices_list = []
        Window.size = (800, 600)
        
    def build(self):
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title_label = Label(
            text='Flask - ISO to USB Flasher',
            font_size=24,
            size_hint_y=None,
            height=50
        )
        self.main_layout.add_widget(title_label)
        
        # Status label
        self.status_label = Label(
            text='Select an ISO file and USB device to begin',
            font_size=16,
            size_hint_y=None,
            height=30
        )
        self.main_layout.add_widget(self.status_label)
        
        # File chooser for ISO
        self.file_chooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.iso']
        )
        self.file_chooser.bind(on_submit=self.select_iso)
        self.file_chooser.bind(selection=self.on_selection)
        self.main_layout.add_widget(self.file_chooser)
        
        # Selected ISO display
        self.iso_label = Label(
            text='No ISO selected',
            size_hint_y=None,
            height=30
        )
        self.main_layout.add_widget(self.iso_label)
        
        # Device selection dropdown
        device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        device_label = Label(text='Select USB Device:', size_hint_x=0.3)
        device_layout.add_widget(device_label)
        
        self.device_button = Button(text='Select USB Device', size_hint_x=0.7)
        self.device_dropdown = DropDown()
        self.device_button.bind(on_release=self.device_dropdown.open)
        self.device_dropdown.bind(on_select=lambda instance, x: self.select_device(x))
        device_layout.add_widget(self.device_button)
        
        self.main_layout.add_widget(device_layout)
        
        # Refresh devices button
        refresh_button = Button(
            text='Refresh USB Devices',
            size_hint_y=None,
            height=50
        )
        refresh_button.bind(on_release=self.refresh_devices)
        self.main_layout.add_widget(refresh_button)
        
        # Progress bar
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=30)
        self.main_layout.add_widget(self.progress_bar)
        
        # Flash button
        self.flash_button = Button(
            text='Flash ISO to USB',
            size_hint_y=None,
            height=70,
            background_color=(0.8, 0.2, 0.2, 1),
            disabled=True
        )
        self.flash_button.bind(on_release=self.start_flashing)
        self.main_layout.add_widget(self.flash_button)
        
        # Initialize the device list
        self.refresh_devices(None)
        
        return self.main_layout
    
    def on_selection(self, fileChooser, selection):
        if selection:
            self.selected_iso = selection[0]
            self.iso_label.text = f'Selected ISO: {os.path.basename(self.selected_iso)}'
            self.update_flash_button()
    
    def select_iso(self, fileChooser, selection, touch):
        self.selected_iso = selection[0]
        self.iso_label.text = f'Selected ISO: {os.path.basename(self.selected_iso)}'
        self.update_flash_button()
    
    def refresh_devices(self, instance):
        self.status_label.text = "Refreshing USB devices..."
        self.device_dropdown.clear_widgets()
        self.devices_list = []
        
        # Get list of devices - This is OS-dependent
        if sys.platform.startswith('linux'):
            # Using lsblk on Linux to list only removable block devices
            try:
                output = subprocess.check_output(
                    ['lsblk', '-d', '-o', 'NAME,SIZE,MODEL,RM', '--json'],
                    universal_newlines=True
                )
                import json
                devices = json.loads(output)
                
                for device in devices['blockdevices']:
                    # Only show removable devices (RM=1)
                    if device.get('rm') == "1":
                        device_path = f"/dev/{device['name']}"
                        display_name = f"{device['name']} - {device.get('size', 'Unknown')} - {device.get('model', 'Unknown')}"
                        self.devices_list.append((device_path, display_name))
            except Exception as e:
                self.status_label.text = f"Error listing devices: {str(e)}"
        
        elif sys.platform == 'darwin':  # macOS
            try:
                # List mounted volumes
                output = subprocess.check_output(
                    ['diskutil', 'list', 'external', 'physical'],
                    universal_newlines=True
                )
                
                # Parse the output
                current_disk = None
                for line in output.splitlines():
                    if line.startswith("/dev/"):
                        current_disk = line.split()[0]
                    elif "removable" in line.lower() and current_disk:
                        size = line.split()[2:4]
                        size_str = " ".join(size)
                        display_name = f"{current_disk} - {size_str}"
                        self.devices_list.append((current_disk, display_name))
            except Exception as e:
                self.status_label.text = f"Error listing devices: {str(e)}"
                
        elif sys.platform == 'win32':  # Windows
            try:
                # Use wmic to get the list of drives
                output = subprocess.check_output(
                    ['wmic', 'diskdrive', 'get', 'DeviceID,Size,Model,MediaType'],
                    universal_newlines=True
                )
                
                for line in output.splitlines()[1:]:  # Skip header
                    if line.strip() and "removable" in line.lower():
                        parts = line.split()
                        if len(parts) >= 3:
                            device_id = parts[0]
                            size = parts[1]
                            model = " ".join(parts[2:-1])
                            display_name = f"{device_id} - {int(size)/(1024**3):.1f} GB - {model}"
                            self.devices_list.append((device_id, display_name))
            except Exception as e:
                self.status_label.text = f"Error listing devices: {str(e)}"
        
        # Add devices to dropdown
        if self.devices_list:
            for device_path, display_name in self.devices_list:
                btn = Button(text=display_name, size_hint_y=None, height=44)
                btn.bind(on_release=lambda btn, dev=device_path, name=display_name: 
                         self.device_dropdown.select((dev, name)))
                self.device_dropdown.add_widget(btn)
            self.status_label.text = f"Found {len(self.devices_list)} USB devices"
        else:
            self.device_button.text = 'No USB devices found'
            self.status_label.text = "No USB devices found. Try refreshing."
            self.selected_device = None
            self.update_flash_button()
    
    def select_device(self, device_tuple):
        self.selected_device = device_tuple[0]  # Path to the device
        self.device_button.text = device_tuple[1]  # Display name
        self.update_flash_button()
    
    def update_flash_button(self):
        self.flash_button.disabled = not (self.selected_iso and self.selected_device)
    
    def start_flashing(self, instance):
        if not self.selected_iso or not self.selected_device:
            self.status_label.text = "Please select both an ISO file and a USB device"
            return
        
        # Confirm before flashing
        import kivy.uix.popup as popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"WARNING: You are about to erase all data on\n{self.device_button.text}\n\nThis cannot be undone!"))
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        cancel_button = Button(text='Cancel')
        confirm_button = Button(text='Proceed', background_color=(1, 0, 0, 1))
        
        buttons.add_widget(cancel_button)
        buttons.add_widget(confirm_button)
        content.add_widget(buttons)
        
        popup_window = popup.Popup(title='Confirm Flash Operation', 
                                  content=content,
                                  size_hint=(0.8, 0.4))
        
        cancel_button.bind(on_release=popup_window.dismiss)
        confirm_button.bind(on_release=lambda x: self.confirm_flash(popup_window))
        
        popup_window.open()
    
    def confirm_flash(self, popup_window):
        popup_window.dismiss()
        
        # Disable UI elements during flashing
        self.flash_button.disabled = True
        self.file_chooser.disabled = True
        self.device_button.disabled = True
        
        # Reset progress bar
        self.progress_bar.value = 0
        
        # Start flashing in a separate thread
        self.status_label.text = "Starting flash operation..."
        self.flashing_thread = threading.Thread(target=self.flash_iso)
        self.flashing_thread.daemon = True
        self.flashing_thread.start()
        
        # Start progress polling
        Clock.schedule_interval(self.update_progress, 0.5)
    
    def flash_iso(self):
        try:
            # This command varies by OS
            if sys.platform.startswith('linux'):
                cmd = ['dd', 'if=' + self.selected_iso, 'of=' + self.selected_device, 
                       'bs=4M', 'status=progress', 'conv=fsync']
                
                # Open a status file to monitor progress
                self.status_file = open('/tmp/flask_progress', 'w+')
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                
                # Get the total size of the ISO
                iso_size = os.path.getsize(self.selected_iso)
                
                for line in iter(process.stdout.readline, ''):
                    if 'bytes' in line:
                        try:
                            bytes_written = int(line.split()[0])
                            progress = (bytes_written / iso_size) * 100
                            # Write progress to the status file
                            self.status_file.seek(0)
                            self.status_file.write(str(progress))
                            self.status_file.flush()
                        except:
                            pass
                
                process.wait()
                return_code = process.returncode
                
            elif sys.platform == 'darwin':  # macOS
                # Unmount the device first
                subprocess.run(['diskutil', 'unmountDisk', self.selected_device])
                
                # Get ISO size
                iso_size = os.path.getsize(self.selected_iso)
                self.status_file = open('/tmp/flask_progress', 'w+')
                
                # Use dd for macOS
                cmd = ['dd', 'if=' + self.selected_iso, 'of=' + self.selected_device, 'bs=1m']
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
                
                # MacOS dd doesn't show progress, so we'll use a separate method
                start_time = time.time()
                while process.poll() is None:
                    # Check progress by seeing how much has been written
                    # This is not perfect but gives a rough estimate
                    try:
                        disk_info = subprocess.check_output(
                            ['diskutil', 'info', self.selected_device],
                            universal_newlines=True
                        )
                        
                        # Estimate progress based on time elapsed
                        elapsed = time.time() - start_time
                        estimated_bytes = min(elapsed * 10 * 1024 * 1024, iso_size)  # Assume ~10MB/s
                        progress = (estimated_bytes / iso_size) * 100
                        
                        self.status_file.seek(0)
                        self.status_file.write(str(progress))
                        self.status_file.flush()
                    except:
                        pass
                    
                    time.sleep(1)
                    
                return_code = process.returncode
                
            elif sys.platform == 'win32':  # Windows
                # On Windows, we'll use a third-party tool like dd for Windows
                # For this example, we'll assume dd for Windows is installed
                iso_size = os.path.getsize(self.selected_iso)
                self.status_file = open('C:\\temp\\flask_progress.txt', 'w+')
                
                # This is just an example - would need proper dd for Windows
                cmd = ['dd', 'if=' + self.selected_iso, 'of=' + self.selected_device, 'bs=4M']
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
                
                # Similar to macOS approach for progress estimation
                start_time = time.time()
                while process.poll() is None:
                    elapsed = time.time() - start_time
                    estimated_bytes = min(elapsed * 10 * 1024 * 1024, iso_size)
                    progress = (estimated_bytes / iso_size) * 100
                    
                    self.status_file.seek(0)
                    self.status_file.write(str(progress))
                    self.status_file.flush()
                    time.sleep(1)
                    
                return_code = process.returncode
            
            # Check return code
            if return_code == 0:
                Clock.schedule_once(lambda dt: self.flash_completed(), 0)
            else:
                Clock.schedule_once(lambda dt: self.flash_error(f"Flash failed with error code {return_code}"), 0)
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self.flash_error(str(e)), 0)
        finally:
            if hasattr(self, 'status_file'):
                self.status_file.close()
    
    def update_progress(self, dt):
        if not self.flashing_thread or not self.flashing_thread.is_alive():
            return False
        
        try:
            if hasattr(self, 'status_file'):
                self.status_file.seek(0)
                progress_str = self.status_file.read().strip()
                if progress_str:
                    progress = float(progress_str)
                    self.progress_bar.value = progress
                    self.status_label.text = f"Flashing: {progress:.1f}% complete"
        except:
            pass
        
        return True
    
    def flash_completed(self):
        self.status_label.text = "Flash completed successfully!"
        self.progress_bar.value = 100
        self.reset_ui()
        
        # Show completion popup
        from kivy.uix.popup import Popup
        popup = Popup(title='Flash Completed',
                     content=Label(text='ISO has been successfully flashed to the USB device.'),
                     size_hint=(0.7, 0.3))
        popup.open()
    
    def flash_error(self, error_msg):
        self.status_label.text = f"Error: {error_msg}"
        self.reset_ui()
        
        # Show error popup
        from kivy.uix.popup import Popup
        popup = Popup(title='Flash Error',
                     content=Label(text=error_msg),
                     size_hint=(0.7, 0.3))
        popup.open()
    
    def reset_ui(self):
        self.flash_button.disabled = False
        self.file_chooser.disabled = False
        self.device_button.disabled = False

if __name__ == '__main__':
    FlaskApp().run()
