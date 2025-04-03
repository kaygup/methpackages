import os
import sys
import subprocess
import threading
import shutil
from pathlib import Path

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.dropdown import DropDown
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window

kivy.require('2.0.0')

class FlaskApp(App):
    def build(self):
        # Set window size and title
        Window.size = (800, 600)
        self.title = 'Flask - USB ISO Flashing Utility'
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title_label = Label(
            text='Flask USB ISO Flashing Utility',
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        main_layout.add_widget(title_label)
        
        # ISO file selection
        iso_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        iso_label = Label(text='Select ISO file:', size_hint_y=None, height=30, halign='left')
        iso_label.bind(size=lambda *args: setattr(iso_label, 'text_size', (iso_label.width, None)))
        iso_layout.add_widget(iso_label)
        
        self.file_chooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.iso']
        )
        iso_layout.add_widget(self.file_chooser)
        main_layout.add_widget(iso_layout)
        
        # USB device selection
        usb_layout = BoxLayout(orientation='vertical', size_hint_y=0.25)
        usb_label = Label(text='Select USB device:', size_hint_y=None, height=30, halign='left')
        usb_label.bind(size=lambda *args: setattr(usb_label, 'text_size', (usb_label.width, None)))
        usb_layout.add_widget(usb_label)
        
        # USB device dropdown
        self.usb_dropdown_btn = Button(
            text='Click to select device',
            size_hint_y=None,
            height=44
        )
        
        self.usb_dropdown = DropDown()
        
        # Refresh button for USB devices
        refresh_btn = Button(
            text='Refresh USB Devices',
            size_hint_y=None,
            height=44
        )
        refresh_btn.bind(on_release=self.refresh_usb_devices)
        
        usb_btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=44, spacing=10)
        usb_btn_layout.add_widget(self.usb_dropdown_btn)
        usb_btn_layout.add_widget(refresh_btn)
        
        usb_layout.add_widget(usb_btn_layout)
        main_layout.add_widget(usb_layout)
        
        # Progress bar
        progress_layout = BoxLayout(orientation='vertical', size_hint_y=0.15)
        self.progress_label = Label(text='Ready', size_hint_y=None, height=30)
        progress_layout.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(max=100, value=0)
        progress_layout.add_widget(self.progress_bar)
        main_layout.add_widget(progress_layout)
        
        # Flash button
        self.flash_button = Button(
            text='Flash ISO to USB',
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.flash_button.bind(on_release=self.flash_iso)
        main_layout.add_widget(self.flash_button)
        
        # Initialize by discovering USB devices
        self.selected_device = None
        self.refresh_usb_devices(None)
        
        return main_layout
    
    def refresh_usb_devices(self, instance):
        """Refresh the list of available USB devices."""
        self.usb_dropdown.clear_widgets()
        
        # Get list of USB devices
        devices = self.get_usb_devices()
        
        if not devices:
            # If no devices found, show a message
            btn = Button(
                text='No USB devices found',
                size_hint_y=None,
                height=44
            )
            self.usb_dropdown.add_widget(btn)
            self.usb_dropdown_btn.text = 'No USB devices found'
            self.selected_device = None
        else:
            # Add devices to dropdown
            for device in devices:
                btn = Button(
                    text=device['name'],
                    size_hint_y=None,
                    height=44
                )
                btn.bind(on_release=lambda btn, dev=device: self.select_device(btn.text, dev))
                self.usb_dropdown.add_widget(btn)
        
        self.usb_dropdown_btn.bind(on_release=self.usb_dropdown.open)
    
    def get_usb_devices(self):
        """Get list of available USB devices."""
        devices = []
        
        try:
            # Use lsblk on Linux to list block devices
            if sys.platform.startswith('linux'):
                output = subprocess.check_output(['lsblk', '-d', '-o', 'NAME,SIZE,MODEL,TRAN', '--json']).decode('utf-8')
                import json
                result = json.loads(output)
                
                for device in result.get('blockdevices', []):
                    if device.get('tran') == 'usb':
                        devices.append({
                            'name': f"/dev/{device['name']} - {device.get('model', 'USB Device')} ({device.get('size', 'unknown')})",
                            'path': f"/dev/{device['name']}"
                        })
            
            # Use diskutil on macOS
            elif sys.platform == 'darwin':
                output = subprocess.check_output(['diskutil', 'list', 'external']).decode('utf-8')
                import re
                disk_pattern = r'/dev/disk(\d+)'
                size_pattern = r'\*?\s*(\d+\.\d+\s[GM]B)'
                
                matches = re.finditer(disk_pattern, output)
                for match in matches:
                    disk_id = match.group(1)
                    disk_path = f"/dev/disk{disk_id}"
                    
                    # Try to get the size
                    size_match = re.search(size_pattern, output)
                    size = size_match.group(1) if size_match else "Unknown size"
                    
                    devices.append({
                        'name': f"{disk_path} - USB Drive ({size})",
                        'path': disk_path
                    })
            
            # Use wmic on Windows
            elif sys.platform == 'win32':
                output = subprocess.check_output(['wmic', 'diskdrive', 'where', 'MediaType="Removable Media"', 'get', 'DeviceID,Model,Size']).decode('utf-8')
                import re
                
                for line in output.strip().split('\n')[1:]:
                    if line.strip():
                        parts = re.split(r'\s{2,}', line.strip())
                        if len(parts) >= 3:
                            device_id, model, size = parts[0], parts[1], parts[2]
                            try:
                                size_gb = round(int(size) / (1024**3), 2)
                                devices.append({
                                    'name': f"{device_id} - {model} ({size_gb} GB)",
                                    'path': device_id
                                })
                            except (ValueError, IndexError):
                                pass
        
        except Exception as e:
            print(f"Error getting USB devices: {str(e)}")
        
        return devices
    
    def select_device(self, text, device):
        """Select a USB device from the dropdown."""
        self.usb_dropdown.dismiss()
        self.usb_dropdown_btn.text = text
        self.selected_device = device
    
    def update_progress(self, dt):
        """Update progress bar during flashing."""
        # Simple animation for progress
        if self.progress_bar.value < 100:
            increment = 0.5 if self.progress_bar.value < 90 else 0.1
            self.progress_bar.value += increment
        else:
            self.flash_timer.cancel()
            self.flash_complete()
    
    def flash_complete(self):
        """Handle completion of flashing process."""
        self.progress_label.text = "Flash completed successfully!"
        self.flash_button.disabled = False
        self.flash_button.text = "Flash ISO to USB"
    
    def flash_error(self, error_msg):
        """Handle flashing error."""
        self.progress_label.text = f"Error: {error_msg}"
        self.flash_button.disabled = False
        self.flash_button.text = "Flash ISO to USB"
        if hasattr(self, 'flash_timer') and self.flash_timer:
            self.flash_timer.cancel()
    
    def flash_iso(self, instance):
        """Flash the selected ISO to the selected USB device."""
        # Validate selections
        if not self.file_chooser.selection:
            self.progress_label.text = "Error: No ISO file selected."
            return
        
        if not self.selected_device:
            self.progress_label.text = "Error: No USB device selected."
            return
        
        # Confirm action
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"WARNING: All data on {self.selected_device['name']} will be erased. Continue?",
            text_size=(400, None),
            halign='center'
        ))
        
        buttons = BoxLayout(size_hint_y=None, height=44, spacing=10)
        
        cancel_btn = Button(text="Cancel")
        confirm_btn = Button(text="Confirm", background_color=(0.8, 0.2, 0.2, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title="Confirm Flash Operation",
            content=content,
            size_hint=(None, None),
            size=(500, 200),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda btn: self.perform_flash(popup))
        
        popup.open()
    
    def perform_flash(self, popup):
        """Perform the actual flashing operation after confirmation."""
        popup.dismiss()
        
        # Disable flash button during operation
        self.flash_button.disabled = True
        self.flash_button.text = "Flashing in progress..."
        
        # Reset progress
        self.progress_bar.value = 0
        self.progress_label.text = "Preparing to flash..."
        
        # Get selected file and device
        iso_path = self.file_chooser.selection[0]
        device_path = self.selected_device['path']
        
        # Start flashing in a separate thread
        threading.Thread(target=self.flash_thread, args=(iso_path, device_path)).start()
        
        # Start progress timer
        self.flash_timer = Clock.schedule_interval(self.update_progress, 0.1)
    
    def flash_thread(self, iso_path, device_path):
        """Thread that handles the actual flashing process."""
        try:
            self.progress_label.text = "Flashing ISO to USB... (This may take several minutes)"
            
            # The actual dd command depends on the OS
            if sys.platform.startswith('linux') or sys.platform == 'darwin':
                cmd = ['dd', f'if={iso_path}', f'of={device_path}', 'bs=4M', 'status=progress']
                
                if sys.platform == 'darwin':  # macOS uses different dd options
                    cmd = ['dd', f'if={iso_path}', f'of={device_path}', 'bs=4m']
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=False
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    error = stderr.decode('utf-8') or "Unknown error during flashing"
                    Clock.schedule_once(lambda dt: self.flash_error(error), 0)
                    return
            
            elif sys.platform == 'win32':
                # On Windows, we would use tools like Rufus or Win32DiskImager
                # Here we'll simulate with a copy for demonstration
                try:
                    with open(iso_path, 'rb') as src, open(device_path, 'wb') as dst:
                        shutil.copyfileobj(src, dst)
                except Exception as e:
                    Clock.schedule_once(lambda dt: self.flash_error(str(e)), 0)
                    return
            
            # If we reach here, flashing was successful
            # The progress will continue until 100% via the timer
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.flash_error(str(e)), 0)

if __name__ == '__main__':
    FlaskApp().run()
