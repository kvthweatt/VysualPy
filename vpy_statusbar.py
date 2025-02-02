from PyQt5.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime
import os

class IDEStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set fixed height and slate color
        self.setFixedHeight(22)  # Reduce height
        self.setStyleSheet("""
            QStatusBar {
                background: #1a1a1a;  /* Dark slate color */
                color: #ecf0f1;
                border-top: 1px solid #2c2c2c;
                min-height: 22px;
                max-height: 22px;
            }
            QLabel {
                color: #ecf0f1;
                padding: 2px 6px;
                border-right: 1px solid #2c2c2c;
                font-size: 11px;
                min-height: 20px;
                max-height: 20px;
            }
        """)
        
        # Create status widgets
        self.file_info = QLabel()
        self.cursor_pos = QLabel()
        self.line_count = QLabel()
        self.last_saved = QLabel()
        self.encoding = QLabel("UTF-8")
        
        # Add permanent widgets (from right to left)
        self.addPermanentWidget(self.encoding)
        self.addPermanentWidget(self.last_saved)
        self.addPermanentWidget(self.line_count)
        self.addPermanentWidget(self.cursor_pos)
        self.addPermanentWidget(self.file_info)
        
        # Initialize timer for updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
        
        self.last_save_time = None

    def update_file_info(self, filepath=None):
        if filepath:
            filename = os.path.basename(filepath)
            self.file_info.setText(f"File: {filename}")
        else:
            self.file_info.setText("No file opened")

    def update_cursor_position(self, line, column):
        self.cursor_pos.setText(f"Ln {line}, Col {column}")

    def update_line_count(self, count):
        self.line_count.setText(f"Lines: {count}")

    def update_last_saved(self):
        self.last_save_time = datetime.now()

    def update_status(self):
        # Update last saved time if available
        if self.last_save_time:
            delta = datetime.now() - self.last_save_time
            if delta.total_seconds() < 60:
                saved_text = "Saved less than a minute ago"
            elif delta.total_seconds() < 3600:
                minutes = int(delta.total_seconds() / 60)
                saved_text = f"Saved {minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                hours = int(delta.total_seconds() / 3600)
                saved_text = f"Saved {hours} hour{'s' if hours != 1 else ''} ago"
            self.last_saved.setText(saved_text)

    def handle_text_changed(self, text_edit):
        """Update status bar based on text editor changes"""
        # Update line count
        count = text_edit.document().blockCount()
        self.update_line_count(count)
        
        # Update cursor position
        cursor = text_edit.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.update_cursor_position(line, column)

    def handle_save(self, filepath):
        """Update status bar when file is saved"""
        self.update_last_saved()
        self.update_file_info(filepath)
