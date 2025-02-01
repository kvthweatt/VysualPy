import re, os

from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QAction, QTextEdit, QMessageBox, QGraphicsView,
    QFileDialog, QInputDialog, QWidget, QVBoxLayout, QSizePolicy
    )

from PyQt5.QtGui import (
    QIcon, QSyntaxHighlighter, QColor, QTextCharFormat, QFont, QBrush, QPainter
    )

from PyQt5.QtCore import (
    Qt
    )

from vpy_config import ConfigManager, LanguageConfig
from vpy_menus import RecentFilesMenu, PreferencesDialog

from vpy_blueprints import (
    BlueprintScene, BlueprintView, BlueprintGraphWindow,
    ExecutionScene, ExecutionView, ExecutionGraphWindow,
    BuildGraphScene, BuildGraphView, BuildGraphWindow
    )

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
        colors = self.current_language['colors']
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(colors['keyword']))
        keywords = self.current_language['keywords']
        self.styles['keyword'] = (keyword_format, '\\b(' + '|'.join(keywords) + ')\\b')
        
        # Other styles remain the same but use colors from config
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(colors['string']))
        self.styles['string'] = (string_format, r'"[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\'')
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(colors['comment']))
        self.styles['comment'] = (comment_format, '#[^\n]*')
        
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(colors['function']))
        self.styles['function'] = (function_format, '\\bdef\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\b')
        
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(colors['class']))
        self.styles['class'] = (class_format, '\\bclass\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\b')
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(colors['number']))
        self.styles['number'] = (number_format, '\\b[0-9]+\\b')
        
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor(colors['decorator']))
        self.styles['decorator'] = (decorator_format, '@[a-zA-Z_][a-zA-Z0-9_]*')
    
    def highlightBlock(self, text):
        for style_name, (format, pattern) in self.styles.items():
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)

class CodeEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_config = LanguageConfig()
        self.highlighter = SyntaxHighlighter(self.document(), self.lang_config)
        
        # Debug flag
        self.debug = True
        
        # Set font and basic properties
        self.setFont(QFont("Courier New", 12))
        self.setLineWrapMode(QTextEdit.NoWrap)
        
        # Enable scrollbars and configure them
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Configure document size limits
        self.document().setMaximumBlockCount(0)  # Disable block count limit
        
        # Set viewport margins to ensure text doesn't touch edges
        self.setViewportMargins(5, 5, 5, 5)
        
        # Set document margins
        doc = self.document()
        doc.setDocumentMargin(10)
        
        # Configure text interaction flags
        self.setTextInteractionFlags(
            Qt.TextEditorInteraction | 
            Qt.TextSelectableByKeyboard | 
            Qt.TextSelectableByMouse
        )
        
        # Style the scrollbars and editor
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ecf0f1;
                border: none;
                font-family: 'Courier New';
                font-size: 12px;
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
            QScrollBar:horizontal {
                border: none;
                background: #2c2c2c;
                height: 14px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #4a4a4a;
                min-width: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
    
    def load_file(self, filepath):
        if self.debug:
            print(f"\nDebug: Loading file: {filepath}")
        
        ext = os.path.splitext(filepath)[1]
        config = self.lang_config.get_language_config(ext)
        if config:
            self.highlighter.load_language(config['lang']['name'])
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if self.debug:
                    print(f"Debug: File size: {len(content)} bytes")
                    print(f"Debug: Number of lines: {len(content.splitlines())}")
                
                # Store content length for verification
                self._content_length = len(content)
                
                # Set the content
                self.setPlainText(content)
                
                if self.debug:
                    actual_text = self.toPlainText()
                    print(f"Debug: Editor content size: {len(actual_text)} bytes")
                    print(f"Debug: Editor number of lines: {len(actual_text.splitlines())}")
                    print(f"Debug: Document block count: {self.document().blockCount()}")
                    print(f"Debug: Vertical scrollbar range: {self.verticalScrollBar().minimum()} to {self.verticalScrollBar().maximum()}")
                
                # Move cursor to start
                cursor = self.textCursor()
                cursor.movePosition(cursor.Start)
                self.setTextCursor(cursor)
                self.ensureCursorVisible()
                
                # Reset scroll positions
                self.verticalScrollBar().setValue(0)
                self.horizontalScrollBar().setValue(0)
                
                # Force layout update
                self.document().adjustSize()
                self.updateGeometry()
                
                if self.debug:
                    print(f"Debug: Document size: {self.document().size()}")
                    print(f"Debug: Viewport size: {self.viewport().size()}")
                    
        except Exception as e:
            print(f"Error loading file: {e}")
            raise
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ensure document width matches viewport
        self.document().setTextWidth(self.viewport().width())
        if hasattr(self, '_content_length'):
            actual_text = self.toPlainText()
            if len(actual_text) != self._content_length:
                print(f"Debug: Content length mismatch after resize!")
                print(f"Debug: Expected {self._content_length}, got {len(actual_text)}")
    
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
            # Adjust scroll speed
            delta = event.angleDelta().y()
            scrollbar = self.verticalScrollBar()
            value = scrollbar.value()
            
            # Make scrolling smoother
            if abs(delta) > 120:  # High-resolution scroll events
                step = delta / 8
            else:
                step = delta / 2
                
            scrollbar.setValue(int(value - step))
            event.accept()
    
    def showEvent(self, event):
        super().showEvent(event)
        if self.debug:
            print("Debug: Editor shown")
            print(f"Debug: Current content size: {len(self.toPlainText())}")
            print(f"Debug: Visible blocks: {self.document().blockCount()}")

class PythonIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.grid_size = 50
        self.recent_files_menu = RecentFilesMenu(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Vysual Python IDE")
        self.setWindowIcon(QIcon("icon.svg"))
        
        # Create menu bar
        menubar = QMenuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: #34495e;
                color: white;
                padding: 4px;
            }
            QMenuBar::item:selected {
                background: #446380;
                border-radius: 4px;
            }
            QMenu {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
            }
            QMenu::item:selected {
                background-color: #446380;
            }
        """)
        
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

        self.setMenuBar(menubar)
        
        # Text editor
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.textEdit = CodeEditor()
        
        # Ensure the text editor can expand
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add editor to layout
        layout.addWidget(self.textEdit)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Configure window
        self.resize(1024, 768)
        self.setMinimumSize(400, 300)
        
        # Store current file reference
        self.currentFile = None
        
    def createMenuBar(self):
        menubar = QMenuBar()
        # [Rest of menu creation code remains the same]
        return menubar

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
        self.textEdit.clear()
        self.currentFile = None

    def openFile(self):
        options = QFileDialog.Options()
        supported_extensions = []
        for lang_config in self.textEdit.lang_config.languages.values():
            exts = lang_config['lang']['extensions']
            supported_extensions.extend(f"*.{ext}" for ext in exts)
        
        filter_str = "All Supported Files ({});;All Files (*)".format(" ".join(supported_extensions))
        
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", filter_str, options=options
        )
        
        if filePath:
            try:
                self.textEdit.load_file(filePath)
                self.currentFile = filePath
                self.recent_files_menu.add_recent_file(filePath)
                self.setWindowTitle(f"Vysual IDE - {filePath}")
            except Exception as e:
                self.show_error_message(f"Error opening file: {e}")

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def saveFile(self):
        if self.currentFile:
            with open(self.currentFile, 'w') as file:
                file.write(self.textEdit.toPlainText())
        else:
            self.saveFileAs()

    def saveFileAs(self):
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
        if self.currentFile:
            self.saveFile()  # Save the current file before running
            try:
                result = subprocess.run(["python3", self.currentFile], capture_output=True, text=True)
                QMessageBox.information(self, "Program Output", result.stdout + result.stderr)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to run the program:\n{e}")
        else:
            QMessageBox.warning(self, "Warning", "Please save the file before running.")

    def showExGraph(self):
        code = self.textEdit.toPlainText()
        graph_window = ExecutionGraphWindow(None, code, self.currentFile)
        graph_window.show()

    def showBdGraph(self):
        # Store reference to prevent garbage collection
        self.build_graph_window = BuildGraphWindow(self, self.textEdit.toPlainText())
        if not hasattr(self.build_graph_window, 'cancelled') or not self.build_graph_window.cancelled:
            # Position the window relative to the main IDE window
            ide_geometry = self.geometry()
            self.build_graph_window.move(ide_geometry.x() + 50, ide_geometry.y() + 50)
            self.build_graph_window.show()

    def showGraph(self):
        """Show the Blueprint Graph window"""
        graph_window = BlueprintGraphWindow(None, self.textEdit.toPlainText())
        graph_window.show()
        # Store reference to prevent garbage collection
        self.blueprint_window = graph_window

    def showPreferences(self):
        print("Opening preferences dialog")  # Debug print
        dialog = PreferencesDialog(self)
        dialog.exec_()

    def showIDEHelp(self):
        QMessageBox.information(self, "VysualPy IDE Help", "This is a blueprint-based IDE built with PyQt5 currently only supporting Python.\n\nMore detailed help will be available soon.\n\nPlease see https://github.com/kvthweatt/VysualPy for more help.")

    def showAbout(self):
        contributors = ["None yet."]
        contributors = '\n\t'.join(contributors)
        QMessageBox.about(self, "About", f"Python IDE\nVersion 1.0\nBuilt with Qt5\n\nWritten by Karac V. Thweatt - Open Source\n\nContributors:{contributors}")
