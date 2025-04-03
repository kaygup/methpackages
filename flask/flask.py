import os
import sys
import threading
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup

class FlaskApp(App):
    def build(self):
        # Set window properties
        Window.size = (800, 600)
        Window.minimum_width, Window.minimum_height = 700, 500
        self.title = 'Flask - USB ISO Flasher'
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title_label = Label(
            text="Flask USB ISO Flasher",
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        main_layout.add_widget(title_label)
        
        # File selection layout
        file_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        file_label = Label(text="Select ISO file:", size_hint_y=None, height=30, halign='left')
        file_label.bind(size=lambda s, w: setattr(file_label, 'text_size', w))
        file_layout.add_widget(file_label)
        
        self.file_chooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=['*.iso']
        )
        file_layout.add_widget(self.file_chooser)
        main_layout.add_widget(file_layout)
        
        # USB device selection layout
        usb_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        usb_label = Label(text="Select USB device:", size_hint_x=0.3)
        self.usb_spinner = Spinner(text='No devices found', values=[])
        refresh_button = Button(text="Refresh", size_hint_x=0.2)
        refresh_button.bind(on_release=self.refresh_usb_devices)
        
        usb_layout.add_widget(usb_label)
        usb_layout.add_widget(self.usb_spinner)
        usb_layout.add_widget(refresh_button)
        main_layout.add_widget(usb_layout)
        
        # Progress layout
        progress_layout = BoxLayout(orientation='vertical', size_hint_y=0.2)
        self.progress_label = Label(text="Ready", halign='left')
        self.progress_label.bind(size=lambda s, w: setattr(self.progress_label, 'text_size', w))
        self.progress_bar = ProgressBar(max=100, value=0)
        
        progress_layout.add_widget(self.progress_label)
        progress_layout.add_widget(self.progress_bar)
        main_layout.add_widget(progress_layout)
        
        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        flash_button = Button(text="Flash ISO", background_color=(0.2, 0.7, 0.2, 1))
        flash_button.bind(on_release=self.flash_iso)
        cancel_button = Button(text="Exit", background_color=(0.7, 0.2, 0.2, 1))
        cancel_button.bind(on_release=self.exit_app)
        
        button_layout.add_widget(flash_button)
        button_layout.add_widget(cancel_button)
        main_layout.add_widget(button_layout)
        
        # Initialize USB device list
        self.refresh_usb_devices()
        
        return main_layout
    
    def refresh_usb_devices(self, instance=None):
        self.progress_label.text = "Scanning for USB devices..."
        threading.Thread(target=self._get_usb_devices).start()
    
    def _get_usb_devices(self):
        try:
            # For Linux
            if sys.platform.startswith('linux'):
                cmd = "lsblk -d -o NAME,SIZE,MODEL,TRAN | grep 'usb'"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                devices = []
                for line in output.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            size = parts[1]
                            model = ' '.join(parts[2:-1]) if len(parts) > 3 else "USB Device"
                            devices.append(f"/dev/{name} ({size}) - {model}")
            
            # For macOS
            elif sys.platform == 'darwin':
                cmd = "diskutil list | grep external"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                devices = []
                for line in output.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 1:
                            name = parts[0]
                            devices.append(f"{name} - External Device")
            
            # For Windows
            elif sys.platform == 'win32':
                cmd = "wmic diskdrive where MediaType='Removable Media' get DeviceID,Size,Model /format:list"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                devices = []
                current_device = {}
                for line in output.strip().split('\n'):
                    line = line.strip()
                    if not line:
                        if current_device and 'DeviceID' in current_device and 'Size' in current_device:
                            size_gb = int(current_device['Size']) / (1024**3)
                            model = current_device.get('Model', 'USB Device')
                            devices.append(f"{current_device['DeviceID']} ({size_gb:.1f} GB) - {model}")
                        current_device = {}
                    elif '=' in line:
                        key, value = line.split('=', 1)
                        current_device[key.strip()] = value.strip()
            
            else:
                devices = ["Unsupported platform"]
            
            # Update UI on the main thread
            Clock.schedule_once(lambda dt: self._update_device_list(devices), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._handle_device_scan_error(str(e)), 0)
    
    def _update_device_list(self, devices):
        if not devices:
            self.usb_spinner.text = "No USB devices found"
            self.usb_spinner.values = []
        else:
            self.usb_spinner.values = devices
            self.usb_spinner.text = devices[0]
        self.progress_label.text = f"Found {len(devices)} USB device(s)"
    
    def _handle_device_scan_error(self, error_msg):
        self.usb_spinner.text = "Error scanning devices"
        self.usb_spinner.values = []
        self.progress_label.text = f"Error: {error_msg}"
    
    def flash_iso(self, instance):
        selected_file = self.file_chooser.selection
        if not selected_file:
            self._show_error("Please select an ISO file first")
            return
        
        selected_device = self.usb_spinner.text
        if selected_device in ["No USB devices found", "No devices found", "Error scanning devices", "Unsupported platform"]:
            self._show_error("Please select a valid USB device")
            return
        
        # Extract the device path from the spinner text
        device_path = selected_device.split()[0]
        
        # Confirm flashing
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message = f"This will erase ALL data on {selected_device}.\nAre you sure you want to continue?"
        content.add_widget(Label(text=message))
        
        buttons = BoxLayout(size_hint_y=None, height=50)
        cancel_btn = Button(text="Cancel")
        proceed_btn = Button(text="Proceed", background_color=(0.8, 0.2, 0.2, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(proceed_btn)
        content.add_widget(buttons)
        
        popup = Popup(title="Warning", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        cancel_btn.bind(on_release=popup.dismiss)
        proceed_btn.bind(on_release=lambda btn: self._start_flashing(popup, selected_file[0], device_path))
        
        popup.open()
    
    def _start_flashing(self, popup, iso_path, device_path):
        popup.dismiss()
        self.progress_label.text = "Preparing to flash..."
        self.progress_bar.value = 0
        threading.Thread(target=self._flash_iso_thread, args=(iso_path, device_path)).start()
    
    def _flash_iso_thread(self, iso_path, device_path):
        try:
            # Command to flash ISO to USB
            if sys.platform.startswith('linux'):
                cmd = f"dd bs=4M if='{iso_path}' of='{device_path}' status=progress"
            elif sys.platform == 'darwin':
                cmd = f"dd bs=4m if='{iso_path}' of='{device_path}' status=progress"
            elif sys.platform == 'win32':
                # For Windows, we'll use PowerShell as dd is not natively available
                # This is a simple example and might not work perfectly
                cmd = f'powershell -command "Copy-Item -Path \'{iso_path}\' -Destination \'{device_path}\' -PassThru | ForEach-Object {{$_.PercentComplete}}"'
            else:
                Clock.schedule_once(lambda dt: self._update_progress("Unsupported platform", -1), 0)
                return

            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # For tracking progress
            total_size = os.path.getsize(iso_path)
            current_progress = 0
            
            for line in iter(process.stdout.readline, ''):
                # Try to parse progress from dd output
                if 'bytes transferred' in line:
                    try:
                        transferred = int(line.split('bytes transferred')[0].strip())
                        percent = min(100, int(transferred * 100 / total_size))
                        current_progress = percent
                    except:
                        pass
                
                # Update UI
                Clock.schedule_once(lambda dt, p=current_progress, m=line: self._update_progress(m, p), 0)
            
            # Wait for process to complete
            returncode = process.wait()
            
            if returncode == 0:
                Clock.schedule_once(lambda dt: self._update_progress("Flashing completed successfully!", 100), 0)
            else:
                Clock.schedule_once(lambda dt: self._update_progress("Error: Flashing failed with return code " + str(returncode), -1), 0)
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self._update_progress("Error: " + str(e), -1), 0)
    
    def _update_progress(self, message, percent):
        self.progress_label.text = message
        if percent >= 0:
            self.progress_bar.value = percent
    
    def _show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        button = Button(text="OK", size_hint_y=None, height=50)
        content.add_widget(button)
        
        popup = Popup(title="Error", content=content, size_hint=(0.7, 0.3), auto_dismiss=False)
        button.bind(on_release=popup.dismiss)
        popup.open()
    
    def exit_app(self, instance):
        App.get_running_app().stop()


if __name__ == "__main__":
    FlaskApp().run()
