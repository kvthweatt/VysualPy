from PyQt5.QtWidgets import (
    QTreeView, QFileSystemModel, QDockWidget, QPlainTextEdit,
    QSplitter, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QStyle, QSizePolicy
)
from PyQt5.QtCore import Qt, QDir
import sys
import os

class FileBrowser(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("File Browser", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create tree view for files
        self.tree_view = QTreeView()
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: none;
            }
            QTreeView::item:hover {
                background-color: #323232;
            }
            QTreeView::item:selected {
                background-color: #2d5177;
            }
        """)
        
        # Set up the file system model
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        
        # Configure the tree view
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(""))
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        
        # Hide unnecessary columns
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)
            
        self.setWidget(self.tree_view)
        
        # Connect signals
        self.tree_view.clicked.connect(self.on_file_clicked)
        
    def set_current_directory(self, path):
        index = self.model.index(path)
        self.tree_view.setRootIndex(index)
        
    def on_file_clicked(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            try:
                self.parent().open_file(path)
            except AttributeError:
                pass

class Terminal(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        
        # Create container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Create output text area
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        # Create toolbar with clear button
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        clear_button = QPushButton()
        clear_button.setIcon(self.style().standardIcon(QStyle.SP_DialogResetButton))
        clear_button.setToolTip("Clear Output")
        clear_button.clicked.connect(self.clear_output)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(clear_button)
        
        # Add widgets to layout
        layout.addWidget(self.output)
        layout.addWidget(toolbar)
        
        self.setWidget(container)
    
    def write(self, text):
        self.output.appendPlainText(text.rstrip())
        # Ensure the last line is visible
        self.output.moveCursor(self.output.textCursor().End)
        self.output.ensureCursorVisible()
    
    def clear_output(self):
        self.output.clear()

class IDELayout:
    @staticmethod
    def setup(ide_window):
        # Create the main splitter
        ide_window.main_splitter = QSplitter(Qt.Vertical)
        
        # Create the editor widget
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.addWidget(ide_window.textEdit)
        
        # Add the editor to the splitter
        ide_window.main_splitter.addWidget(editor_widget)
        
        # Create and set up the file browser
        ide_window.file_browser = FileBrowser(ide_window)
        ide_window.file_browser.setMinimumWidth(200)
        ide_window.addDockWidget(Qt.LeftDockWidgetArea, ide_window.file_browser)
        
        # Create and set up the terminal
        ide_window.terminal = Terminal(ide_window)
        ide_window.terminal.setMinimumHeight(100)
        ide_window.addDockWidget(Qt.BottomDockWidgetArea, ide_window.terminal)
        
        # Redirect stdout to terminal
        sys.stdout = ide_window.terminal
        
        # Set the main splitter as the central widget
        ide_window.setCentralWidget(ide_window.main_splitter)
