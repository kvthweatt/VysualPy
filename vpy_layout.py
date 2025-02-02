from PyQt5.QtWidgets import (
    QTreeView, QFileSystemModel, QDockWidget, QPlainTextEdit,
    QSplitter, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QStyle, QSizePolicy, QTabWidget, QLabel
)
from PyQt5.QtCore import Qt, QDir
import sys
import os

class ProjectBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create message widget for when no project is loaded
        self.message_widget = QWidget()
        message_layout = QVBoxLayout(self.message_widget)
        message_label = QLabel("No Project Open")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
            }
        """)
        message_layout.addWidget(message_label)
        
        # Create tree view for project files (initially hidden)
        self.tree_view = QTreeView()
        self.tree_view.setVisible(False)  # Hide initially
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
        
        # Add both widgets to layout
        self.layout.addWidget(self.message_widget)
        self.layout.addWidget(self.tree_view)
        
        # Connect signals
        self.tree_view.clicked.connect(self.on_file_clicked)
        
        # Track project state
        self.current_project = None
        
    def load_project(self, project_path):
        """Load a project from the given path."""
        if project_path and os.path.isdir(project_path):
            self.current_project = project_path
            index = self.model.index(project_path)
            self.tree_view.setRootIndex(index)
            self.message_widget.setVisible(False)
            self.tree_view.setVisible(True)
    
    def close_project(self):
        """Close the current project."""
        self.current_project = None
        self.tree_view.setVisible(False)
        self.message_widget.setVisible(True)
        
    def on_file_clicked(self, index):
        """Handle file click in project tree."""
        if not self.current_project:
            return
            
        path = self.model.filePath(index)
        if os.path.isfile(path):
            try:
                self.parent().parent().parent().open_file(path)
            except AttributeError:
                pass

class FileBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
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
            
        layout.addWidget(self.tree_view)
        
        # Connect signals
        self.tree_view.clicked.connect(self.on_file_clicked)
        
    def set_current_directory(self, path):
        index = self.model.index(path)
        self.tree_view.setRootIndex(index)
        
    def on_file_clicked(self, index):
        path = self.model.filePath(index)
        if os.path.isfile(path):
            try:
                self.parent().parent().parent().open_file(path)
            except AttributeError:
                pass

class BrowserTabs(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("File Management", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #2b2b2b;
                color: #a9b7c6;
                padding: 8px 12px;
                border: none;
            }
            QTabBar::tab:selected {
                background: #323232;
                border-bottom: 2px solid #2d5177;
            }
            QTabBar::tab:hover {
                background: #323232;
            }
        """)
        
        # Create browsers
        self.file_browser = FileBrowser()
        self.project_browser = ProjectBrowser()
        
        # Add browsers to tabs
        self.tab_widget.addTab(self.file_browser, "File Browser")
        self.tab_widget.addTab(self.project_browser, "Project Browser")
        
        self.setWidget(self.tab_widget)

class Terminal(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Output", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        
        # Create container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Create output text area with true black background
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #a9b7c6;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
            QScrollBar:vertical {
                background: #000000;
                width: 14px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #2b2b2b;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #000000;
                height: 14px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #2b2b2b;
                min-width: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
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
        
        # Create and set up the browser tabs
        ide_window.browser_tabs = BrowserTabs(ide_window)
        ide_window.browser_tabs.setMinimumWidth(200)
        ide_window.addDockWidget(Qt.LeftDockWidgetArea, ide_window.browser_tabs)
        
        # Create and set up the terminal
        ide_window.terminal = Terminal(ide_window)
        ide_window.terminal.setMinimumHeight(100)
        ide_window.addDockWidget(Qt.BottomDockWidgetArea, ide_window.terminal)
        
        # Redirect stdout to terminal
        sys.stdout = ide_window.terminal
        
        # Set the main splitter as the central widget
        ide_window.setCentralWidget(ide_window.main_splitter)
