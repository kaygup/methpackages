#!/usr/bin/env python3
import os
import sys
import threading
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window

class FlaskApp(App):
    def build(self):
        # Set window properties
        Window.size = (800, 600)
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.title = 'Flask - USB ISO Flasher'
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title_label = Label(
            text='Flask USB ISO Flasher',
            font_size=24,
            size_hint=(1, 0.1)
        )
        self.main_layout.add_widget(title_label)
        
        # File selection
        file_label = Label(
            text='Select ISO File:',
            size_hint=(1, 0.05),
            halign='left'
        )
        file_label.bind(size=self._update_label_text_size)
        self.main_layout.add_widget(file_label)
        
        self.file_chooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.iso'],
            size_hint=(1, 0.4)
        )
        self.main_layout.add_widget(self.file_chooser)
        
        # USB device selection
        usb_label = Label(
            text='Select USB Device:',
            size_hint=(1, 0.05),
            halign='left'
        )
        usb_label.bind(size=self._update_label_text_size)
        self.main_layout.add_widget(usb_label)
        
        self.usb_spinner = Spinner(
            text='Select USB Drive',
            values=self._get_usb_devices(),
            size_hint=(1, 0.1)
        )
        self.main_layout.add_widget(self.usb_spinner)
        
        # Refresh button for USB devices
        refresh_button = Button(
            text='Refresh USB Devices',
            size_hint=(1, 0.1)
        )
        refresh_button.bind(on_press=self._refresh_usb_devices)
        self.main_layout.add_widget(refresh_button)
        
        # Progress bar
        self.progress_label = Label(
            text='Ready',
            size_hint=(1, 0.05)
        )
        self.main_layout.add_widget(self.progress_label)
        
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 0.05)
        )
        self.main_layout.add_widget(self.progress_bar)
        
        # Flash button
        self.flash_button = Button(
            text='Flash ISO to USB',
            size_hint=(1, 0.1),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.flash_button.bind(on_press=self._flash_iso)
        self.main_layout.add_widget(self.flash_button)
        
        return self.main_layout
    
    def _update_label_text_size(self, instance, value):
        instance.text_size = (value[0], None)
    
    def _get_usb_devices(self):
        devices = []
        try:
            if sys.platform == 'linux':
                result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,MODEL', '-n'], 
                                       capture_output=True, text=True)
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if parts[0].startswith('sd'):
                            name = '/dev/' + parts[0]
                            size = parts[1]
                            model = ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown'
                            devices.append(f"{name} ({size}, {model})")
            elif sys.platform == 'darwin':  # macOS
                result = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if '/dev/disk' in line and 'external' in line.lower():
                        disk_id = line.split()[0]
                        devices.append(disk_id)
            elif sys.platform == 'win32':  # Windows
                # Simplified for this example
                import win32api
                drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
                for drive in drives:
                    if win32api.GetDriveType(drive) == win32api.DRIVE_REMOVABLE:
                        devices.append(drive)
        except Exception as e:
            print(f"Error getting USB devices: {e}")
        
        return devices if devices else ['No USB devices found']
    
    def _refresh_usb_devices(self, instance):
        self.usb_spinner.values = self._get_usb_devices()
        self.usb_spinner.text = 'Select USB Drive'
    
    def _flash_iso(self, instance):
        if not self.file_chooser.selection or not self.usb_spinner.text or self.usb_spinner.text == 'Select USB Drive' or self.usb_spinner.text == 'No USB devices found':
            self.progress_label.text = 'Error: Please select both ISO file and USB device'
            return
        
        iso_path = self.file_chooser.selection[0]
        usb_device = self.usb_spinner.text.split()[0]  # Extract device path
        
        # Confirm before flashing
        confirm_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        confirm_layout.add_widget(Label(text=f'Warning: This will erase all data on {usb_device}!\nContinue?'))
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.3))
        
        def cancel_callback(instance):
            self.main_layout.remove_widget(confirm_layout)
            self.progress_label.text = 'Operation cancelled'
        
        def proceed_callback(instance):
            self.main_layout.remove_widget(confirm_layout)
            self._start_flashing(iso_path, usb_device)
        
        cancel_button = Button(text='Cancel', background_color=(0.3, 0.3, 0.3, 1))
        cancel_button.bind(on_press=cancel_callback)
        
        proceed_button = Button(text='Proceed', background_color=(0.8, 0.2, 0.2, 1))
        proceed_button.bind(on_press=proceed_callback)
        
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(proceed_button)
        confirm_layout.add_widget(button_layout)
        
        self.main_layout.add_widget(confirm_layout)
    
    def _start_flashing(self, iso_path, usb_device):
        self.flash_button.disabled = True
        self.progress_label.text = 'Flashing in progress... Do not remove USB device!'
        self.progress_bar.value = 0
        
        # Start flashing in a separate thread
        threading.Thread(target=self._flash_process, args=(iso_path, usb_device)).start()
    
    def _flash_process(self, iso_path, usb_device):
        try:
            # Get file size for progress calculation
            file_size = os.path.getsize(iso_path)
            
            # Command for different platforms
            if sys.platform == 'linux' or sys.platform == 'darwin':
                cmd = ['dd', f'if={iso_path}', f'of={usb_device}', 'bs=4M', 'status=progress']
            elif sys.platform == 'win32':
                # Windows would use different tools like PowerShell
                # Simplified for this example
                from shutil import copyfile
                copyfile(iso_path, usb_device)
                Clock.schedule_once(lambda dt: self._update_progress(100), 0)
                Clock.schedule_once(lambda dt: self._flash_completed(), 0)
                return
            
            # Execute dd command and capture output for progress
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            # Monitor the process
            while process.poll() is None:
                output = process.stderr.readline()
                if 'bytes' in output:
                    try:
                        transferred = int(output.split()[0])
                        progress = min(100, int((transferred / file_size) * 100))
                        Clock.schedule_once(lambda dt, p=progress: self._update_progress(p), 0)
                    except:
                        pass
            
            if process.returncode == 0:
                Clock.schedule_once(lambda dt: self._flash_completed(), 0)
            else:
                Clock.schedule_once(lambda dt: self._flash_failed(), 0)
                
        except Exception as e:
            Clock.schedule_once(lambda dt, error=str(e): self._flash_error(error), 0)
    
    def _update_progress(self, progress):
        self.progress_bar.value = progress
        self.progress_label.text = f'Progress: {progress}%'
    
    def _flash_completed(self):
        self.progress_bar.value = 100
        self.progress_label.text = 'Flashing completed successfully!'
        self.flash_button.disabled = False
    
    def _flash_failed(self):
        self.progress_label.text = 'Flashing failed!'
        self.flash_button.disabled = False
    
    def _flash_error(self, error):
        self.progress_label.text = f'Error: {error}'
        self.flash_button.disabled = False

if __name__ == '__main__':
    FlaskApp().run()
