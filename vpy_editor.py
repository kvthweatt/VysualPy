import re, os, subprocess

from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QAction, QTextEdit, QMessageBox, QGraphicsView,
    QFileDialog, QInputDialog, QWidget, QVBoxLayout, QSizePolicy,
    QSplitter, QShortcut, QTabWidget
    )

from PyQt5.QtGui import (
    QIcon, QSyntaxHighlighter, QColor, QTextCharFormat, QFont, QBrush, QPainter,
    QFontMetrics, QKeySequence, QTextFormat
    )

from PyQt5.QtCore import (
    Qt, QSize, QRect, QTimer, pyqtSignal
    )

from vpy_config import ConfigManager, LanguageConfig
from vpy_menus import RecentFilesMenu, PreferencesDialog
from vpy_winmix import CustomWindowMixin

from vpy_blueprints import (
    BlueprintScene, BlueprintView, BlueprintGraphWindow,
    ExecutionScene, ExecutionView, ExecutionGraphWindow,
    BuildGraphScene, BuildGraphView, BuildGraphWindow
    )

from vpy_layout import IDELayout

class GlobalNodeTextEditor(QMainWindow, CustomWindowMixin):
    """Global text editor that tracks and displays all BuildableNodes."""
    
    def __init__(self, title="All Nodes Editor", parent=None):
        super().__init__(parent)
        self.tracked_nodes = []
        self.current_node_index = 0
        self.unsaved_changes = False
        
        self.setWindowTitle(f"Global Editor - {title}")
        self.setStyleSheet("QMainWindow { background: #2c3e50; color: white; }")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup custom title bar
        container, containerLayout, titleBar = self.setupCustomTitleBar(f"Global Node Editor - {title}")
        main_layout.addWidget(titleBar)
        
        # Create node selector
        from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel
        node_selector_widget = QWidget()
        node_selector_layout = QHBoxLayout(node_selector_widget)
        node_selector_layout.setContentsMargins(10, 5, 10, 5)
        
        node_label = QLabel("Current Node:")
        node_label.setStyleSheet("color: #95a5a6; font-weight: bold;")
        
        self.node_selector = QComboBox()
        self.node_selector.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                padding: 5px;
                border-radius: 3px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
            }
        """)
        self.node_selector.currentIndexChanged.connect(self.on_node_changed)
        
        node_selector_layout.addWidget(node_label)
        node_selector_layout.addWidget(self.node_selector)
        node_selector_layout.addStretch()
        
        main_layout.addWidget(node_selector_widget)
        
        # Create the code editor
        self.code_editor = CodeEditor()
        
        # Connect change detection
        self.code_editor.textChanged.connect(self.on_content_changed)
        
        main_layout.addWidget(self.code_editor)
        
        # Create button bar
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setContentsMargins(10, 5, 10, 10)
        button_layout.setSpacing(5)
        
        from PyQt5.QtWidgets import QPushButton
        
        button_row = QWidget()
        button_row_layout = QHBoxLayout(button_row)
        button_row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Save button
        self.save_button = QPushButton("Save & Sync Current Node")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.save_button.clicked.connect(self.save_current_node)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh Nodes")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_tracked_nodes)
        
        button_row_layout.addWidget(self.save_button)
        button_row_layout.addWidget(self.refresh_button)
        button_row_layout.addStretch()
        
        # Status label
        self.status_label = QWidget()
        self.status_label.setStyleSheet("color: #95a5a6; padding: 4px;")
        status_layout = QHBoxLayout(self.status_label)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        from PyQt5.QtWidgets import QLabel
        self.status_text = QLabel("No nodes tracked")
        self.status_text.setStyleSheet("color: #95a5a6;")
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        
        button_layout.addWidget(button_row)
        button_layout.addWidget(self.status_label)
        
        main_layout.addWidget(button_widget)
        
        # Set up window properties
        titleBar.mousePressEvent = self.titleBarMousePressEvent
        titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent
        
        self.setCentralWidget(central_widget)
        self.resize(900, 700)
        
        # Set focus to the code editor
        self.code_editor.setFocus()
        
        # Initial refresh
        self.refresh_tracked_nodes()
        
    def add_tracked_node(self, node):
        """Add a BuildableNode to be tracked by this editor."""
        if node not in self.tracked_nodes:
            self.tracked_nodes.append(node)
            # Register this editor with the node for synchronization
            if not hasattr(node, '_external_editors'):
                node._external_editors = []
            if self not in node._external_editors:
                node._external_editors.append(self)
            self.refresh_node_selector()
            
    def remove_tracked_node(self, node):
        """Remove a BuildableNode from tracking."""
        if node in self.tracked_nodes:
            self.tracked_nodes.remove(node)
            # Unregister from node
            if hasattr(node, '_external_editors') and self in node._external_editors:
                node._external_editors.remove(self)
            self.refresh_node_selector()
            
    def refresh_tracked_nodes(self):
        """Find and track all BuildableNodes in the scene."""
        # Clear current tracking
        for node in self.tracked_nodes[:]:
            self.remove_tracked_node(node)
        
        # Find all BuildableNodes in active scenes
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            for widget in app.allWidgets():
                # Check if this is a scene with BuildableNodes
                if hasattr(widget, 'items'):
                    for item in widget.items():
                        if hasattr(item, 'node_type') and hasattr(item.node_type, 'value'):
                            if item.node_type.value == 'buildable':
                                self.add_tracked_node(item)
        
        # Update status
        count = len(self.tracked_nodes)
        if count == 0:
            self.status_text.setText("No BuildableNodes found")
            self.status_text.setStyleSheet("color: #e74c3c;")
        else:
            self.status_text.setText(f"Tracking {count} BuildableNode(s)")
            self.status_text.setStyleSheet("color: #27ae60;")
            
    def refresh_node_selector(self):
        """Update the node selector dropdown."""
        self.node_selector.blockSignals(True)
        self.node_selector.clear()
        
        if self.tracked_nodes:
            for node in self.tracked_nodes:
                self.node_selector.addItem(f"{node.name} ({id(node)})")
            
            # Select current node or first one
            if self.current_node_index < len(self.tracked_nodes):
                self.node_selector.setCurrentIndex(self.current_node_index)
            else:
                self.current_node_index = 0
                self.node_selector.setCurrentIndex(0)
                
            self.load_current_node_content()
        else:
            self.code_editor.setPlainText("# No BuildableNodes to display")
            
        self.node_selector.blockSignals(False)
        
    def on_node_changed(self, index):
        """Handle node selection change."""
        if 0 <= index < len(self.tracked_nodes):
            # Save current node first if there are changes
            if self.unsaved_changes:
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    "Save changes to current node before switching?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                if reply == QMessageBox.Save:
                    self.save_current_node()
                elif reply == QMessageBox.Cancel:
                    # Revert selection
                    self.node_selector.blockSignals(True)
                    self.node_selector.setCurrentIndex(self.current_node_index)
                    self.node_selector.blockSignals(False)
                    return
                    
            self.current_node_index = index
            self.load_current_node_content()
            
    def load_current_node_content(self):
        """Load content from the currently selected node."""
        if 0 <= self.current_node_index < len(self.tracked_nodes):
            node = self.tracked_nodes[self.current_node_index]
            content = getattr(node, 'content', '') or getattr(node, 'full_content', '')
            self.code_editor.setPlainText(content)
            self.unsaved_changes = False
            self.update_status()
            
    def on_content_changed(self):
        """Handle content changes in the editor."""
        if 0 <= self.current_node_index < len(self.tracked_nodes):
            node = self.tracked_nodes[self.current_node_index]
            current_content = self.code_editor.toPlainText()
            original_content = getattr(node, 'content', '') or getattr(node, 'full_content', '')
            
            if current_content != original_content:
                self.unsaved_changes = True
                self.status_text.setText(f"● Unsaved changes to {node.name}")
                self.status_text.setStyleSheet("color: #f39c12;")
            else:
                self.unsaved_changes = False
                self.update_status()
                
    def save_current_node(self):
        """Save changes to the currently selected node."""
        if 0 <= self.current_node_index < len(self.tracked_nodes):
            node = self.tracked_nodes[self.current_node_index]
            new_content = self.code_editor.toPlainText()
            
            # Get original content for change processing
            original_content = getattr(node, 'content', '') or getattr(node, 'full_content', '')
            
            # Update the node's content
            node.content = new_content
            node.full_content = new_content
            
            # Process content change to trigger analysis and auto-generation
            if hasattr(node, 'process_content_change'):
                node.process_content_change(original_content, new_content)
            
            # Update visual representation
            node.update()
            
            # AUTOMATIC CONNECTION DETECTION: Analyze code references and create connections
            if hasattr(node, 'scene') and node.scene():
                scene = node.scene()
                if hasattr(scene, 'analyze_node_references'):
                    scene.analyze_node_references(node)
            
            # Update status
            self.unsaved_changes = False
            self.status_text.setText(f"✓ Saved {node.name}")
            self.status_text.setStyleSheet("color: #27ae60;")
            
            # Reset status after a delay
            QTimer.singleShot(2000, lambda: self.update_status())
            
    def update_status(self):
        """Update the status display."""
        if self.tracked_nodes:
            count = len(self.tracked_nodes)
            if 0 <= self.current_node_index < count:
                current_node = self.tracked_nodes[self.current_node_index]
                self.status_text.setText(f"Editing {current_node.name} ({self.current_node_index + 1}/{count})")
            else:
                self.status_text.setText(f"Tracking {count} node(s)")
            self.status_text.setStyleSheet("color: #95a5a6;")
        else:
            self.status_text.setText("No nodes tracked")
            self.status_text.setStyleSheet("color: #e74c3c;")
            
    def set_content(self, content):
        """Set content for external synchronization compatibility."""
        # This method is called by BuildableNode.sync_with_external_editors
        if 0 <= self.current_node_index < len(self.tracked_nodes):
            current_node = self.tracked_nodes[self.current_node_index]
            current_content = self.code_editor.toPlainText()
            
            # Only update if the content is for the currently displayed node
            # This prevents interference when multiple nodes are being synchronized
            if content != current_content:
                # Check if this content matches any of our tracked nodes
                for i, node in enumerate(self.tracked_nodes):
                    node_content = getattr(node, 'content', '') or getattr(node, 'full_content', '')
                    if content == node_content:
                        # This content belongs to one of our nodes
                        if i == self.current_node_index:
                            # It's the currently displayed node, update the editor
                            self.code_editor.blockSignals(True)
                            self.code_editor.setPlainText(content)
                            self.code_editor.blockSignals(False)
                            self.unsaved_changes = False
                            self.update_status()
                        break
                        
    def get_content(self):
        """Get content for external synchronization compatibility."""
        return self.code_editor.toPlainText()
        
    def closeEvent(self, event):
        """Handle window close event."""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_current_node()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
                return
        else:
            event.accept()
            
        # Clean up tracking
        for node in self.tracked_nodes[:]:
            self.remove_tracked_node(node)

class ExternalTextEditorDialog(QMainWindow, CustomWindowMixin):
    """External text editor dialog for BuildableNode editing."""
    
    def __init__(self, title="Code Editor", content="", node_reference=None, parent=None):
        super().__init__(parent)
        self.node_reference = node_reference
        self.original_content = content
        self.unsaved_changes = False
        
        self.setWindowTitle(f"External Editor - {title}")
        self.setStyleSheet("QMainWindow { background: #2c3e50; color: white; }")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup custom title bar
        container, containerLayout, titleBar = self.setupCustomTitleBar(f"Code Editor - {title}")
        main_layout.addWidget(titleBar)
        
        # Create the code editor
        self.code_editor = CodeEditor()
        self.code_editor.setPlainText(content)
        
        # Connect change detection
        self.code_editor.textChanged.connect(self.on_content_changed)
        
        main_layout.addWidget(self.code_editor)
        
        # Create button bar
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setContentsMargins(10, 5, 10, 10)
        button_layout.setSpacing(5)
        
        from PyQt5.QtWidgets import QPushButton, QHBoxLayout
        
        button_row = QWidget()
        button_row_layout = QHBoxLayout(button_row)
        button_row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Save button
        self.save_button = QPushButton("Save & Sync")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self.save_button.clicked.connect(self.save_and_sync)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_editing)
        
        button_row_layout.addWidget(self.save_button)
        button_row_layout.addWidget(self.cancel_button)
        button_row_layout.addStretch()
        
        # Status label
        self.status_label = QWidget()
        self.status_label.setStyleSheet("color: #95a5a6; padding: 4px;")
        status_layout = QHBoxLayout(self.status_label)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        from PyQt5.QtWidgets import QLabel
        self.status_text = QLabel("No changes")
        self.status_text.setStyleSheet("color: #95a5a6;")
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        
        button_layout.addWidget(button_row)
        button_layout.addWidget(self.status_label)
        
        main_layout.addWidget(button_widget)
        
        # Set up window properties
        titleBar.mousePressEvent = self.titleBarMousePressEvent
        titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent
        
        self.setCentralWidget(central_widget)
        self.resize(800, 600)
        
        # Set focus to the code editor
        self.code_editor.setFocus()
        
    def on_content_changed(self):
        """Handle content changes in the editor."""
        current_content = self.code_editor.toPlainText()
        if current_content != self.original_content:
            self.unsaved_changes = True
            self.status_text.setText("● Unsaved changes")
            self.status_text.setStyleSheet("color: #f39c12;")
            
            # Update window title to show unsaved changes
            title = self.windowTitle()
            if not title.endswith(" *"):
                self.setWindowTitle(title + " *")
        else:
            self.unsaved_changes = False
            self.status_text.setText("No changes")
            self.status_text.setStyleSheet("color: #95a5a6;")
            
            # Remove asterisk from title
            title = self.windowTitle()
            if title.endswith(" *"):
                self.setWindowTitle(title[:-2])
                
    def save_and_sync(self):
        """Save changes and synchronize with the BuildableNode."""
        new_content = self.code_editor.toPlainText()
        
        # Update the node if reference exists
        if self.node_reference:
            # Update the node's content
            self.node_reference.content = new_content
            self.node_reference.full_content = new_content
            
            # Process content change to trigger analysis and auto-generation
            if hasattr(self.node_reference, 'process_content_change'):
                self.node_reference.process_content_change(self.original_content, new_content)
            
            # Update visual representation
            self.node_reference.update()
            
        # Update original content and reset change status
        self.original_content = new_content
        self.unsaved_changes = False
        self.on_content_changed()  # Refresh status
        
        # Show success message briefly
        self.status_text.setText("✓ Saved and synchronized")
        self.status_text.setStyleSheet("color: #27ae60;")
        
        # Reset status after a delay
        QTimer.singleShot(2000, lambda: (
            self.status_text.setText("No changes"),
            self.status_text.setStyleSheet("color: #95a5a6;")
        ))
        
    def cancel_editing(self):
        """Cancel editing and close the dialog."""
        if self.unsaved_changes:
            # Ask for confirmation
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to close without saving?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
                
        self.close()
        
    def closeEvent(self, event):
        """Handle window close event."""
        if self.unsaved_changes:
            # Ask for confirmation
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_and_sync()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
                return
        else:
            event.accept()
            
    def get_content(self):
        """Get the current content of the editor."""
        return self.code_editor.toPlainText()
        
    def set_content(self, content):
        """Set the content of the editor."""
        self.code_editor.setPlainText(content)
        self.original_content = content
        self.unsaved_changes = False
        self.on_content_changed()

class CodeViewerWindow(QMainWindow, CustomWindowMixin):
    def __init__(self, title, content):
        super().__init__()
        self.setStyleSheet("QMainWindow { background: #2c3e50; color: white; }")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        container, containerLayout, titleBar = self.setupCustomTitleBar(title)
        main_layout.addWidget(titleBar)
        
        self.textEdit = QTextEdit()
        self.textEdit.setFont(QFont("Courier", 10))
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(content)
        self.textEdit.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ecf0f1;
                border: none;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        
        main_layout.addWidget(self.textEdit)
        
        titleBar.mousePressEvent = self.titleBarMousePressEvent
        titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent
        
        self.setCentralWidget(central_widget)
        self.resize(600, 400)

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, language_config=None):
        super().__init__(parent)
        self.colors = {
            'keyword': QColor("#FF6B6B"),
            'string': QColor("#98C379"), 
            'comment': QColor("#5C6370"),
            'function': QColor("#61AFEF"),
            'class': QColor("#E5C07B"),
            'number': QColor("#D19A66"),
            'decorator': QColor("#C678DD"),
        }
        self.lang_config = language_config or LanguageConfig()
        self.current_language = None
        self.styles = {}
        self.setup_default_format()
    
    def setup_default_format(self):
        self.load_language("Python")  # Default to Python
    
    def load_language(self, language_name):
        config = self.lang_config.get_language_by_name(language_name)
        if not config:
            return
            
        self.current_language = config
        self.setup_formats()
    
    def setup_formats(self):
        if not self.current_language:
            return
            
        self.styles = {}
        # Use self.colors as the source of truth for colors
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(self.colors['keyword'])
        keywords = self.current_language['keywords']
        self.styles['keyword'] = (keyword_format, '\\b(' + '|'.join(keywords) + ')\\b')
        
        # Other styles use colors from self.colors dictionary
        string_format = QTextCharFormat()
        string_format.setForeground(self.colors['string'])
        self.styles['string'] = (string_format, r'"[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\'')
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(self.colors['comment'])
        self.styles['comment'] = (comment_format, '#[^\n]*')
        
        function_format = QTextCharFormat()
        function_format.setForeground(self.colors['function'])
        self.styles['function'] = (function_format, '\\bdef\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\b')
        
        class_format = QTextCharFormat()
        class_format.setForeground(self.colors['class'])
        self.styles['class'] = (class_format, '\\bclass\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\b')
        
        number_format = QTextCharFormat()
        number_format.setForeground(self.colors['number'])
        self.styles['number'] = (number_format, '\\b[0-9]+\\b')
        
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(self.colors['decorator'])
        self.styles['decorator'] = (decorator_format, '@[a-zA-Z_][a-zA-Z0-9_]*')
    
    def highlightBlock(self, text):
        for style_name, (format, pattern) in self.styles.items():
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_config = LanguageConfig()
        self.highlighter = SyntaxHighlighter(self.document(), self.lang_config)
        
        # Load saved colors from config
        self.load_saved_colors()
        
        # Debug flag
        self.debug = True
        
        # Line Numbers
        self.line_number_area = LineNumberArea(self)
        
        # Configure scrollbars first
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Set viewport update mode for better performance
        self.setViewportMargins(self.line_number_area_width(), 5, 5, 5)
        
        # Set font and disable word wrap
        font = QFont("Courier New", 12)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QTextEdit.NoWrap)
        
        # Document setup
        doc = self.document()
        doc.setDocumentMargin(10)
        doc.setMaximumBlockCount(0)  # No limit on lines
        
        # Set text interaction flags
        self.setTextInteractionFlags(
            Qt.TextEditorInteraction | 
            Qt.TextSelectableByKeyboard | 
            Qt.TextSelectableByMouse
        )
        
        # Connect signals
        self.verticalScrollBar().rangeChanged.connect(self.handleScrollRangeChange)
        self.document().blockCountChanged.connect(self.update_line_number_area_width)
        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)
        self.textChanged.connect(self.handleTextChanged)
        
        # Apply styling
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ecf0f1;
                border: none;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #2c2c2c;
                width: 14px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: #2c2c2c;
            }
        """)

    def handleScrollRangeChange(self, min_val, max_val):
        """Handle scroll range changes to ensure proper document display"""
        scrollbar = self.verticalScrollBar()
        viewport_height = int(self.viewport().height())
        
        # Calculate proper document height
        doc = self.document()
        total_height = int(doc.size().height())
        
        # Set proper range and page step
        if total_height > viewport_height:
            scrollbar.setRange(0, int(total_height - viewport_height))
            scrollbar.setPageStep(viewport_height)
        else:
            scrollbar.setRange(0, 0)
            scrollbar.setPageStep(viewport_height)

    def handleTextChanged(self):
        """Handle text changes to ensure proper document layout"""
        doc = self.document()
        doc.adjustSize()
        layout = doc.documentLayout()
        layout.documentSizeChanged.emit(doc.size())

    def lineNumberAreaPaintEvent(self, event):
        """Paint the line number area."""
        try:
            painter = QPainter(self.line_number_area)
            painter.fillRect(event.rect(), QColor("#2b2b2b"))  # Dark background for line numbers

            # Set smaller font for line numbers
            font = self.font()
            # Ensure font size is always positive and reasonable
            current_size = font.pointSize()
            new_size = max(8, current_size - 1) if current_size > 0 else 10
            font.setPointSize(new_size)
            painter.setFont(font)

            block = self.document().firstBlock()
            block_number = block.blockNumber()
            viewport_offset = self.verticalScrollBar().value()
            page_bottom = viewport_offset + self.viewport().height()
            font_metrics = QFontMetrics(font)  # Use metrics of smaller font
            line_height = self.fontMetrics().height()  # Keep original line height for spacing

            # Adjust starting position based on visible blocks
            current_y = 0
            max_blocks = 1000  # Prevent infinite loops
            block_count = 0
            
            while block.isValid() and block_count < max_blocks:
                # Skip blocks that are above the visible area
                if current_y > page_bottom:
                    break

                if block.isVisible():
                    number = str(block_number + 1)
                    painter.setPen(QColor("#6c757d"))  # Grey color for line numbers
                    width = self.line_number_area_width()
                    
                    # Calculate vertical centering offset
                    font_height = font_metrics.height()
                    y_offset = (line_height - font_height) // 2  # Center the smaller font in the line
                    
                    # Only draw if the line is in the visible area
                    block_top = current_y - viewport_offset
                    if block_top >= -line_height and block_top <= self.viewport().height():
                        painter.drawText(0, block_top + y_offset, width - 5, font_height, 
                                      Qt.AlignRight | Qt.AlignVCenter, number)

                # Move to next block
                block = block.next()
                block_number += 1
                current_y += line_height
                block_count += 1
        except Exception as e:
            print(f"Error in lineNumberAreaPaintEvent: {e}")

    def line_number_area_width(self):
        """Calculate the width needed for the line number area."""
        digits = max(1, len(str(self.document().blockCount())))
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self):
        """Update the margins to accommodate the line number area."""
        self.setViewportMargins(self.line_number_area_width(), 5, 5, 5)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Update line number area
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(),
            cr.top(),
            self.line_number_area_width(),
            cr.height()
        )
        
        # Update document layout
        self.document().setTextWidth(self.viewport().width())
        
        # Force scroll range update
        self.handleScrollRangeChange(
            self.verticalScrollBar().minimum(),
            self.verticalScrollBar().maximum()
        )
        
    def go_to_line(self):
        """Open dialog to go to specific line number."""
        line_count = self.document().blockCount()
        line_number, ok = QInputDialog.getInt(
            self, 
            "Go to Line", 
            f"Enter line number (1-{line_count}):",
            1, 1, line_count
        )
        
        if ok:
            # Move cursor to the specified line
            cursor = self.textCursor()
            block = self.document().findBlockByLineNumber(line_number - 1)  # Convert to 0-based index
            cursor.setPosition(block.position())
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
            
            # Flash the line briefly to highlight it
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#3d3d3d"))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = cursor
            selection.cursor.clearSelection()
            
            # Apply the highlight
            self.setExtraSelections([selection])
            
            # Clear the highlight after a short delay
            QTimer.singleShot(1000, lambda: self.setExtraSelections([]))

    def handleCursorPosition(self):
        """Ensure cursor stays visible without aggressive snapping"""
        cursor = self.textCursor()
        scrollbar = self.verticalScrollBar()
        
        # Calculate cursor position in viewport coordinates
        cursor_rect = self.cursorRect(cursor)
        viewport_rect = self.viewport().rect()
        
        # Only scroll if cursor is outside visible area
        if not viewport_rect.contains(cursor_rect.center()):
            # Calculate the target scroll position
            if cursor_rect.top() < 0:
                # Cursor above viewport
                new_value = scrollbar.value() + cursor_rect.top()
            elif cursor_rect.bottom() > viewport_rect.height():
                # Cursor below viewport
                new_value = scrollbar.value() + cursor_rect.bottom() - viewport_rect.height()
            else:
                return
                
            # Apply scroll with bounds checking
            scrollbar.setValue(max(0, min(new_value, scrollbar.maximum())))

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            # Handle zoom
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            event.accept()
        else:
            # Normal scrolling
            super().wheelEvent(event)

    def load_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Temporarily disable updates
            self.setUpdatesEnabled(False)
            
            # Clear existing content and set new content
            self.clear()
            
            # Set the text directly
            self.setPlainText(content)
            
            # Force immediate layout update
            doc = self.document()
            doc.adjustSize()
            layout = doc.documentLayout()
            layout.documentSizeChanged.emit(doc.size())
            
            # Update scrollbar configuration
            self.handleScrollRangeChange(0, doc.size().height())
            
            # Reset view
            cursor = self.textCursor()
            cursor.movePosition(cursor.Start)
            self.setTextCursor(cursor)
            self.verticalScrollBar().setValue(0)
            
            # Re-enable updates and force refresh
            self.setUpdatesEnabled(True)
            self.viewport().update()
            
            return True
            
        except Exception as e:
            print(f"Error loading file: {e}")
            raise
    
    def load_saved_colors(self):
        """Load saved color preferences and apply to the highlighter."""
        try:
            config = ConfigManager()
            saved_config = config.load_config()
            saved_colors = saved_config.get('editor', {}).get('colors', {})
            
            if saved_colors:
                # Convert string colors to QColor objects and update highlighter
                for name, color_str in saved_colors.items():
                    if name in self.highlighter.colors:
                        color = QColor(color_str)
                        if color.isValid():
                            self.highlighter.colors[name] = color
                
                # Rebuild format objects with the new colors
                self.highlighter.setup_formats()
                
                # Trigger re-highlighting if there's content
                if self.toPlainText():
                    self.highlighter.rehighlight()
                    
        except Exception as e:
            print(f"Error loading saved colors: {e}")

