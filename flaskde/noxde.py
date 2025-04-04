# noxde.py - Main desktop environment file
#!/usr/bin/env python3

import gi
import os
import subprocess
import sys
import threading
import json
import tempfile

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango

class NoxDE:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("NoxDE")
        self.window.set_default_size(1024, 768)
        self.window.connect("destroy", Gtk.main_quit)
        
        # Main layout container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(self.main_box)
        
        # Create top panel
        self.create_panel()
        
        # Create desktop area
        self.desktop_area = Gtk.Box()
        self.main_box.pack_start(self.desktop_area, True, True, 0)
        
        # Load desktop icons
        self.load_desktop_icons()
        
        # Connect right-click menu
        self.window.connect("button-press-event", self.on_desktop_click)
        
        # Show all widgets
        self.window.show_all()
    
    def create_panel(self):
        # Top panel
        self.panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.panel.get_style_context().add_class("panel")
        self.panel.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.2, 0.2, 0.2, 1))
        
        # Start menu button
        start_button = Gtk.Button(label="NoxDE")
        start_button.connect("clicked", self.on_start_menu)
        self.panel.pack_start(start_button, False, False, 0)
        
        # Clock 
        self.clock_label = Gtk.Label()
        self.update_clock()
        self.panel.pack_end(self.clock_label, False, False, 5)
        GLib.timeout_add(1000, self.update_clock)
        
        self.main_box.pack_start(self.panel, False, False, 0)
    
    def update_clock(self):
        current_time = subprocess.check_output(["date", "+%H:%M:%S"]).decode().strip()
        self.clock_label.set_text(current_time)
        return True
    
    def load_desktop_icons(self):
        desktop_icons = [
            {"name": "USB Creator", "icon": "drive-removable-media", "command": self.launch_usb_creator},
            {"name": "Flask2 Editor", "icon": "accessories-text-editor", "command": self.launch_flask2}
        ]
        
        icon_box = Gtk.FlowBox()
        icon_box.set_valign(Gtk.Align.START)
        icon_box.set_max_children_per_line(10)
        icon_box.set_selection_mode(Gtk.SelectionMode.NONE)
        
        for app in desktop_icons:
            icon = self.create_desktop_icon(app["name"], app["icon"], app["command"])
            icon_box.add(icon)
        
        self.desktop_area.pack_start(icon_box, True, True, 10)
    
    def create_desktop_icon(self, name, icon_name, command):
        button = Gtk.Button()
        button.connect("clicked", lambda x: command())
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        box.pack_start(icon, False, False, 0)
        
        # Label
        label = Gtk.Label(label=name)
        label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))
        box.pack_start(label, False, False, 0)
        
        button.add(box)
        return button
    
    def on_desktop_click(self, widget, event):
        if event.button == 3:  # Right click
            menu = Gtk.Menu()
            
            menu_items = [
                {"label": "New Terminal", "callback": self.launch_terminal},
                {"label": "USB Creator", "callback": self.launch_usb_creator},
                {"label": "Flask2 Editor", "callback": self.launch_flask2},
                {"label": "About", "callback": self.show_about},
                {"label": "Exit", "callback": Gtk.main_quit}
            ]
            
            for item in menu_items:
                menu_item = Gtk.MenuItem(label=item["label"])
                menu_item.connect("activate", lambda x, cb=item["callback"]: cb())
                menu.append(menu_item)
            
            menu.show_all()
            menu.popup_at_pointer(event)
    
    def on_start_menu(self, widget):
        menu = Gtk.Menu()
        
        menu_items = [
            {"label": "Terminal", "callback": self.launch_terminal},
            {"label": "USB Creator", "callback": self.launch_usb_creator},
            {"label": "Flask2 Editor", "callback": self.launch_flask2},
            {"label": "About", "callback": self.show_about},
            {"label": "Exit", "callback": Gtk.main_quit}
        ]
        
        for item in menu_items:
            menu_item = Gtk.MenuItem(label=item["label"])
            menu_item.connect("activate", lambda x, cb=item["callback"]: cb())
            menu.append(menu_item)
        
        menu.show_all()
        menu.popup_at_widget(widget, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)
    
    def launch_terminal(self):
        terminal_apps = ["x-terminal-emulator", "gnome-terminal", "xterm"]
        for term in terminal_apps:
            try:
                subprocess.Popen([term])
                return
            except FileNotFoundError:
                continue
    
    def launch_usb_creator(self):
        usb_creator = USBCreator()
        usb_creator.run()
    
    def launch_flask2(self):
        flask2 = Flask2Editor()
        flask2.run()
    
    def show_about(self):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_title("About NoxDE")
        about_dialog.set_program_name("NoxDE")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("A minimal desktop environment with USB creator and Flask2 editor")
        about_dialog.set_copyright("© 2025")
        about_dialog.run()
        about_dialog.destroy()


