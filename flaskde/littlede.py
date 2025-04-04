# little_de.py
#!/usr/bin/env python3
"""
Little DE - A minimal desktop environment with USB bootable creation
and Flask2 text editor utility
"""

import os
import sys
import gi
import subprocess
import threading
import tempfile
import shutil
from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GLib, GObject

class Flask2Editor(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Flask2 Editor")
        self.set_default_size(800, 600)
        self.current_file = None
        
        # Main layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)
        
        # Menu bar
        menubar = Gtk.MenuBar()
        self.box.pack_start(menubar, False, False, 0)
        
        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        menubar.append(file_item)
        
        new_item = Gtk.MenuItem(label="New")
        new_item.connect("activate", self.on_new_clicked)
        file_menu.append(new_item)
        
        open_item = Gtk.MenuItem(label="Open")
        open_item.connect("activate", self.on_open_clicked)
        file_menu.append(open_item)
        
        save_item = Gtk.MenuItem(label="Save")
        save_item.connect("activate", self.on_save_clicked)
        file_menu.append(save_item)
        
        save_as_item = Gtk.MenuItem(label="Save As")
        save_as_item.connect("activate", self.on_save_as_clicked)
        file_menu.append(save_as_item)
        
        separator = Gtk.SeparatorMenuItem()
        file_menu.append(separator)
        
        exit_item = Gtk.MenuItem(label="Exit")
        exit_item.connect("activate", self.on_exit_clicked)
        file_menu.append(exit_item)
        
        # Edit menu
        edit_menu = Gtk.Menu()
        edit_item = Gtk.MenuItem(label="Edit")
        edit_item.set_submenu(edit_menu)
        menubar.append(edit_item)
        
        undo_item = Gtk.MenuItem(label="Undo")
        undo_item.connect("activate", self.on_undo_clicked)
        edit_menu.append(undo_item)
        
        redo_item = Gtk.MenuItem(label="Redo")
        redo_item.connect("activate", self.on_redo_clicked)
        edit_menu.append(redo_item)
        
        separator = Gtk.SeparatorMenuItem()
        edit_menu.append(separator)
        
        cut_item = Gtk.MenuItem(label="Cut")
        cut_item.connect("activate", self.on_cut_clicked)
        edit_menu.append(cut_item)
        
        copy_item = Gtk.MenuItem(label="Copy")
        copy_item.connect("activate", self.on_copy_clicked)
        edit_menu.append(copy_item)
        
        paste_item = Gtk.MenuItem(label="Paste")
        paste_item.connect("activate", self.on_paste_clicked)
        edit_menu.append(paste_item)
        
        # Text view with scrolling
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.box.pack_start(scrolled_window, True, True, 0)
        
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = self.textview.get_buffer()
        font_desc = Pango.FontDescription('monospace 10')
        self.textview.override_font(font_desc)
        scrolled_window.add(self.textview)
        
        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.box.pack_start(self.statusbar, False, False, 0)
        self.status_context = self.statusbar.get_context_id("editor_status")
        self.statusbar.push(self.status_context, "Ready")
        
    def on_new_clicked(self, widget):
        if self.check_save():
            self.textbuffer.set_text("")
            self.current_file = None
            self.statusbar.push(self.status_context, "New file")
    
    def on_open_clicked(self, widget):
        if self.check_save():
            dialog = Gtk.FileChooserDialog(
                title="Open File", parent=self,
                action=Gtk.FileChooserAction.OPEN
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
            
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.current_file = dialog.get_filename()
                try:
                    with open(self.current_file, "r") as file:
                        text = file.read()
                        self.textbuffer.set_text(text)
                    self.statusbar.push(self.status_context, f"Opened: {self.current_file}")
                except Exception as e:
                    self.show_error(f"Error opening file: {str(e)}")
            
            dialog.destroy()
    
    def on_save_clicked(self, widget):
        if self.current_file:
            self.save_file(self.current_file)
        else:
            self.on_save_as_clicked(widget)
    
    def on_save_as_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Save File As", parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_do_overwrite_confirmation(True)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.current_file = dialog.get_filename()
            self.save_file(self.current_file)
        
        dialog.destroy()
    
    def save_file(self, filename):
        try:
            start_iter = self.textbuffer.get_start_iter()
            end_iter = self.textbuffer.get_end_iter()
            text = self.textbuffer.get_text(start_iter, end_iter, True)
            
            with open(filename, "w") as file:
                file.write(text)
            
            self.statusbar.push(self.status_context, f"Saved: {filename}")
            return True
        except Exception as e:
            self.show_error(f"Error saving file: {str(e)}")
            return False
    
    def check_save(self):
        if self.textbuffer.get_modified():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Save changes to current file?"
            )
            dialog.format_secondary_text("Your changes will be lost if you don't save them.")
            dialog.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                return self.on_save_clicked(None)
            elif response == Gtk.ResponseType.NO:
                return True
            else:
                return False
        return True
    
    def on_exit_clicked(self, widget):
        if self.check_save():
            Gtk.main_quit()
    
    def on_undo_clicked(self, widget):
        # Placeholder for undo functionality
        self.statusbar.push(self.status_context, "Undo not implemented yet")
    
    def on_redo_clicked(self, widget):
        # Placeholder for redo functionality
        self.statusbar.push(self.status_context, "Redo not implemented yet")
    
    def on_cut_clicked(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.cut_clipboard(clipboard, self.textview.get_editable())
    
    def on_copy_clicked(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.copy_clipboard(clipboard)
    
    def on_paste_clicked(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.paste_clipboard(clipboard, None, self.textview.get_editable())
    
    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


class USBCreator(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="USB Bootable Creator")
        self.set_default_size(600, 400)
        self.set_border_width(10)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)
        
        # ISO file selection
        file_box = Gtk.Box(spacing=5)
        main_box.pack_start(file_box, False, False, 0)
        
        file_label = Gtk.Label(label="ISO File:")
        file_box.pack_start(file_label, False, False, 0)
        
        self.file_entry = Gtk.Entry()
        self.file_entry.set_editable(False)
        self.file_entry.set_hexpand(True)
        file_box.pack_start(self.file_entry, True, True, 0)
        
        file_button = Gtk.Button(label="Browse")
        file_button.connect("clicked", self.on_file_clicked)
        file_box.pack_start(file_button, False, False, 0)
        
        # USB device selection
        usb_box = Gtk.Box(spacing=5)
        main_box.pack_start(usb_box, False, False, 0)
        
        usb_label = Gtk.Label(label="USB Device:")
        usb_box.pack_start(usb_label, False, False, 0)
        
        self.usb_combo = Gtk.ComboBoxText()
        self.usb_combo.set_hexpand(True)
        usb_box.pack_start(self.usb_combo, True, True, 0)
        
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", self.refresh_usb_devices)
        usb_box.pack_start(refresh_button, False, False, 0)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        main_box.pack_start(self.progress_bar, False, False, 0)
        
        # Status label
        self.status_label = Gtk.Label(label="Select an ISO file and USB device")
        main_box.pack_start(self.status_label, False, False, 0)
        
        # Create button
        button_box = Gtk.Box(spacing=5)
        main_box.pack_start(button_box, False, False, 0)
        
        self.create_button = Gtk.Button(label="Create Bootable USB")
        self.create_button.connect("clicked", self.on_create_clicked)
        button_box.pack_end(self.create_button, False, False, 0)
        
        # Load devices initially
        self.refresh_usb_devices()
    
    def refresh_usb_devices(self, widget=None):
        self.usb_combo.remove_all()
        
        # Get devices
        try:
            result = subprocess.run(
                ["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL"],
                capture_output=True, text=True, check=True
            )
            
            for line in result.stdout.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and not parts[0].startswith("loop"):
                        device = parts[0]
                        size = parts[1]
                        model = " ".join(parts[2:]) if len(parts) > 2 else "Unknown"
                        text = f"/dev/{device} ({size}) - {model}"
                        self.usb_combo.append_text(text)
            
            if self.usb_combo.get_model().iter_n_children() > 0:
                self.usb_combo.set_active(0)
                
        except subprocess.SubprocessError as e:
            self.status_label.set_text(f"Error getting devices: {str(e)}")
    
    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select ISO File",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_iso = Gtk.FileFilter()
        filter_iso.set_name("ISO files")
        filter_iso.add_pattern("*.iso")
        dialog.add_filter(filter_iso)
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Image files")
        filter_img.add_pattern("*.img")
        dialog.add_filter(filter_img)
        
        filter_any = Gtk.FileFilter()
        filter_any.set_name("All files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file_entry.set_text(dialog.get_filename())
        
        dialog.destroy()
    
    def on_create_clicked(self, widget):
        iso_file = self.file_entry.get_text()
        usb_device = self.usb_combo.get_active_text()
        
        if not iso_file:
            self.show_error("Please select an ISO file")
            return
        
        if not usb_device:
            self.show_error("Please select a USB device")
            return
        
        device_path = usb_device.split()[0]
        
        # Confirm with user
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="WARNING: All data on the selected device will be lost!"
        )
        dialog.format_secondary_text(f"You are about to write to {device_path}. This cannot be undone.")
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            self.create_button.set_sensitive(False)
            self.status_label.set_text("Creating bootable USB... This may take a while")
            
            # Start thread for dd operation
            threading.Thread(target=self.create_usb, args=(iso_file, device_path), daemon=True).start()
    
    def create_usb(self, iso_file, device_path):
        try:
            # Using dd to write the ISO to USB
            process = subprocess.Popen(
                ["dd", f"if={iso_file}", f"of={device_path}", "bs=4M", "status=progress"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            # Process the output to update progress
            for line in iter(process.stderr.readline, ''):
                # Parse progress info and update UI through GLib idle add
                if "bytes" in line:
                    GLib.idle_add(self.status_label.set_text, f"Progress: {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                GLib.idle_add(self.on_create_success)
            else:
                GLib.idle_add(self.on_create_error, "dd command failed")
                
        except Exception as e:
            GLib.idle_add(self.on_create_error, str(e))
    
    def on_create_success(self):
        self.status_label.set_text("Bootable USB created successfully!")
        self.create_button.set_sensitive(True)
        
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Success"
        )
        dialog.format_secondary_text("Bootable USB created successfully!")
        dialog.run()
        dialog.destroy()
    
    def on_create_error(self, error_message):
        self.status_label.set_text(f"Error: {error_message}")
        self.create_button.set_sensitive(True)
        
        self.show_error(f"Failed to create bootable USB: {error_message}")
    
    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


class LittleDE(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id="org.little.de")
        self.connect("activate", self.on_activate)
        
    def on_activate(self, app):
        self.win = Gtk.ApplicationWindow(application=app, title="Little DE")
        self.win.set_default_size(800, 600)
        self.win.connect("delete-event", self.on_window_delete)
        
        # Main layout
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.win.add(self.box)
        
        # Header with title
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Little DE"
        self.win.set_titlebar(header)
        
        # Main content area with buttons for applications
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_border_width(20)
        self.box.pack_start(content_box, True, True, 0)
        
        # Title label
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>Little Desktop Environment</span>")
        content_box.pack_start(title_label, False, False, 0)
        
        # Applications section
        apps_label = Gtk.Label()
        apps_label.set_markup("<span size='large' weight='bold'>Applications</span>")
        apps_label.set_halign(Gtk.Align.START)
        content_box.pack_start(apps_label, False, False, 10)
        
        # App buttons container
        app_buttons = Gtk.Box(spacing=10)
        content_box.pack_start(app_buttons, False, False, 0)
        
        # Flask2 text editor button
        editor_button = Gtk.Button(label="Flask2 Text Editor")
        editor_button.connect("clicked", self.on_editor_clicked)
        app_buttons.pack_start(editor_button, True, True, 0)
        
        # USB creator button
        usb_button = Gtk.Button(label="USB Bootable Creator")
        usb_button.connect("clicked", self.on_usb_clicked)
        app_buttons.pack_start(usb_button, True, True, 0)
        
        # Quit button
        quit_button = Gtk.Button(label="Quit")
        quit_button.connect("clicked", self.on_quit_clicked)
        app_buttons.pack_start(quit_button, True, True, 0)
        
        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.statusbar.push(0, "Ready")
        self.box.pack_end(self.statusbar, False, False, 0)
        
        self.win.show_all()
    
    def on_editor_clicked(self, button):
        editor = Flask2Editor()
        editor.connect("destroy", Gtk.main_quit)
        editor.show_all()
        Gtk.main()
    
    def on_usb_clicked(self, button):
        usb_creator = USBCreator()
        usb_creator.connect("destroy", Gtk.main_quit)
        usb_creator.show_all()
        Gtk.main()
    
    def on_quit_clicked(self, button):
        self.win.close()
    
    def on_window_delete(self, widget, event):
        return False


def main():
    app = LittleDE()
    app.run(sys.argv)

if __name__ == "__main__":
    main()
