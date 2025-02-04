import re, os, subprocess

from PyQt5.QtWidgets import (
    QMainWindow, QMenuBar, QAction, QTextEdit, QMessageBox, QGraphicsView,
    QFileDialog, QInputDialog, QWidget, QVBoxLayout, QSizePolicy,
    QSplitter, QShortcut, QPlainTextEdit, QMenu
    )

from PyQt5.QtGui import (
    QIcon, QSyntaxHighlighter, QColor, QTextCharFormat, QFont, QBrush, QPainter,
    QFontMetrics, QKeySequence, QTextFormat
    )

from PyQt5.QtCore import (
    Qt, QSize, QRect, QPoint
    )

from vpy_config import ConfigManager, LanguageConfig
from vpy_menus import RecentFilesMenu, PreferencesDialog
from vpy_winmix import CustomWindowMixin
from vpy_layout import IDELayout
from vpy_assembler import AssemblyViewer
from vpy_statusbar import IDEStatusBar
from vpy_projects import ProjectManager, NewProjectDialog, ProjectTreeWidget

from vpy_blueprints import (
    BlueprintScene, BlueprintView, BlueprintGraphWindow,
    ExecutionScene, ExecutionView, ExecutionGraphWindow,
    BuildGraphScene, BuildGraphView, BuildGraphWindow
    )

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

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setMouseTracking(True)
        
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def mousePressEvent(self, event):
        line_number = self.editor.get_line_from_y(event.pos().y())
        self.editor.toggle_breakpoint(line_number)
        self.update()

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang_config = LanguageConfig()
        self.highlighter = SyntaxHighlighter(self.document(), self.lang_config)
        
        # Debug flag
        self.debug = True
        
        # Line Numbers and Breakpoints
        self.line_number_area = LineNumberArea(self)
        self.breakpoints = set()
        
        # Add F2 shortcut for breakpoints
        self.shortcut_breakpoint = QShortcut(QKeySequence("F2"), self)
        self.shortcut_breakpoint.activated.connect(self.toggle_breakpoint_current_line)
        
        # Configure scrollbars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Set viewport update mode and margins
        self.updateRequest.connect(self.update_line_number_area)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.update_line_number_area_width()
        
        # Set font and disable word wrap
        font = QFont("Courier New", 12)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        # Connect signals
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        # Apply styling
        self.setStyleSheet("""
            QPlainTextEdit {
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

        # Initial line highlight
        self.highlightCurrentLine()

    def get_line_from_y(self, y_pos):
        """Convert y coordinate to line number"""
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= y_pos:
            if y_pos <= bottom:
                return block_number + 1
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

        return block_number

    def toggle_breakpoint(self, line_number):
        """Toggle breakpoint for the given line number"""
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
        else:
            self.breakpoints.add(line_number)
        self.line_number_area.update()

    def toggle_breakpoint_current_line(self):
        """Toggle breakpoint for the current line"""
        cursor = self.textCursor()
        current_line = cursor.blockNumber() + 1
        self.toggle_breakpoint(current_line)

    def line_number_area_width(self):
        """Calculate width needed for line number area"""
        digits = len(str(self.blockCount()))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * max(2, digits)
        return space + 20  # Extra space for breakpoint circles

    def update_line_number_area_width(self):
        """Update the editor margins to accommodate line numbers"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Handle updates to the line number area"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        """Handle resize events to adjust line number area"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def setText(self, text):
        """Compatibility method to handle setText calls"""
        self.setPlainText(text)

    def text(self):
        """Compatibility method to handle text() calls"""
        return self.toPlainText()

    def lineNumberAreaPaintEvent(self, event):
        """Paint the line number area with line numbers and breakpoints"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2b2b2b"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        block_height = self.blockBoundingRect(block).height()
        font_metrics = self.fontMetrics()
        font_height = font_metrics.height()

        while block.isValid() and block_top <= event.rect().bottom():
            if block.isVisible() and block_top + block_height >= event.rect().top():
                number = str(block_number + 1)
                line_number = block_number + 1
                
                # Draw breakpoint if exists
                if line_number in self.breakpoints:
                    # Draw red circle for breakpoint
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor("#FF4444"))
                    circle_size = font_height - 4
                    circle_x = 4
                    circle_y = int(block_top) + 2
                    painter.drawEllipse(QRect(circle_x, circle_y, circle_size, circle_size))
                
                # Create a proper QRect for the line number text
                text_rect = QRect(
                    0,  # x
                    int(block_top),  # y
                    self.line_number_area.width() - 2,  # width
                    int(block_height)  # height
                )
                
                # Draw line number
                painter.setPen(QColor("#6c757d"))
                painter.drawText(text_rect, Qt.AlignRight | Qt.AlignVCenter, number)

            block = block.next()
            block_top = block_top + block_height
            block_number += 1

    def highlightCurrentLine(self):
        """Highlight the current line"""
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#252525")
            
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def get_breakpoints(self):
        """Return the current set of breakpoints"""
        return self.breakpoints.copy()

    def clear_breakpoints(self):
        """Clear all breakpoints"""
        self.breakpoints.clear()
        self.line_number_area.update()

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
        
        # Create menu bar with existing menus
        menubar = self.createMenuBar()
        self.setMenuBar(menubar)
        
        # Create text editor
        self.textEdit = CodeEditor()
        
        # Set up the IDE layout with file browser and terminal
        IDELayout.setup(self)

        self.status_bar = IDEStatusBar(self)
        self.setStatusBar(self.status_bar)
        
        # Configure window
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Initialize current file reference
        self.currentFile = None
        
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
        
        # File menu
        fileMenu = menubar.addMenu("File")
        fileMenu.setObjectName("FileMenu")
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
        self.setup_project_menu()
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
        asmAction = QAction("Assemble Program", self)
        asmAction.triggered.connect(self.showAssemblyView)
        runMenu.addAction(asmAction)

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

        # Connect text editor signals to status bar
        self.textEdit.textChanged.connect(lambda: self.status_bar.handle_text_changed(self.textEdit))
        self.textEdit.cursorPositionChanged.connect(lambda: self.status_bar.handle_text_changed(self.textEdit))
     
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
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", 
                                                "Python Files (*.py);;All Files (*)", options=options)
        if filePath:
            try:
                with open(filePath, 'r') as file:
                    self.textEdit.setText(file.read())
                self.currentFile = filePath
                self.setWindowTitle(f"Visual Python IDE - {filePath}")
                self.status_bar.handle_save(filePath)  # Initialize status bar with file info
                self.status_bar.handle_text_changed(self.textEdit)  # Update line count and cursor position
            except Exception as e:
                self.show_error_message(f"Error opening file: {e}")

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def saveFile(self):
        if self.currentFile:
            with open(self.currentFile, 'w') as file:
                file.write(self.textEdit.toPlainText())
            self.status_bar.handle_save(self.currentFile)
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
            self.saveFile()  # Save before running
            try:
                self.terminal.clear_output()  # Clear previous output
                print(f"Running: {self.currentFile}")
                result = subprocess.run(
                    ["python3", self.currentFile], 
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

    def showAssemblyView(self):
        """Show the Assembly View window"""
        try:
            code_text = self.textEdit.toPlainText()
            if not code_text.strip():
                self.show_error_message("No code to analyze. Please enter some Python code first.")
                return
                
            # Store reference to prevent garbage collection
            self.assembly_window = AssemblyViewer(self, code_text)
            
            # Position the window relative to the main IDE window
            ide_geometry = self.geometry()
            self.assembly_window.move(ide_geometry.x() + 60, ide_geometry.y() + 60)
            
            self.assembly_window.show()
        except Exception as e:
            self.show_error_message(f"Error showing assembly view: {str(e)}")
            import traceback
            print(f"Assembly view error details:\n{traceback.format_exc()}")

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

    def setup_project_menu(self):
        """Add project-related menu items to the File menu"""
        # Find the File menu
        fileMenu = None
        for menu in self.menuBar().findChildren(QMenu):
            if menu.title() == "File":
                fileMenu = menu
                break
        
        if not fileMenu:
            print("File menu not found")
            return

        # Add separator before project actions
        fileMenu.addSeparator()

        # Add New Project action
        newProjectAction = QAction("New Project...", self)
        newProjectAction.triggered.connect(
            lambda: self.browser_tabs.project_browser.create_new_project()
        )
        fileMenu.addAction(newProjectAction)

        # Add Open Project action
        openProjectAction = QAction("Open Project...", self)
        openProjectAction.triggered.connect(
            lambda: self.browser_tabs.project_browser.open_project()
        )
        fileMenu.addAction(openProjectAction)

        # Add Close Project action
        closeProjectAction = QAction("Close Project", self)
        closeProjectAction.triggered.connect(
            lambda: self.browser_tabs.project_browser.close_project()
        )
        fileMenu.addAction(closeProjectAction)

        # Add separator after project actions
        fileMenu.addSeparator()
