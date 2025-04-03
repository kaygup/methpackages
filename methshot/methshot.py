#!/usr/bin/env python3
"""
methshot - A simple screenshot utility built with PySide6
"""

import sys
import os
import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                             QFileDialog, QComboBox, QCheckBox, QSpinBox)
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtGui import QPixmap, QScreen, QGuiApplication, QIcon, QKeySequence, QShortcut

class ScreenshotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Methshot")
        self.resize(500, 350)
        
        # Default screenshot directory
        self.screenshot_dir = os.path.expanduser("~/Pictures/Screenshots")
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        
        self.capture_mode = "fullscreen"  # Default mode
        self.delay_seconds = 0
        self.show_notification = True
        
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Title
        title_label = QLabel("Methshot - Screenshot Utility")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Capture mode selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Capture Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Fullscreen", "Active Window", "Region Selection"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        main_layout.addLayout(mode_layout)
        
        # Delay selection
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Delay (seconds):")
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(0)
        self.delay_spin.valueChanged.connect(self.change_delay)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_spin)
        main_layout.addLayout(delay_layout)
        
        # Notification checkbox
        notification_layout = QHBoxLayout()
        self.notification_checkbox = QCheckBox("Show notification")
        self.notification_checkbox.setChecked(True)
        self.notification_checkbox.stateChanged.connect(self.toggle_notification)
        notification_layout.addWidget(self.notification_checkbox)
        main_layout.addLayout(notification_layout)
        
        # Save directory selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Save Directory:")
        self.dir_button = QPushButton(self.screenshot_dir)
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_button)
        main_layout.addLayout(dir_layout)
        
        # Capture button
        self.capture_button = QPushButton("Capture Screenshot")
        self.capture_button.setStyleSheet("font-size: 14pt; padding: 10px; margin-top: 20px;")
        self.capture_button.clicked.connect(self.capture_screenshot)
        main_layout.addWidget(self.capture_button)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Set central widget
        self.setCentralWidget(main_widget)
        
        # Keyboard shortcuts
        capture_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        capture_shortcut.activated.connect(self.capture_screenshot)
        
    def change_mode(self, mode_text):
        mode_map = {
            "Fullscreen": "fullscreen",
            "Active Window": "window",
            "Region Selection": "region"
        }
        self.capture_mode = mode_map.get(mode_text, "fullscreen")
        
    def change_delay(self, value):
        self.delay_seconds = value
        
    def toggle_notification(self, state):
        self.show_notification = bool(state)
        
    def select_directory(self):
        dir_name = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.screenshot_dir)
        if dir_name:
            self.screenshot_dir = dir_name
            self.dir_button.setText(self.screenshot_dir)
            
    def capture_screenshot(self):
        if self.delay_seconds > 0:
            self.status_label.setText(f"Capturing in {self.delay_seconds} seconds...")
            self.hide()  # Hide the window during countdown
            QTimer.singleShot(self.delay_seconds * 1000, self.perform_capture)
        else:
            self.hide()  # Hide the window immediately
            QTimer.singleShot(200, self.perform_capture)  # Small delay to ensure window is hidden
            
    def perform_capture(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"methshot_{timestamp}.png"
        full_path = os.path.join(self.screenshot_dir, filename)
        
        if self.capture_mode == "fullscreen":
            screen = QGuiApplication.primaryScreen()
            pixmap = screen.grabWindow(0)
        elif self.capture_mode == "window":
            # This is a simplified version - getting actual active window 
            # requires platform-specific code
            screen = QGuiApplication.primaryScreen()
            pixmap = screen.grabWindow(0)  # Fallback to fullscreen
        elif self.capture_mode == "region":
            # In a real implementation, this would use a selection widget
            # For this example, we'll just capture the center portion
            screen = QGuiApplication.primaryScreen()
            full = screen.grabWindow(0)
            screen_size = screen.size()
            region = QRect(
                screen_size.width() // 4,
                screen_size.height() // 4,
                screen_size.width() // 2,
                screen_size.height() // 2
            )
            pixmap = full.copy(region)
        
        # Save the screenshot
        success = pixmap.save(full_path)
        
        # Show result
        if success:
            self.status_label.setText(f"Screenshot saved: {full_path}")
            if self.show_notification:
                # In a full implementation, this would use a proper notification system
                print(f"Screenshot saved: {full_path}")
        else:
            self.status_label.setText("Failed to save screenshot")
        
        self.show()  # Show the window again

def main():
    app = QApplication(sys.argv)
    window = ScreenshotWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