class USBCreator:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("USB Creator")
        self.window.set_default_size(500, 400)
        self.window.set_border_width(10)
        
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(self.main_box)
        
        # ISO selection
        iso_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        iso_label = Gtk.Label(label="ISO File:")
        iso_box.pack_start(iso_label, False, False, 0)
        
        self.iso_entry = Gtk.Entry()
        iso_box.pack_start(self.iso_entry, True, True, 0)
        
        iso_button = Gtk.Button(label="Browse")
        iso_button.connect("clicked", self.on_iso_browse)
        iso_box.pack_start(iso_button, False, False, 0)
        
        self.main_box.pack_start(iso_box, False, False, 0)
        
        # USB Drive selection
        usb_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        usb_label = Gtk.Label(label="USB Drive:")
        usb_box.pack_start(usb_label, False, False, 0)
        
        self.usb_combo = Gtk.ComboBoxText()
        self.refresh_usb_drives()
        usb_box.pack_start(self.usb_combo, True, True, 0)
        
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        usb_box.pack_start(refresh_button, False, False, 0)
        
        self.main_box.pack_start(usb_box, False, False, 0)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.main_box.pack_start(self.progress_bar, False, False, 0)
        
        # Status label
        self.status_label = Gtk.Label()
        self.main_box.pack_start(self.status_label, False, False, 0)
        
        # Create button
        create_button = Gtk.Button(label="Create Bootable USB")
        create_button.connect("clicked", self.on_create_clicked)
        self.main_box.pack_start(create_button, False, False, 0)
    
    def run(self):
        self.window.show_all()
    
    def refresh_usb_drives(self):
        self.usb_combo.remove_all()
        drives = self.get_usb_drives()
        for drive in drives:
            self.usb_combo.append_text(drive)
        if drives:
            self.usb_combo.set_active(0)
    
    def get_usb_drives(self):
        try:
            output = subprocess.check_output(["lsblk", "-J", "-o", "NAME,TYPE,SIZE,MOUNTPOINT"]).decode()
            data = json.loads(output)
            
            drives = []
            for device in data["blockdevices"]:
                if device["type"] == "disk" and not device["name"].startswith("loop") and not device["name"].startswith("sr"):
                    if device["name"].startswith("sd") or device["name"].startswith("nvme"):
                        drives.append(f"/dev/{device['name']} ({device.get('size', 'Unknown size')})")
            
            return drives
        except Exception as e:
            print(f"Error getting USB drives: {e}")
            return []
    
    def on_iso_browse(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select ISO File",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # Add file filter for ISO files
        filter_iso = Gtk.FileFilter()
        filter_iso.set_name("ISO files")
        filter_iso.add_pattern("*.iso")
        dialog.add_filter(filter_iso)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.iso_entry.set_text(dialog.get_filename())
        
        dialog.destroy()
    
    def on_refresh_clicked(self, button):
        self.refresh_usb_drives()
    
    def on_create_clicked(self, button):
        iso_file = self.iso_entry.get_text()
        usb_drive = self.usb_combo.get_active_text()
        
        if not iso_file or not usb_drive:
            self.status_label.set_text("Please select both ISO file and USB drive")
            return
        
        # Extract device path from combo box text
        usb_device = usb_drive.split()[0]
        
        # Confirm
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Warning: All data on {usb_drive} will be erased!"
        )
        dialog.format_secondary_text("Are you sure you want to continue?")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            threading.Thread(target=self.create_bootable_usb, args=(iso_file, usb_device)).start()
    
    def create_bootable_usb(self, iso_file, usb_device):
        try:
            # Update UI
            GLib.idle_add(self.status_label.set_text, "Creating bootable USB. Please wait...")
            
            # Use dd to create bootable USB
            process = subprocess.Popen(
                ["dd", f"if={iso_file}", f"of={usb_device}", "bs=4M", "status=progress"],
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Update progress (approximate)
            for i in range(10):
                GLib.idle_add(self.progress_bar.set_fraction, i/10)
                GLib.idle_add(self.progress_bar.set_text, f"{i*10}%")
                time.sleep(1)  # This is a simplified approach
            
            process.wait()
            
            if process.returncode == 0:
                GLib.idle_add(self.status_label.set_text, "Bootable USB created successfully!")
                GLib.idle_add(self.progress_bar.set_fraction, 1.0)
                GLib.idle_add(self.progress_bar.set_text, "100%")
            else:
                error = process.stderr.read()
                GLib.idle_add(self.status_label.set_text, f"Error: {error}")
        
        except Exception as e:
            GLib.idle_add(self.status_label.set_text, f"Error: {str(e)}")


class Flask2Editor:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_title("Flask2 Editor")
        self.window.set_default_size(800, 600)
        
        self.current_file = None
        
        # Main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(self.main_box)
        
        # Menu bar
        self.create_menu_bar()
        
        # Text editor
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        
        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        
        # Set monospace font
        font_desc = Pango.FontDescription("monospace 10")
        self.text_view.override_font(font_desc)
        
        self.text_buffer = self.text_view.get_buffer()
        
        scrolled_window.add(self.text_view)
        self.main_box.pack_start(scrolled_window, True, True, 0)
        
        # Status bar
        self.status_bar = Gtk.Statusbar()
        self.status_bar_context = self.status_bar.get_context_id("main")
        self.main_box.pack_start(self.status_bar, False, False, 0)
        
        # Update status when text changes
        self.text_buffer.connect("changed", self.update_status_bar)
    
    def create_menu_bar(self):
        menu_bar = Gtk.MenuBar()
        
        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        
        new_item = Gtk.MenuItem(label="New")
        new_item.connect("activate", self.on_new)
        file_menu.append(new_item)
        
        open_item = Gtk.MenuItem(label="Open")
        open_item.connect("activate", self.on_open)
        file_menu.append(open_item)
        
        save_item = Gtk.MenuItem(label="Save")
        save_item.connect("activate", self.on_save)
        file_menu.append(save_item)
        
        save_as_item = Gtk.MenuItem(label="Save As")
        save_as_item.connect("activate", self.on_save_as)
        file_menu.append(save_as_item)
        
        separator = Gtk.SeparatorMenuItem()
        file_menu.append(separator)
        
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        file_menu.append(quit_item)
        
        # Edit menu
        edit_menu = Gtk.Menu()
        edit_item = Gtk.MenuItem(label="Edit")
        edit_item.set_submenu(edit_menu)
        
        cut_item = Gtk.MenuItem(label="Cut")
        cut_item.connect("activate", self.on_cut)
        edit_menu.append(cut_item)
        
        copy_item = Gtk.MenuItem(label="Copy")
        copy_item.connect("activate", self.on_copy)
        edit_menu.append(copy_item)
        
        paste_item = Gtk.MenuItem(label="Paste")
        paste_item.connect("activate", self.on_paste)
        edit_menu.append(paste_item)
        
        separator = Gtk.SeparatorMenuItem()
        edit_menu.append(separator)
        
        find_item = Gtk.MenuItem(label="Find")
        find_item.connect("activate", self.on_find)
        edit_menu.append(find_item)
        
        # Help menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)
        
        about_item = Gtk.MenuItem(label="About")
        about_item.connect("activate", self.on_about)
        help_menu.append(about_item)
        
        # Add menus to menu bar
        menu_bar.append(file_item)
        menu_bar.append(edit_item)
        menu_bar.append(help_item)
        
        self.main_box.pack_start(menu_bar, False, False, 0)
    
    def run(self):
        self.window.show_all()
        self.update_status_bar()
    
    def update_status_bar(self, *args):
        cursor_position = self.text_buffer.get_property("cursor-position")
        char_count = self.text_buffer.get_char_count()
        
        # Get current line and column
        iter_at_cursor = self.text_buffer.get_iter_at_offset(cursor_position)
        line = iter_at_cursor.get_line() + 1  # 0-based to 1-based
        column = iter_at_cursor.get_line_offset() + 1  # 0-based to 1-based
        
        status_text = f"Line: {line}, Column: {column}, Characters: {char_count}"
        
        if self.current_file:
            status_text = f"{os.path.basename(self.current_file)} - {status_text}"
        
        # Update status bar
        self.status_bar.pop(self.status_bar_context)
        self.status_bar.push(self.status_bar_context, status_text)
    
    def on_new(self, widget):
        if self.check_unsaved_changes():
            self.text_buffer.set_text("")
            self.current_file = None
            self.update_status_bar()
            self.window.set_title("Flask2 Editor")
    
    def on_open(self, widget):
        if not self.check_unsaved_changes():
            return
        
        dialog = Gtk.FileChooserDialog(
            title="Open File",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.open_file(dialog.get_filename())
        
        dialog.destroy()
    
    def open_file(self, filename):
        try:
            with open(filename, 'r') as f:
                content = f.read()
                self.text_buffer.set_text(content)
                self.current_file = filename
                self.window.set_title(f"Flask2 Editor - {os.path.basename(filename)}")
                self.update_status_bar()
        except Exception as e:
            self.show_error_dialog(f"Error opening file: {str(e)}")
    
    def on_save(self, widget):
        if self.current_file:
            self.save_file(self.current_file)
        else:
            self.on_save_as(widget)
    
    def on_save_as(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Save File",
            parent=self.window,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_do_overwrite_confirmation(True)
        
        if self.current_file:
            dialog.set_filename(self.current_file)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.save_file(filename)
        
        dialog.destroy()
    
    def save_file(self, filename):
        try:
            start_iter = self.text_buffer.get_start_iter()
            end_iter = self.text_buffer.get_end_iter()
            text = self.text_buffer.get_text(start_iter, end_iter, True)
            
            with open(filename, 'w') as f:
                f.write(text)
            
            self.current_file = filename
            self.window.set_title(f"Flask2 Editor - {os.path.basename(filename)}")
            self.update_status_bar()
            
            # Show success message in status bar
            self.status_bar.push(self.status_bar_context, f"File saved: {filename}")
        except Exception as e:
            self.show_error_dialog(f"Error saving file: {str(e)}")
    
    def on_quit(self, widget):
        if self.check_unsaved_changes():
            self.window.destroy()
    
    def on_cut(self, widget):
        self.text_buffer.cut_clipboard(Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD), True)
    
    def on_copy(self, widget):
        self.text_buffer.copy_clipboard(Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD))
    
    def on_paste(self, widget):
        self.text_buffer.paste_clipboard(Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD), None, True)
    
    def on_find(self, widget):
        dialog = Gtk.Dialog(
            title="Find",
            parent=self.window,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_FIND, Gtk.ResponseType.OK
        )
        
        box = dialog.get_content_area()
        box.set_border_width(10)
        
        label = Gtk.Label(label="Search for:")
        box.pack_start(label, False, False, 0)
        
        entry = Gtk.Entry()
        box.pack_start(entry, True, True, 5)
        
        case_sensitive = Gtk.CheckButton(label="Case sensitive")
        box.pack_start(case_sensitive, False, False, 5)
        
        box.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            search_text = entry.get_text()
            if search_text:
                self.find_text(search_text, case_sensitive.get_active())
        
        dialog.destroy()
    
    def find_text(self, search_text, case_sensitive=False):
        start_iter = self.text_buffer.get_start_iter()
        if not case_sensitive:
            search_flags = Gtk.TextSearchFlags.CASE_INSENSITIVE
        else:
            search_flags = Gtk.TextSearchFlags.VISIBLE_ONLY
        
        match = start_iter.forward_search(search_text, search_flags, None)
        
        if match:
            match_start, match_end = match
            self.text_buffer.select_range(match_start, match_end)
            self.text_view.scroll_to_iter(match_start, 0.0, True, 0.0, 0.5)
        else:
            self.show_info_dialog(f"Text '{search_text}' not found")
    
    def on_about(self, widget):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_title("About Flask2 Editor")
        about_dialog.set_program_name("Flask2 Editor")
        about_dialog.set_version("1.0")
        about_dialog.set_comments("A simple text editor for NoxDE")
        about_dialog.set_copyright("© 2025")
        about_dialog.run()
        about_dialog.destroy()
    
    def check_unsaved_changes(self):
        if self.text_buffer.get_modified():
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text="Save changes before closing?"
            )
            dialog.add_buttons(
                "Cancel", Gtk.ResponseType.CANCEL,
                "Don't Save", Gtk.ResponseType.NO,
                "Save", Gtk.ResponseType.YES
            )
            
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                self.on_save(None)
                return True
            elif response == Gtk.ResponseType.NO:
                return True
            else:
                return False
        return True
    
    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def show_info_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Information"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    # Set CSS styles
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(b"""
        .panel {
            background-color: #333333;
            color: white;
            padding: 5px;
        }
        window {
            background-color: #222222;
        }
        button {
            background-image: none;
            background-color: #444444;
            color: white;
            border-radius: 3px;
            border: 1px solid #555555;
        }
        button:hover {
            background-color: #555555;
        }
    """)
    
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    
    # Start the desktop environment
    de = NoxDE()
    Gtk.main()
