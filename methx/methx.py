#!/usr/bin/env python3
import os
import wx
import shutil
import subprocess
import platform
from datetime import datetime

class FileExplorerPanel(wx.Panel):
    def __init__(self, parent):
        super(FileExplorerPanel, self).__init__(parent)
        
        self.current_path = os.path.expanduser("~")
        
        # Create sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        nav_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Navigation controls
        self.path_text = wx.TextCtrl(self)
        self.path_text.SetValue(self.current_path)
        self.path_text.Bind(wx.EVT_TEXT_ENTER, self.on_path_changed)
        
        back_btn = wx.Button(self, label="Back")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        
        up_btn = wx.Button(self, label="Up")
        up_btn.Bind(wx.EVT_BUTTON, self.on_up)
        
        refresh_btn = wx.Button(self, label="Refresh")
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        
        # Add controls to navigation sizer
        nav_sizer.Add(back_btn, 0, wx.RIGHT, 5)
        nav_sizer.Add(up_btn, 0, wx.RIGHT, 5)
        nav_sizer.Add(refresh_btn, 0, wx.RIGHT, 5)
        nav_sizer.Add(self.path_text, 1, wx.EXPAND)
        
        # Create file list
        self.file_list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.file_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        self.file_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_right_click)
        
        # Add columns to file list
        self.file_list.InsertColumn(0, "Name")
        self.file_list.InsertColumn(1, "Size")
        self.file_list.InsertColumn(2, "Type")
        self.file_list.InsertColumn(3, "Modified")
        
        # Add search box
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        search_label = wx.StaticText(self, label="Search:")
        self.search_text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.search_text.Bind(wx.EVT_TEXT_ENTER, self.on_search)
        search_btn = wx.Button(self, label="Search")
        search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        
        search_sizer.Add(search_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        search_sizer.Add(self.search_text, 1, wx.EXPAND | wx.RIGHT, 5)
        search_sizer.Add(search_btn, 0)
        
        # Status bar for information
        self.status_bar = wx.StaticText(self)
        
        # Add everything to main sizer
        main_sizer.Add(nav_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.file_list, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(search_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.status_bar, 0, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)
        
        # Fill file list with initial directory
        self.populate_file_list()
        
        # Set column widths
        self.file_list.SetColumnWidth(0, 250)
        self.file_list.SetColumnWidth(1, 100)
        self.file_list.SetColumnWidth(2, 100)
        self.file_list.SetColumnWidth(3, 150)
    
    def populate_file_list(self):
        self.file_list.DeleteAllItems()
        self.path_text.SetValue(self.current_path)
        
        try:
            # Get list of files and directories
            items = os.listdir(self.current_path)
            
            # Add directories first
            directories = [item for item in items if os.path.isdir(os.path.join(self.current_path, item))]
            directories.sort()
            
            files = [item for item in items if os.path.isfile(os.path.join(self.current_path, item))]
            files.sort()
            
            # Add special ".." directory for going up
            index = self.file_list.InsertItem(0, "..")
            self.file_list.SetItem(index, 1, "")
            self.file_list.SetItem(index, 2, "Directory")
            self.file_list.SetItem(index, 3, "")
            
            # Add directories
            for i, item in enumerate(directories):
                path = os.path.join(self.current_path, item)
                index = self.file_list.InsertItem(i + 1, item)
                
                # Set file size
                self.file_list.SetItem(index, 1, "")
                
                # Set file type
                self.file_list.SetItem(index, 2, "Directory")
                
                # Set modification time
                try:
                    mod_time = os.path.getmtime(path)
                    date_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    self.file_list.SetItem(index, 3, date_str)
                except:
                    self.file_list.SetItem(index, 3, "")
            
            # Add files
            for i, item in enumerate(files):
                path = os.path.join(self.current_path, item)
                index = self.file_list.InsertItem(i + 1 + len(directories), item)
                
                # Set file size
                try:
                    size = os.path.getsize(path)
                    size_str = self.format_size(size)
                    self.file_list.SetItem(index, 1, size_str)
                except:
                    self.file_list.SetItem(index, 1, "")
                
                # Set file type
                ext = os.path.splitext(item)[1].lower()
                if ext:
                    self.file_list.SetItem(index, 2, ext[1:].upper() + " File")
                else:
                    self.file_list.SetItem(index, 2, "File")
                
                # Set modification time
                try:
                    mod_time = os.path.getmtime(path)
                    date_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    self.file_list.SetItem(index, 3, date_str)
                except:
                    self.file_list.SetItem(index, 3, "")
            
            # Update status bar
            self.update_status_bar(directories, files)
            
        except Exception as e:
            self.status_bar.SetLabel(f"Error: {str(e)}")
    
    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def update_status_bar(self, directories, files):
        total_size = 0
        try:
            for file in files:
                path = os.path.join(self.current_path, file)
                total_size += os.path.getsize(path)
        except:
            pass
        
        self.status_bar.SetLabel(f"{len(directories)} directories, {len(files)} files, Total size: {self.format_size(total_size)}")
    
    def on_path_changed(self, event):
        new_path = self.path_text.GetValue()
        if os.path.exists(new_path) and os.path.isdir(new_path):
            self.current_path = new_path
            self.populate_file_list()
        else:
            self.path_text.SetValue(self.current_path)
            self.status_bar.SetLabel(f"Invalid path: {new_path}")
    
    def on_back(self, event):
        # TODO: Implement back functionality with history
        pass
    
    def on_up(self, event):
        parent_dir = os.path.dirname(self.current_path)
        if parent_dir and parent_dir != self.current_path:
            self.current_path = parent_dir
            self.populate_file_list()
    
    def on_refresh(self, event):
        self.populate_file_list()
    
    def on_item_activated(self, event):
        index = event.GetIndex()
        item_text = self.file_list.GetItemText(index)
        
        if item_text == "..":
            # Go up a directory
            self.on_up(None)
        else:
            path = os.path.join(self.current_path, item_text)
            if os.path.isdir(path):
                self.current_path = path
                self.populate_file_list()
            else:
                self.open_file(path)
    
    def on_right_click(self, event):
        index = event.GetIndex()
        item_text = self.file_list.GetItemText(index)
        
        if item_text == "..":
            return
        
        path = os.path.join(self.current_path, item_text)
        
        # Create context menu
        menu = wx.Menu()
        
        # Add menu items
        open_item = menu.Append(wx.ID_ANY, "Open")
        self.Bind(wx.EVT_MENU, lambda e: self.open_file(path), open_item)
        
        if os.path.isfile(path):
            edit_item = menu.Append(wx.ID_ANY, "Edit")
            self.Bind(wx.EVT_MENU, lambda e: self.edit_file(path), edit_item)
        
        menu.AppendSeparator()
        
        copy_item = menu.Append(wx.ID_ANY, "Copy")
        self.Bind(wx.EVT_MENU, lambda e: self.copy_to_clipboard(path), copy_item)
        
        delete_item = menu.Append(wx.ID_ANY, "Delete")
        self.Bind(wx.EVT_MENU, lambda e: self.delete_item(path), delete_item)
        
        menu.AppendSeparator()
        
        properties_item = menu.Append(wx.ID_ANY, "Properties")
        self.Bind(wx.EVT_MENU, lambda e: self.show_properties(path), properties_item)
        
        # Show context menu
        self.PopupMenu(menu)
        menu.Destroy()
    
    def open_file(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
            self.status_bar.SetLabel(f"Opened: {path}")
        except Exception as e:
            self.status_bar.SetLabel(f"Error opening file: {str(e)}")
    
    def edit_file(self, path):
        try:
            # Try to determine suitable editor
            editor = None
            if platform.system() == "Windows":
                editor = "notepad.exe"
            elif platform.system() == "Darwin":  # macOS
                editor = "open -t"
            else:  # Linux
                for ed in ["nano", "vim", "gedit", "kwrite"]:
                    if shutil.which(ed):
                        editor = ed
                        break
            
            if editor:
                if " " in editor:  # handle "open -t" case
                    cmd = editor.split() + [path]
                    subprocess.Popen(cmd)
                else:
                    subprocess.Popen([editor, path])
                self.status_bar.SetLabel(f"Editing: {path}")
            else:
                self.status_bar.SetLabel("No suitable editor found")
        except Exception as e:
            self.status_bar.SetLabel(f"Error editing file: {str(e)}")
    
    def copy_to_clipboard(self, path):
        clipboard = wx.Clipboard.Get()
        if clipboard.Open():
            clipboard.SetData(wx.TextDataObject(path))
            clipboard.Close()
            self.status_bar.SetLabel(f"Path copied to clipboard: {path}")
    
    def delete_item(self, path):
        filename = os.path.basename(path)
        dlg = wx.MessageDialog(self, f"Are you sure you want to delete '{filename}'?",
                              "Confirm Delete", wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        
        if result == wx.ID_YES:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.populate_file_list()
                self.status_bar.SetLabel(f"Deleted: {path}")
            except Exception as e:
                self.status_bar.SetLabel(f"Error deleting: {str(e)}")
    
    def show_properties(self, path):
        filename = os.path.basename(path)
        is_dir = os.path.isdir(path)
        
        try:
            stats = os.stat(path)
            created = datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            accessed = datetime.fromtimestamp(stats.st_atime).strftime("%Y-%m-%d %H:%M:%S")
            
            size_bytes = stats.st_size if not is_dir else self.get_dir_size(path)
            size_str = self.format_size(size_bytes)
            
            info = f"Name: {filename}\n"
            info += f"Type: {'Directory' if is_dir else 'File'}\n"
            info += f"Location: {os.path.dirname(path)}\n"
            info += f"Size: {size_str} ({size_bytes:,} bytes)\n"
            info += f"Created: {created}\n"
            info += f"Modified: {modified}\n"
            info += f"Accessed: {accessed}\n"
            
            # File permissions
            if platform.system() != "Windows":
                perms = stats.st_mode
                info += f"Permissions: {oct(perms)[-3:]}\n"
            
            dlg = wx.MessageDialog(self, info, "Properties", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        except Exception as e:
            self.status_bar.SetLabel(f"Error getting properties: {str(e)}")
    
    def get_dir_size(self, path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except:
                        pass
        return total_size
    
    def on_search(self, event):
        search_term = self.search_text.GetValue().lower()
        if not search_term:
            self.populate_file_list()
            return
        
        self.file_list.DeleteAllItems()
        
        try:
            items = os.listdir(self.current_path)
            matching_items = []
            
            for item in items:
                if search_term in item.lower():
                    path = os.path.join(self.current_path, item)
                    matching_items.append((item, path))
            
            # Add special ".." directory for going up
            index = self.file_list.InsertItem(0, "..")
            self.file_list.SetItem(index, 1, "")
            self.file_list.SetItem(index, 2, "Directory")
            self.file_list.SetItem(index, 3, "")
            
            # Add matching items
            for i, (item, path) in enumerate(matching_items):
                index = self.file_list.InsertItem(i + 1, item)
                
                # Set file size
                if os.path.isfile(path):
                    try:
                        size = os.path.getsize(path)
                        size_str = self.format_size(size)
                        self.file_list.SetItem(index, 1, size_str)
                    except:
                        self.file_list.SetItem(index, 1, "")
                else:
                    self.file_list.SetItem(index, 1, "")
                
                # Set file type
                if os.path.isdir(path):
                    self.file_list.SetItem(index, 2, "Directory")
                else:
                    ext = os.path.splitext(item)[1].lower()
                    if ext:
                        self.file_list.SetItem(index, 2, ext[1:].upper() + " File")
                    else:
                        self.file_list.SetItem(index, 2, "File")
                
                # Set modification time
                try:
                    mod_time = os.path.getmtime(path)
                    date_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    self.file_list.SetItem(index, 3, date_str)
                except:
                    self.file_list.SetItem(index, 3, "")
            
            self.status_bar.SetLabel(f"Search results for '{search_term}': {len(matching_items)} items found")
            
        except Exception as e:
            self.status_bar.SetLabel(f"Error searching: {str(e)}")


class MethxApp(wx.Frame):
    def __init__(self):
        super(MethxApp, self).__init__(None, title="Methx File Explorer", size=(800, 600))
        
        # Create menu bar
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        
        open_item = file_menu.Append(wx.ID_OPEN, "Open Location...", "Open a specific location")
        self.Bind(wx.EVT_MENU, self.on_open_location, open_item)
        
        file_menu.AppendSeparator()
        
        exit_item = file_menu.Append(wx.ID_EXIT, "Exit", "Exit the application")
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        
        # Edit menu
        edit_menu = wx.Menu()
        
        select_all_item = edit_menu.Append(wx.ID_SELECTALL, "Select All", "Select all items")
        self.Bind(wx.EVT_MENU, self.on_select_all, select_all_item)
        
        # View menu
        view_menu = wx.Menu()
        
        refresh_item = view_menu.Append(wx.ID_REFRESH, "Refresh", "Refresh the current view")
        self.Bind(wx.EVT_MENU, self.on_refresh, refresh_item)
        
        # Help menu
        help_menu = wx.Menu()
        
        about_item = help_menu.Append(wx.ID_ABOUT, "About", "About Methx File Explorer")
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        
        # Add menus to menu bar
        menubar.Append(file_menu, "File")
        menubar.Append(edit_menu, "Edit")
        menubar.Append(view_menu, "View")
        menubar.Append(help_menu, "Help")
        
        self.SetMenuBar(menubar)
        
        # Create status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready")
        
        # Create file explorer panel
        self.explorer = FileExplorerPanel(self)
        
        # Create sizer for layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.explorer, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        # Center on screen
        self.Centre()
        self.Show()
    
    def on_open_location(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.explorer.current_path = path
            self.explorer.populate_file_list()
        dlg.Destroy()
    
    def on_exit(self, event):
        self.Close()
    
    def on_select_all(self, event):
        for i in range(self.explorer.file_list.GetItemCount()):
            self.explorer.file_list.Select(i)
    
    def on_refresh(self, event):
        self.explorer.populate_file_list()
    
    def on_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("Methx File Explorer")
        info.SetVersion("1.0")
        info.SetDescription("A simple file explorer built with wxPython")
        info.SetCopyright("(C) 2025")
        info.SetWebSite("https://example.com/methx")
        
        wx.adv.AboutBox(info)


def main():
    app = wx.App()
    frame = MethxApp()
    app.MainLoop()


if __name__ == "__main__":
    main()