class EditorTabs(QTabWidget):
    """Tabbed editor container that manages multiple CodeEditor instances."""
    
    # Signal emitted when the current editor changes
    currentEditorChanged = pyqtSignal(object)  # Emits CodeEditor instance or None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure tab widget
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.ElideRight)
        
        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_changed)
        
        # Apply dark theme styling consistent with existing UI
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #1a1a1a;
            }
            QTabBar::tab {
                background: #2b2b2b;
                color: #a9b7c6;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: #1a1a1a;
                border-bottom: 2px solid #2d5177;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #323232;
            }
            QTabBar::close-button {
                image: none;
                background: rgba(169, 183, 198, 0.3);
                border-radius: 6px;
                width: 12px;
                height: 12px;
                margin: 2px;
            }
            QTabBar::close-button:hover {
                background: rgba(255, 107, 107, 0.8);
            }
            QTabBar::close-button:pressed {
                background: rgba(255, 107, 107, 1.0);
            }
        """)
        
        # Track untitled file counter
        self.untitled_counter = 0
    
    def add_new_tab(self, content="", filepath=None, title=None):
        """Add a new tab with a CodeEditor.
        
        Args:
            content (str): Initial content for the editor
            filepath (str): File path if opening an existing file
            title (str): Custom tab title (will be derived from filepath if not provided)
        
        Returns:
            CodeEditor: The newly created editor instance
        """
        editor = self._create_code_editor()
        
        # Set initial content
        if content:
            editor.setPlainText(content)
        
        # Determine tab title
        if title:
            tab_title = title
        elif filepath:
            tab_title = os.path.basename(filepath)
        else:
            self.untitled_counter += 1
            tab_title = f"Untitled {self.untitled_counter}"
        
        # Add tab
        tab_index = self.addTab(editor, tab_title)
        
        # Store filepath in tab data
        editor.setProperty('filepath', filepath)
        editor.setProperty('is_dirty', False)
        
        # Connect text changed signal for dirty state tracking
        editor.textChanged.connect(lambda: self._mark_dirty(editor))
        
        # Set as current tab
        self.setCurrentIndex(tab_index)
        
        return editor
    
    def _create_code_editor(self):
        """Create a new CodeEditor with proper configuration."""
        editor = CodeEditor()
        
        # Set up Go to Line shortcut for this editor
        go_to_line_shortcut = QShortcut(QKeySequence("Ctrl+G"), editor)
        go_to_line_shortcut.activated.connect(editor.go_to_line)
        
        return editor
    
    def _mark_dirty(self, editor):
        """Mark an editor as dirty (unsaved changes)."""
        if not editor.property('is_dirty'):
            editor.setProperty('is_dirty', True)
            
            # Find the tab index for this editor
            for i in range(self.count()):
                if self.widget(i) == editor:
                    current_text = self.tabText(i)
                    if not current_text.endswith('*'):
                        self.setTabText(i, current_text + '*')
                    break
    
    def _mark_clean(self, editor):
        """Mark an editor as clean (saved)."""
        editor.setProperty('is_dirty', False)
        
        # Find the tab index for this editor and remove asterisk
        for i in range(self.count()):
            if self.widget(i) == editor:
                current_text = self.tabText(i)
                if current_text.endswith('*'):
                    self.setTabText(i, current_text[:-1])
                break
    
    def close_tab(self, index):
        """Close a tab at the given index."""
        if index < 0 or index >= self.count():
            return
        
        editor = self.widget(index)
        
        # Check if the editor has unsaved changes
        if editor.property('is_dirty'):
            filepath = editor.property('filepath') or f"Untitled {index + 1}"
            filename = os.path.basename(filepath) if filepath else filepath
            
            reply = QMessageBox.question(
                self, 'Unsaved Changes',
                f'The file "{filename}" has unsaved changes.\n\nDo you want to save before closing?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                # Try to save the file
                if hasattr(self.parent(), 'save_current_file'):
                    if not self.parent().save_current_file(editor):
                        return  # Save failed, don't close
                else:
                    return  # No save method available
            elif reply == QMessageBox.Cancel:
                return  # User cancelled, don't close
            # If Discard, continue with closing
        
        # Remove the tab
        self.removeTab(index)
        
        # Clean up the editor
        editor.deleteLater()
    
    def _on_current_changed(self, index):
        """Handle tab change to emit currentEditorChanged signal."""
        if index >= 0:
            editor = self.widget(index)
            self.currentEditorChanged.emit(editor)
        else:
            self.currentEditorChanged.emit(None)
    
    def current_editor(self):
        """Get the currently active CodeEditor."""
        current_widget = self.currentWidget()
        return current_widget if isinstance(current_widget, CodeEditor) else None
    
    def find_tab_by_filepath(self, filepath):
        """Find a tab index by its filepath.
        
        Returns:
            int: Tab index if found, -1 if not found
        """
        for i in range(self.count()):
            editor = self.widget(i)
            if editor.property('filepath') == filepath:
                return i
        return -1
    
    def get_all_editors(self):
        """Get all CodeEditor instances in tabs.
        
        Returns:
            list: List of (editor, filepath) tuples
        """
        editors = []
        for i in range(self.count()):
            editor = self.widget(i)
            filepath = editor.property('filepath')
            editors.append((editor, filepath))
        return editors
    
    def set_tab_filepath(self, editor, filepath):
        """Update the filepath for a tab and refresh the title."""
        editor.setProperty('filepath', filepath)
        
        # Update tab title
        for i in range(self.count()):
            if self.widget(i) == editor:
                filename = os.path.basename(filepath) if filepath else f"Untitled {i + 1}"
                is_dirty = editor.property('is_dirty')
                tab_title = filename + ('*' if is_dirty else '')
                self.setTabText(i, tab_title)
                break
        
        # Mark as clean since we're setting a new filepath (likely after save)
        self._mark_clean(editor)

class PythonIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.grid_size = 50
        self.recent_files_menu = RecentFilesMenu(self)
        # Will be set up by IDELayout.setup()
        self.editor_tabs = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Vysual Python IDE")
        self.setWindowIcon(QIcon("icon.svg"))
        
        # Create menu bar with existing menus
        menubar = self.createMenuBar()
        self.setMenuBar(menubar)
        
        # Set up the IDE layout with file browser and terminal
        # This creates self.editor_tabs and sets up the layout
        IDELayout.setup(self)
        
        # Configure window
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Initialize current file reference for backward compatibility
        self.currentFile = None
        
        # Create menus
        self.createMenus()
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QMenuBar {
                background: #3c3f41;
                color: #a9b7c6;
            }
            QMenuBar::item:selected {
                background: #2d5177;
            }
            QMenu {
                background-color: #3c3f41;
                color: #a9b7c6;
                border: 1px solid #2b2b2b;
            }
            QMenu::item:selected {
                background-color: #2d5177;
            }
            QDockWidget {
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(float.png);
            }
            QDockWidget::title {
                background: #3c3f41;
                color: #a9b7c6;
                padding-left: 5px;
                padding-top: 2px;
                padding-bottom: 2px;
            }
        """)
        
    def createMenuBar(self):
        menubar = QMenuBar()
        # [Rest of menu creation code remains the same]
        return menubar
    
    def createMenus(self):
        """Create all menus after layout is set up."""
        menubar = self.menuBar()
        
        # File menu
        fileMenu = menubar.addMenu("File")
        newAction = QAction("New File", self)
        openAction = QAction("Open File", self)
        saveAction = QAction("Save File", self)
        saveAsAction = QAction("Save File As", self)
        exitAction = QAction("Exit", self)

        newAction.triggered.connect(self.newFile)
        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        saveAsAction.triggered.connect(self.saveFileAs)
        exitAction.triggered.connect(self.close)

        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addMenu(self.recent_files_menu)
        fileMenu.addAction(exitAction)
        
        # Edit menu
        editMenu = menubar.addMenu("Edit")
        preferencesAction = QAction("Preferences", self)
        preferencesAction.triggered.connect(self.showPreferences)
        editMenu.addAction(preferencesAction)

        # View menu
        viewMenu = menubar.addMenu("View")
        bpgraphAction = QAction("Blueprint Graph", self)
        bpgraphAction.triggered.connect(self.showGraph)
        viewMenu.addAction(bpgraphAction)
        exgraphAction = QAction("Execution Graph", self)
        exgraphAction.triggered.connect(self.showExGraph)
        viewMenu.addAction(exgraphAction)
        bdgraphAction = QAction("Code Build Graph", self)
        bdgraphAction.triggered.connect(self.showBdGraph)
        viewMenu.addAction(bdgraphAction)

        # Run menu
        runMenu = menubar.addMenu("Run")
        runAction = QAction("Run Program", self)
        runAction.triggered.connect(self.runProgram)
        runMenu.addAction(runAction)

        # Help menu
        helpMenu = menubar.addMenu("Help")
        ideHelpAction = QAction("IDE Help", self)
        aboutAction = QAction("About", self)
        ideHelpAction.triggered.connect(self.showIDEHelp)
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(ideHelpAction)
        helpMenu.addAction(aboutAction)

    def toggleMaximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def titleBarMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def titleBarMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def newFile(self):
        """Create a new empty tab."""
        if self.editor_tabs:
            self.editor_tabs.add_new_tab()
        else:
            # Fallback for single editor mode
            self.textEdit.clear()
            self.currentFile = None

    def openFile(self):
        """Open a file dialog and load the selected file in a tab."""
        # Get supported extensions from language config
        supported_extensions = []
        lang_config = LanguageConfig()
        for lang_data in lang_config.languages.values():
            exts = lang_data['lang']['extensions']
            supported_extensions.extend(f"*.{ext}" for ext in exts)
        
        filter_str = "All Supported Files ({});;All Files (*)".format(" ".join(supported_extensions))
        
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", filter_str, options=options
        )
        
        if filePath:
            self.open_file_in_tab(filePath)

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def saveFile(self):
        """Save the current file using tab-aware methods."""
        if self.editor_tabs:
            # Use tab-aware save
            self.save_current_file()
        else:
            # Fallback for single editor mode
            if self.currentFile:
                with open(self.currentFile, 'w') as file:
                    file.write(self.textEdit.toPlainText())
            else:
                self.saveFileAs()

    def saveFileAs(self):
        """Save As dialog using tab-aware methods."""
        if self.editor_tabs:
            # Use tab-aware save as
            self.save_file_as()
        else:
            # Fallback for single editor mode
            options = QFileDialog.Options()
            filePath, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Python Files (*.py);;All Files (*)", options=options)
            if filePath:
                self.currentFile = filePath
                self.saveFile()
    
    def saveBlueprintWorkspace(self, scene):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Blueprint Workspace", "", 
                                                "Visual Python Blueprints (*.vpb);;All Files (*)", options=options)
        if filePath:
            try:
                # Add .vpb extension if not present
                if not filePath.endswith('.vpb'):
                    filePath += '.vpb'

                workspace_data = {
                    'boxes': [],
                    'connections': [],
                    'comments': []
                }

                # Save all boxes (DraggableRect items)
                for item in scene.items():
                    if isinstance(item, DraggableRect):
                        box_data = {
                            'name': item.name,
                            'content': item.full_content,
                            'x': item.scenePos().x(),
                            'y': item.scenePos().y(),
                            'width': item.rect().width(),
                            'height': item.rect().height(),
                            'is_class': item.is_class,
                            'id': str(id(item))
                        }
                        workspace_data['boxes'].append(box_data)

                    elif isinstance(item, CommentBox):
                        com_data = {
                            'name': item.name,
                            'x': item.scenePos().x(),
                            'y': item.scenePos().y(),
                            'width': item.rect().width(),
                            'height': item.rect().height(),
                            'id': str(id(item))
                        }
                        workspace_data['comments'].append(com_data)

                    elif isinstance(item, Connection):
                        if isinstance(item.start_point, ConnectionPoint) and isinstance(item.end_point, ConnectionPoint):
                            connection_data = {
                                'start_box': str(id(item.start_point.parentItem())),
                                'end_box': str(id(item.end_point.parentItem())),
                                'start_is_output': item.start_point.is_output,
                                'end_is_output': item.end_point.is_output
                            }
                            workspace_data['connections'].append(connection_data)

                with open(filePath, 'w') as f:
                    json.dump(workspace_data, f, indent=4)
                
                QMessageBox.information(self, "Success", "Blueprint workspace saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save workspace:\n{str(e)}", "Error", f"Failed to save workspace:\n{str(e)}")

    def loadBlueprintWorkspace(self, scene):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Load Blueprint Workspace", "", 
                                                "Visual Python Files (*.vpy);;Visual Python Blueprints (*.vpb);;All Files (*)", options=options)
        if filePath:
            try:
                with open(filePath, 'r') as f:
                    content = f.read()
                    if not content.strip():
                        raise ValueError("The blueprint file is empty")
                    workspace_data = json.loads(content)

                # Validate workspace data structure
                if not isinstance(workspace_data, dict) or 'boxes' not in workspace_data or 'connections' not in workspace_data:
                    raise ValueError("Invalid blueprint file format")

                workspace_data.setdefault('boxes', [])
                workspace_data.setdefault('connections', [])
                workspace_data.setdefault('comments', [])

                # Clear existing scene
                scene.clear()

                # Dictionary to map saved IDs to new box objects
                id_to_box = {}
                id_to_com = {}

                # Create all boxes first
                for box_data in workspace_data['boxes']:
                    try:
                        rect = DraggableRect(
                            box_data['name'],
                            box_data['content'],
                            float(box_data['x']),
                            float(box_data['y']),
                            float(box_data['width']),
                            float(box_data['height']),
                            box_data['is_class']
                        )
                        scene.addItem(rect)
                        id_to_box[box_data['id']] = rect
                    except KeyError as e:
                        QMessageBox.warning(self, "Warning", f"Skipping incomplete box data: missing {str(e)}")
                        continue

                for com_data in workspace_data['comments']:
                    try:
                        com = CommentBox(
                            com_data['name'],
                            float(com_data['x']),
                            float(com_data['y']),
                            float(com_data['width']),
                            float(com_data['height'])
                        )
                        scene.addItem(com)
                        id_to_com[com_data['id']] = com
                    except KeyError as e:
                        QMessageBox.warning(self, "Warning", f"Skipping incomplete comment data: missing {str(e)}")
                        continue

                # Create all connections
                for conn_data in workspace_data['connections']:
                    try:
                        start_box = id_to_box.get(conn_data['start_box'])
                        end_box = id_to_box.get(conn_data['end_box'])
                        
                        if start_box and end_box:
                            start_point = start_box.output_point if conn_data['start_is_output'] else start_box.input_point
                            end_point = end_box.output_point if conn_data['end_is_output'] else end_box.input_point
                            
                            connection = Connection(start_point, end_point.scenePos())
                            connection.setEndPoint(end_point)
                            scene.addItem(connection)
                    except KeyError as e:
                        QMessageBox.warning(self, "Warning", f"Skipping incomplete connection data: missing {str(e)}")
                        continue
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Failed to create connection: {str(e)}")
                        continue

                QMessageBox.information(self, "Success", "Blueprint workspace loaded successfully!")
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", "Invalid blueprint file format")
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load workspace:\n{str(e)}")

    def runProgram(self):
        """Run the current file from the active tab."""
        # Get current editor and filepath
        current_filepath = self.current_filepath()
        
        if current_filepath:
            # Save current file before running
            self.saveFile()
            try:
                self.terminal.clear_output()  # Clear previous output
                print(f"Running: {current_filepath}")
                result = subprocess.run(
                    ["python3", current_filepath], 
                    capture_output=True, 
                    text=True
                )
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
            except Exception as e:
                self.show_error_message(f"Failed to run the program:\n{e}")
        else:
            self.show_error_message("Please save the file before running.")
    
    def showExGraph(self):
        """Show the Execution Graph for the current tab."""
        current_editor = self.current_editor()
        current_filepath = self.current_filepath()
        
        if current_editor:
            code = current_editor.toPlainText()
            graph_window = ExecutionGraphWindow(None, code, current_filepath)
            graph_window.show()
        else:
            self.show_error_message("No file is currently open.")

    def showBdGraph(self):
        """Show the Build Graph for the current tab."""
        current_editor = self.current_editor()
        
        if current_editor:
            code = current_editor.toPlainText()
            # Store reference to prevent garbage collection
            self.build_graph_window = BuildGraphWindow(self, code)
            if not hasattr(self.build_graph_window, 'cancelled') or not self.build_graph_window.cancelled:
                # Position the window relative to the main IDE window
                ide_geometry = self.geometry()
                self.build_graph_window.move(ide_geometry.x() + 50, ide_geometry.y() + 50)
                self.build_graph_window.show()
        else:
            self.show_error_message("No file is currently open.")

    def showGraph(self):
        """Show the Blueprint Graph for the current tab."""
        current_editor = self.current_editor()
        
        if current_editor:
            code = current_editor.toPlainText()
            graph_window = BlueprintGraphWindow(None, code)
            graph_window.show()
            # Store reference to prevent garbage collection
            self.blueprint_window = graph_window
        else:
            self.show_error_message("No file is currently open.")

    def showPreferences(self):
        print("Opening preferences dialog")  # Debug print
        dialog = PreferencesDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # Apply saved preferences to the IDE
            self.apply_preferences_changes(dialog)
    
    def apply_preferences_changes(self, preferences_dialog):
        """Apply changes from preferences dialog to the IDE."""
        values = preferences_dialog.getValues()
        if not values:
            return
        
        try:
            # Apply color changes to all open editors
            if 'colors' in values:
                colors = values['colors']
                self.apply_color_changes_to_editors(colors)
                
            # Apply other changes as needed
            # (grid sizes, etc. can be applied when graph windows are opened)
            
        except Exception as e:
            print(f"Error applying preference changes: {e}")
    
    def apply_color_changes_to_editors(self, new_colors):
        """Apply new color settings to all open editors."""
        if not self.editor_tabs:
            return
            
        # Update each editor's syntax highlighter
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if hasattr(editor, 'highlighter') and editor.highlighter:
                # Update the colors dictionary
                editor.highlighter.colors.update(new_colors)
                # Rebuild the format objects with the new colors
                editor.highlighter.setup_formats()
                # Trigger re-highlighting
                editor.highlighter.rehighlight()

    def showIDEHelp(self):
        QMessageBox.information(self, "VysualPy IDE Help", "This is a blueprint-based IDE built with PyQt5 currently only supporting Python.\n\nMore detailed help will be available soon.\n\nPlease see https://github.com/kvthweatt/VysualPy for more help.")

    def showAbout(self):
        contributors = ["None yet."]
        contributors = '\n\t'.join(contributors)
        QMessageBox.about(self, "About", f"Python IDE\nVersion 1.0\nBuilt with Qt5\n\nWritten by Karac V. Thweatt - Open Source\n\nContributors:{contributors}")
        
    # Signal handler for editor tab changes
    def _on_current_editor_changed(self, editor):
        """Handle when the current editor tab changes."""
        # Update window title to reflect current file
        if editor:
            filepath = editor.property('filepath')
            if filepath:
                filename = os.path.basename(filepath)
                self.setWindowTitle(f"Vysual Python IDE - {filename}")
            else:
                self.setWindowTitle("Vysual Python IDE - Untitled")
        else:
            self.setWindowTitle("Vysual Python IDE")
    
    # Tab-aware helper methods
    def current_editor(self):
        """Get the currently active CodeEditor."""
        if self.editor_tabs:
            return self.editor_tabs.current_editor()
        return None
    
    def current_filepath(self):
        """Get the filepath of the currently active editor."""
        editor = self.current_editor()
        if editor:
            return editor.property('filepath')
        return None
    
    def set_current_filepath(self, filepath):
        """Update the filepath for the current tab."""
        editor = self.current_editor()
        if editor and self.editor_tabs:
            self.editor_tabs.set_tab_filepath(editor, filepath)
    
    def save_current_file(self, editor=None):
        """Save the specified editor (or current editor if None).
        
        Returns:
            bool: True if save succeeded, False otherwise
        """
        if not editor:
            editor = self.current_editor()
        
        if not editor:
            return False
        
        filepath = editor.property('filepath')
        
        if filepath:
            # File has a path, save it
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                
                # Mark as clean
                if self.editor_tabs:
                    self.editor_tabs._mark_clean(editor)
                
                return True
            except Exception as e:
                self.show_error_message(f"Error saving file: {e}")
                return False
        else:
            # No filepath, need to use Save As
            return self.save_file_as(editor)
    
    def save_file_as(self, editor=None):
        """Save As dialog for the specified editor (or current editor if None).
        
        Returns:
            bool: True if save succeeded, False otherwise
        """
        if not editor:
            editor = self.current_editor()
        
        if not editor:
            return False
        
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", 
            "Python Files (*.py);;All Files (*)", 
            options=options
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                
                # Update tab filepath and mark clean
                if self.editor_tabs:
                    self.editor_tabs.set_tab_filepath(editor, filepath)
                
                # Add to recent files
                self.recent_files_menu.add_recent_file(filepath)
                
                return True
            except Exception as e:
                self.show_error_message(f"Error saving file: {e}")
                return False
        
        return False
    
    def open_file_in_tab(self, filepath):
        """Open a file in a new tab or switch to existing tab if already open."""
        if not self.editor_tabs:
            return
        
        # Check if file is already open
        existing_tab_index = self.editor_tabs.find_tab_by_filepath(filepath)
        if existing_tab_index >= 0:
            # Switch to existing tab
            self.editor_tabs.setCurrentIndex(existing_tab_index)
            return
        
        # File not open, load it in a new tab
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add new tab
            editor = self.editor_tabs.add_new_tab(content=content, filepath=filepath)
            
            # Add to recent files
            self.recent_files_menu.add_recent_file(filepath)
            
        except Exception as e:
            self.show_error_message(f"Error opening file: {e}")
    
    def closeEvent(self, event):
        """Handle application close event to restore stdout"""
        # Check for unsaved changes in all tabs
        if self.editor_tabs:
            unsaved_files = []
            for editor, filepath in self.editor_tabs.get_all_editors():
                if editor.property('is_dirty'):
                    filename = os.path.basename(filepath) if filepath else "Untitled"
                    unsaved_files.append(filename)
            
            if unsaved_files:
                file_list = "\n  • ".join(unsaved_files)
                reply = QMessageBox.question(
                    self, 'Unsaved Changes',
                    f'The following files have unsaved changes:\n  • {file_list}\n\nDo you want to exit without saving?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    event.ignore()
                    return
        
        if hasattr(self, 'terminal') and self.terminal:
            self.terminal.restore_stdout()
        super().closeEvent(event)
