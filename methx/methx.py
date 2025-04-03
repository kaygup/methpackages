#!/usr/bin/env python3
"""
Methx - A Simple File Explorer made with wxPython
"""

import os
import sys
import wx
import wx.lib.agw.customtreectrl as ctc
import shutil
import subprocess

class MethxFrame(wx.Frame):
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, title="Methx File Explorer", size=(900, 600))
        
        # Create splitter window
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        
        # Create panels
        self.tree_panel = wx.Panel(self.splitter)
        self.file_panel = wx.Panel(self.splitter)
        
        # Tree Panel
        self.tree = ctc.CustomTreeCtrl(self.tree_panel, agwStyle=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.TR_FULL_ROW_HIGHLIGHT)
        self.root = self.tree.AddRoot("Root")
        
        # Get home directory
        self.home_dir = os.path.expanduser("~")
        self.current_dir = self.home_dir
        
        # Create tree layout
        tree_sizer = wx.BoxSizer(wx.VERTICAL)
        path_label = wx.StaticText(self.tree_panel, label="Directory Tree:")
        tree_sizer.Add(path_label, 0, wx.ALL, 5)
        tree_sizer.Add(self.tree, 1, wx.EXPAND|wx.ALL, 5)
        self.tree_panel.SetSizer(tree_sizer)
        
        # File Panel
        self.file_list = wx.ListCtrl(self.file_panel, style=wx.LC_REPORT)
        self.file_list.InsertColumn(0, "Name")
        self.file_list.InsertColumn(1, "Size")
        self.file_list.InsertColumn(2, "Type")
        self.file_list.InsertColumn(3, "Modified")
        
        # Path display - FIX: Added wxTE_PROCESS_ENTER style flag
        self.path_text = wx.TextCtrl(self.file_panel, style=wx.TE_PROCESS_ENTER)
        self.path_text.SetValue(self.current_dir)
        
        # Buttons
        button_panel = wx.Panel(self.file_panel)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.back_btn = wx.Button(button_panel, label="← Back")
        self.home_btn = wx.Button(button_panel, label="Home")
        self.refresh_btn = wx.Button(button_panel, label="Refresh")
        self.go_btn = wx.Button(button_panel, label="Go")
        
        button_sizer.Add(self.back_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.home_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.refresh_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.go_btn, 0, wx.RIGHT, 5)
        
        button_panel.SetSizer(button_sizer)
        
        # File panel layout
        file_sizer = wx.BoxSizer(wx.VERTICAL)
        path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        path_sizer.Add(wx.StaticText(self.file_panel, label="Path: "), 0, wx.CENTER|wx.ALL, 5)
        path_sizer.Add(self.path_text, 1, wx.EXPAND|wx.ALL, 5)
        
        file_sizer.Add(path_sizer, 0, wx.EXPAND|wx.ALL, 5)
        file_sizer.Add(button_panel, 0, wx.ALL, 5)
        file_sizer.Add(self.file_list, 1, wx.EXPAND|wx.ALL, 5)
        self.file_panel.SetSizer(file_sizer)
        
        # Setup splitter
        self.splitter.SplitVertically(self.tree_panel, self.file_panel)
        self.splitter.SetMinimumPaneSize(200)
        self.splitter.SetSashPosition(250)
        
        # Status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Ready")
        
        # Menu bar
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        new_folder_item = file_menu.Append(wx.ID_ANY, "New Folder\tCtrl+N", "Create a new folder")
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(wx.ID_EXIT, "Quit\tCtrl+Q", "Exit application")
        
        # Edit menu
        edit_menu = wx.Menu()
        copy_item = edit_menu.Append(wx.ID_COPY, "Copy\tCtrl+C", "Copy selected files")
        cut_item = edit_menu.Append(wx.ID_CUT, "Cut\tCtrl+X", "Cut selected files")
        paste_item = edit_menu.Append(wx.ID_PASTE, "Paste\tCtrl+V", "Paste files")
        edit_menu.AppendSeparator()
        delete_item = edit_menu.Append(wx.ID_DELETE, "Delete\tDel", "Delete selected files")
        
        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "About", "About Methx File Explorer")
        
        menubar.Append(file_menu, "File")
        menubar.Append(edit_menu, "Edit")
        menubar.Append(help_menu, "Help")
        self.SetMenuBar(menubar)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        self.Bind(wx.EVT_MENU, self.OnNewFolder, new_folder_item)
        self.Bind(wx.EVT_MENU, self.OnCopy, copy_item)
        self.Bind(wx.EVT_MENU, self.OnCut, cut_item)
        self.Bind(wx.EVT_MENU, self.OnPaste, paste_item)
        self.Bind(wx.EVT_MENU, self.OnDelete, delete_item)
        
        self.tree.Bind(ctc.EVT_TREE_ITEM_ACTIVATED, self.OnTreeActivated)
        self.file_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnFileActivated)
        self.back_btn.Bind(wx.EVT_BUTTON, self.OnBackButton)
        self.home_btn.Bind(wx.EVT_BUTTON, self.OnHomeButton)
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.OnRefreshButton)
        self.go_btn.Bind(wx.EVT_BUTTON, self.OnGoButton)
        self.path_text.Bind(wx.EVT_TEXT_ENTER, self.OnGoButton)
        
        # Fill tree with drives/root
        self.populate_tree()
        
        # Fill initial file list
        self.populate_file_list(self.current_dir)
        
        # Clipboard data
        self.clipboard = []
        self.clipboard_action = ""  # "copy" or "cut"
        
        # Center window
        self.Center()
        
    def populate_tree(self):
        """Populate the directory tree with initial items"""
        self.tree.DeleteAllItems()
        self.root = self.tree.AddRoot("Root")
        
        if sys.platform == "win32":
            # On Windows, add drives
            for drive in range(65, 91):  # A-Z
                drive_letter = chr(drive) + ":\\"
                if os.path.exists(drive_letter):
                    drive_item = self.tree.AppendItem(self.root, drive_letter)
                    self.add_subdirectories(drive_item, drive_letter)
        else:
            # On Unix-like systems, start with root
            root_item = self.tree.AppendItem(self.root, "/")
            self.add_subdirectories(root_item, "/")
            
            # Add home directory
            home_item = self.tree.AppendItem(self.root, self.home_dir)
            self.add_subdirectories(home_item, self.home_dir)
    
    def add_subdirectories(self, parent_item, path):
        """Add subdirectories to the tree item"""
        try:
            directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
            directories.sort()
            
            for directory in directories[:10]:  # Limit to first 10 to avoid tree explosion
                dir_path = os.path.join(path, directory)
                try:
                    dir_item = self.tree.AppendItem(parent_item, directory)
                    # Check if this directory has subdirectories
                    has_subdirs = False
                    try:
                        subdirs = [d for d in os.listdir(dir_path) 
                                 if os.path.isdir(os.path.join(dir_path, d)) and not d.startswith('.')]
                        if subdirs:
                            has_subdirs = True
                    except:
                        pass
                        
                    if has_subdirs:
                        # Add a dummy item that will be replaced when expanded
                        self.tree.AppendItem(dir_item, "Loading...")
                except:
                    pass
        except:
            pass
    
    def populate_file_list(self, path):
        """Fill the file list with contents of the path"""
        self.file_list.DeleteAllItems()
        self.current_dir = path
        self.path_text.SetValue(path)
        
        try:
            items = os.listdir(path)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            index = 0
            for item in items:
                item_path = os.path.join(path, item)
                try:
                    # Get item stats
                    stats = os.stat(item_path)
                    
                    # File size (formatted)
                    if os.path.isdir(item_path):
                        size_str = "<DIR>"
                        item_type = "Folder"
                    else:
                        size = stats.st_size
                        if size < 1024:
                            size_str = f"{size} B"
                        elif size < 1024 * 1024:
                            size_str = f"{size / 1024:.1f} KB"
                        else:
                            size_str = f"{size / (1024 * 1024):.1f} MB"
                        
                        # Get file extension
                        _, ext = os.path.splitext(item)
                        item_type = ext[1:].upper() + " File" if ext else "File"
                    
                    # Format date
                    import datetime
                    mod_time = datetime.datetime.fromtimestamp(stats.st_mtime)
                    date_str = mod_time.strftime("%Y-%m-%d %H:%M")
                    
                    # Add to list
                    idx = self.file_list.InsertItem(index, item)
                    self.file_list.SetItem(idx, 1, size_str)
                    self.file_list.SetItem(idx, 2, item_type)
                    self.file_list.SetItem(idx, 3, date_str)
                    
                    index += 1
                except:
                    pass
                    
            # Resize columns
            for i in range(4):
                self.file_list.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                
            # Update status bar
            dir_count = sum(1 for item in items if os.path.isdir(os.path.join(path, item)))
            file_count = len(items) - dir_count
            self.statusbar.SetStatusText(f"{dir_count} directories, {file_count} files")
                
        except Exception as e:
            self.statusbar.SetStatusText(f"Error: {str(e)}")
    
    def OnTreeActivated(self, event):
        """Handle tree item activation"""
        item = event.GetItem()
        if not item:
            return
            
        # Get the full path by traversing up the tree
        path_parts = [self.tree.GetItemText(item)]
        parent = self.tree.GetItemParent(item)
        
        while parent != self.root:
            path_parts.insert(0, self.tree.GetItemText(parent))
            parent = self.tree.GetItemParent(parent)
            
        # Construct the path
        if sys.platform == "win32":
            # On Windows, first part might be a drive letter
            if path_parts and path_parts[0].endswith(':\\'):
                path = path_parts[0]
                for part in path_parts[1:]:
                    path = os.path.join(path, part)
            else:
                path = os.path.join(*path_parts)
        else:
            # On Unix, check if the path starts with / or ~
            if path_parts and path_parts[0] == "/":
                path = os.path.join('/', *path_parts[1:])
            elif path_parts and path_parts[0] == self.home_dir:
                path = self.home_dir
                for part in path_parts[1:]:
                    path = os.path.join(path, part)
            else:
                path = os.path.join(*path_parts)
        
        # Check if this is a directory
        if os.path.isdir(path):
            self.populate_file_list(path)
            
            # Clear existing items and populate with subdirectories
            self.tree.DeleteChildren(item)
            self.add_subdirectories(item, path)
    
    def OnFileActivated(self, event):
        """Handle file list item activation"""
        index = event.GetIndex()
        filename = self.file_list.GetItemText(index)
        filepath = os.path.join(self.current_dir, filename)
        
        if os.path.isdir(filepath):
            # Navigate to the directory
            self.populate_file_list(filepath)
        else:
            # Try to open the file with default application
            try:
                if sys.platform == "win32":
                    os.startfile(filepath)
                elif sys.platform == "darwin":
                    subprocess.call(["open", filepath])
                else:
                    subprocess.call(["xdg-open", filepath])
            except Exception as e:
                wx.MessageBox(f"Could not open the file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def OnBackButton(self, event):
        """Go to parent directory"""
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir and parent_dir != self.current_dir:
            self.populate_file_list(parent_dir)
    
    def OnHomeButton(self, event):
        """Go to home directory"""
        self.populate_file_list(self.home_dir)
    
    def OnRefreshButton(self, event):
        """Refresh current directory"""
        self.populate_file_list(self.current_dir)
    
    def OnGoButton(self, event):
        """Navigate to the path in the text field"""
        path = self.path_text.GetValue()
        if os.path.exists(path) and os.path.isdir(path):
            self.populate_file_list(path)
        else:
            wx.MessageBox(f"Invalid directory: {path}", "Error", wx.OK | wx.ICON_ERROR)
    
    def OnNewFolder(self, event):
        """Create a new folder in the current directory"""
        dialog = wx.TextEntryDialog(self, "Enter name for new folder:", "New Folder")
        if dialog.ShowModal() == wx.ID_OK:
            folder_name = dialog.GetValue()
            new_folder_path = os.path.join(self.current_dir, folder_name)
            
            try:
                os.mkdir(new_folder_path)
                self.populate_file_list(self.current_dir)  # Refresh
            except Exception as e:
                wx.MessageBox(f"Could not create folder: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
                
        dialog.Destroy()
    
    def OnCopy(self, event):
        """Copy selected files to clipboard"""
        selected = []
        index = self.file_list.GetFirstSelected()
        
        while index != -1:
            filename = self.file_list.GetItemText(index)
            filepath = os.path.join(self.current_dir, filename)
            selected.append(filepath)
            index = self.file_list.GetNextSelected(index)
        
        if selected:
            self.clipboard = selected
            self.clipboard_action = "copy"
            self.statusbar.SetStatusText(f"{len(selected)} items copied to clipboard")
    
    def OnCut(self, event):
        """Cut selected files to clipboard"""
        selected = []
        index = self.file_list.GetFirstSelected()
        
        while index != -1:
            filename = self.file_list.GetItemText(index)
            filepath = os.path.join(self.current_dir, filename)
            selected.append(filepath)
            index = self.file_list.GetNextSelected(index)
        
        if selected:
            self.clipboard = selected
            self.clipboard_action = "cut"
            self.statusbar.SetStatusText(f"{len(selected)} items cut to clipboard")
    
    def OnPaste(self, event):
        """Paste files from clipboard"""
        if not self.clipboard:
            return
            
        error_count = 0
        success_count = 0
        
        for src_path in self.clipboard:
            try:
                filename = os.path.basename(src_path)
                dest_path = os.path.join(self.current_dir, filename)
                
                # Check if destination exists
                if os.path.exists(dest_path):
                    dlg = wx.MessageDialog(self, 
                                          f"'{filename}' already exists. Overwrite?",
                                          "Confirm Overwrite",
                                          wx.YES_NO | wx.ICON_QUESTION)
                    if dlg.ShowModal() != wx.ID_YES:
                        dlg.Destroy()
                        continue
                    dlg.Destroy()
                
                # Perform copy or move
                if os.path.isdir(src_path):
                    if self.clipboard_action == "copy":
                        shutil.copytree(src_path, dest_path)
                    else:  # cut
                        shutil.move(src_path, dest_path)
                else:
                    if self.clipboard_action == "copy":
                        shutil.copy2(src_path, dest_path)
                    else:  # cut
                        shutil.move(src_path, dest_path)
                        
                success_count += 1
            except Exception as e:
                error_count += 1
                wx.LogError(f"Error processing '{src_path}': {str(e)}")
        
        # Clear clipboard if it was a cut operation
        if self.clipboard_action == "cut" and error_count == 0:
            self.clipboard = []
            
        # Refresh and update status
        self.populate_file_list(self.current_dir)
        
        if error_count:
            self.statusbar.SetStatusText(f"Paste completed with {error_count} errors")
        else:
            self.statusbar.SetStatusText(f"Paste completed successfully: {success_count} items")
    
    def OnDelete(self, event):
        """Delete selected files"""
        selected = []
        index = self.file_list.GetFirstSelected()
        
        while index != -1:
            filename = self.file_list.GetItemText(index)
            filepath = os.path.join(self.current_dir, filename)
            selected.append(filepath)
            index = self.file_list.GetNextSelected(index)
        
        if not selected:
            return
            
        # Confirm deletion
        msg = f"Are you sure you want to delete {len(selected)} item(s)?"
        dlg = wx.MessageDialog(self, msg, "Confirm Deletion", 
                              wx.YES_NO | wx.ICON_QUESTION)
        
        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
            
        dlg.Destroy()
        
        # Delete files
        error_count = 0
        for path in selected:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                error_count += 1
                wx.LogError(f"Error deleting '{path}': {str(e)}")
        
        # Refresh and update status
        self.populate_file_list(self.current_dir)
        
        if error_count:
            self.statusbar.SetStatusText(f"Deletion completed with {error_count} errors")
        else:
            self.statusbar.SetStatusText(f"Deleted {len(selected)} items successfully")
    
    def OnQuit(self, event):
        """Exit the application"""
        self.Close()
    
    def OnAbout(self, event):
        """Show about dialog"""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Methx File Explorer")
        info.SetVersion("1.0")
        info.SetDescription("A simple file explorer built with wxPython")
        info.SetCopyright("(C) 2025")
        info.AddDeveloper("Methx Developer")
        info.SetWebSite("https://example.com/methx")
        
        wx.adv.AboutBox(info)


class MethxApp(wx.App):
    def OnInit(self):
        frame = MethxFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = MethxApp(False)
    app.MainLoop()
