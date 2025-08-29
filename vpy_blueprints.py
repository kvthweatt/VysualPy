import ast, builtins, json

from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsView, QMainWindow, QWidget, QVBoxLayout, QMenuBar,
    QAction, QApplication, QInputDialog, QDialog, QFileDialog, QMessageBox, QMenu
    )

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen

from vpy_menus import PreferencesDialog
from vpy_winmix import CustomWindowMixin
from vpy_graph import (
    CommentBox, DraggableRect, ExecutionDraggableRect, BuildableNode
    )
from vpy_connection import Connection, ConnectionPoint

class BlueprintScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.connection_in_progress = None
        self.active_connection_point = None

    def mouseMoveEvent(self, event):
        if self.connection_in_progress:
            self.connection_in_progress.end_pos = event.scenePos()
            self.connection_in_progress.updatePath()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.connection_in_progress:
            items = self.items(event.scenePos())
            valid_connection = False
            
            for item in items:
                if isinstance(item, ConnectionPoint):
                    if item.is_output != self.active_connection_point.is_output:
                        # Connect the points
                        self.connection_in_progress.setEndPoint(item)
                        valid_connection = True
                        break
            
            if not valid_connection:
                self.removeItem(self.connection_in_progress)
                # Clear the connection reference from the start point
                if self.active_connection_point:
                    self.active_connection_point.connection = None
            
            self.connection_in_progress = None
            self.active_connection_point = None
            
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Only show context menu if clicking on empty space
            items = self.items(event.scenePos())
            if not items:  # If no items under cursor
                self.showContextMenu(event)
        super().mousePressEvent(event)

    def showContextMenu(self, event):
        menu = QMenu()
        addCommentAction = menu.addAction("Add Comment Box")
        
        # Convert scene position to global position for the menu
        view = self.views()[0]  # Get the view this scene is in
        global_pos = view.mapToGlobal(view.mapFromScene(event.scenePos()))
        
        # Store scene position for later use
        scene_pos = event.scenePos()
        
        # Show menu and handle action
        action = menu.exec_(global_pos)
        if action == addCommentAction:
            name, ok = QInputDialog.getText(None, "New Comment Box", 
                                          "Enter comment box name:")
            if ok and name:
                comment_box = CommentBox(name, scene_pos.x(), scene_pos.y())
                self.addItem(comment_box)

class BlueprintView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)  # Enable rubber band selection
        self.panning = False
        self.last_mouse_pos = None
        
        # Grid settings
        self.grid_size = 50
        self.grid_color = QColor(60, 60, 60)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.scene().selectedItems():
                if isinstance(item, CommentBox):
                    self.scene().removeItem(item)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        items = self.scene().items(self.mapToScene(event.pos()))
        for item in items:
            if isinstance(item, ConnectionPoint):
                self.setDragMode(QGraphicsView.NoDrag)
                super().mousePressEvent(event)
                return
                
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.AltModifier:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if self.panning and self.last_mouse_pos is not None:
            delta = event.pos() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_mouse_pos = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.panning:
            self.panning = False
            self.last_mouse_pos = None
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.RubberBandDrag)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        # Get the visible area in scene coordinates
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        
        # Calculate grid boundaries
        left = int(visible_rect.left() - (visible_rect.left() % self.grid_size))
        top = int(visible_rect.top() - (visible_rect.top() % self.grid_size))
        right = int(visible_rect.right())
        bottom = int(visible_rect.bottom())
        
        # Create a pen for the grid lines
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Draw vertical lines
        x = left
        while x <= right:
            painter.drawLine(x, top, x, bottom)
            x += self.grid_size
            
        # Draw horizontal lines
        y = top
        while y <= bottom:
            painter.drawLine(left, y, right, y)
            y += self.grid_size

    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.scale(1.1, 1.1)
            elif delta < 0:
                self.scale(0.9, 0.9)
        else:
            super().wheelEvent(event)

class BlueprintGraphWindow(QMainWindow, CustomWindowMixin):
    def __init__(self, parent=None, code_text=""):
        super().__init__()  # Don't pass parent to keep window independent
        self.setWindowFlags(Qt.Window)  # Make it an independent window
        super().__init__(parent)
        self.setStyleSheet("QMainWindow { background: #2c3e50; color: white; }")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.grid_size = 50
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup title bar
        container, containerLayout, titleBar = self.setupCustomTitleBar("Blueprint Graph")
        main_layout.addWidget(titleBar)
        
        # Menu bar
        self.menuBar = QMenuBar()
        self.menuBar.setStyleSheet("""
            QMenuBar {
                background: #34495e;
                color: white;
                padding: 4px;
                border: none;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 8px;
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
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #446380;
            }
        """)
        
        fileMenu = self.menuBar.addMenu("File")
        viewMenu = self.menuBar.addMenu("View")
        
        saveAction = QAction("Save Graph", self)
        saveAction.triggered.connect(self.saveBlueprintWorkspace)
        fileMenu.addAction(saveAction)
        
        loadAction = QAction("Load Graph", self)
        loadAction.triggered.connect(self.loadBlueprintWorkspace)
        fileMenu.addAction(loadAction)

        addCommentAction = QAction("Add Comment Box", self)
        addCommentAction.triggered.connect(lambda: self.addCommentBoxToScene(self.scene))
        viewMenu.addAction(addCommentAction)
        
        PreferencesAction = QAction("Preferences", self)
        PreferencesAction.triggered.connect(self.showPreferences)
        viewMenu.addAction(PreferencesAction)

        resetViewAction = QAction("Reset View", self)
        resetViewAction.triggered.connect(self.reset_view)
        viewMenu.addAction(resetViewAction)

        optimizeAction = QAction("Optimize Layout", self)
        optimizeAction.triggered.connect(self.optimize_layout)
        viewMenu.addAction(optimizeAction)
        
        main_layout.addWidget(self.menuBar)

        # Scene and view
        self.scene = BlueprintScene()
        self.view = BlueprintView(self.scene)
        self.view.grid_size = self.grid_size
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        main_layout.addWidget(self.view)

        self.setCentralWidget(central_widget)
        self.resize(800, 600)
        
        # Handle window movement
        titleBar.mousePressEvent = self.titleBarMousePressEvent
        titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent

        # Create nodes from code
        self.create_nodes_from_code(code_text)

    def showPreferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.getValues()
            self.grid_size = values['grid_size']
            self.updateGridSize()

    def updateGridSize(self):
        if hasattr(self, 'view'):
            self.view.grid_size = self.grid_size
            self.view.viewport().update()
            
            # Update grid size for all items
            for item in self.scene.items():
                if isinstance(item, DraggableRect):
                    item.grid_size = self.grid_size
                    item.setPos(
                        item.snapToGrid(item.pos().x()),
                        item.snapToGrid(item.pos().y())
                    )

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
                            scene,
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
                            
                            connection = Connection(start_point, end_point.scenePos(), self.scene)
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

    def addCommentBoxToScene(self, scene):
        name, ok = QInputDialog.getText(None, "New Comment Box", 
                                      "Enter comment box name:")
        if ok and name:
            # Create the comment box at a reasonable default position
            comment_box = CommentBox(name, 100, 100)
            scene.addItem(comment_box)

    def optimize_layout(self):
        optimizer = GraphLayoutOptimizer(self.scene)
        optimizer.optimize()

    def reset_view(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.scale(0.9, 0.9)

    def create_nodes_from_code(self, code):
        y_offset = 0
        current_block = []
        current_block_type = None

        for line in code.splitlines():
            stripped = line.strip()
            
            if stripped.startswith("class "):
                if current_block:
                    y_offset = self.add_code_block(current_block_type, current_block, "class", y_offset)
                class_name = stripped.split()[1].split('(')[0]
                current_block = [line]
                current_block_type = class_name

            elif stripped.startswith(("def ", "async def ")):
                if current_block:
                    y_offset = self.add_code_block(current_block_type, current_block, "function", y_offset)
                func_name = stripped.split()[1 if stripped.startswith("def") else 2].split('(')[0]
                current_block = [line]
                current_block_type = func_name

            elif stripped:
                if not current_block_type:
                    current_block_type = "Global"
                current_block.append(line)

        if current_block:
            self.add_code_block(current_block_type, current_block, "global", y_offset)

    def add_code_block(self, name, block_lines, block_type, y_offset):
        content = "\n".join(block_lines)
        rect = None
        
        if block_type is None:
            rect = DraggableRect("Global", content, 0, y_offset, 400, 250, self.scene, is_class=False)
        elif block_type == "class":
            rect = DraggableRect(name, content, 0, y_offset, 400, 250, self.scene, is_class=True)
        elif block_type == "function":
            rect = DraggableRect(name, content, 0, y_offset, 400, 250, self.scene, is_class=False)
        
        if rect:
            self.scene.addItem(rect)
        return y_offset + 270

    def create_graph_nodes(self, code, scene):
        y_offset = 0
        current_block = []
        current_block_type = None

        for line in code.splitlines():
            stripped = line.strip()
            
            if stripped.startswith("class "):
                if current_block:
                    y_offset = self.add_code_block(current_block_type, current_block, "class", scene, y_offset)
                class_name = stripped.split()[1].split('(')[0]
                current_block = [line]
                current_block_type = class_name

            elif stripped.startswith(("def ", "async def ")):
                if current_block:
                    y_offset = self.add_code_block(current_block_type, current_block, "function", scene, y_offset)
                func_name = stripped.split()[1 if stripped.startswith("def") else 2].split('(')[0]
                current_block = [line]
                current_block_type = func_name

            elif stripped:
                if not current_block_type:
                    current_block_type = "Global"
                current_block.append(line)

        if current_block:
            self.add_code_block(current_block_type, current_block, "global", scene, y_offset)

class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.execution_flow = {}
        self.current_function = None
        self.current_class = None
        self.builtins = set(dir(builtins))
        self.returns = set()
        self.assignments = {}
        self.value_sources = {}
        self.conditional_calls = set()
        self.call_stack = []
        self.in_conditional = False
        self.unique_calls = {}  # Track unique instances of calls
        self.call_counter = {}  # Counter for each function name
        self.excluded_calls = {
            'int', 'str', 'len', 'print', 'list', 'dict', 'set',
            'append', 'extend', 'pop', 'remove', 'clear', 'sort',
            'items', 'keys', 'values', 'split', 'join', 'strip',
            'replace', 'format', 'startswith', 'endswith', 'find',
            'encode', 'decode', 'Embed', 'reverse', 'Decimal', 'bool', 'json',
            'lower', 'upper', 'items', 'QApplication',
            'QMainWindow', 'QTextEdit', 'QAction', 'QFileDialog', 'QMessageBox',
            'QGraphicsView', 'QGraphicsScene', 'QGraphicsRectItem',
            'QGraphicsTextItem', 'QGraphicsPathItem', 'QGraphicsEllipseItem',
            'QMenu', 'QInputDialog', 'QDialog', 'QVBoxLayout', 'QHBoxLayout',
            'QLabel', 'QSlider', 'QSpinBox', 'QPushButton', 'QGroupBox',
            'QWidget', 'QFrame', 'QMenuBar', 'QGraphicsItem', 'QGridLayout',
            'QComboBox', 'QColorDialog', 'QTabWidget', 'QLineEdit', 'QListWidget',
            'QWidget', 'QHBoxLayout', 'QIcon', 'QLabel', 'QPushButton', 'QAction',
            'QListWidget', 'QFileDialog'
        }

    def should_include_call(self, func_name):
        """Determine if a function call should be included in the graph."""
        # Extract base name for attribute calls (e.g., 'string.format' -> 'format')
        base_name = func_name.split('.')[-1]
        return base_name not in self.excluded_calls
        
    def visit_Module(self, node):
        self.execution_flow['global'] = set()
        self.current_function = 'global'
        self.generic_visit(node)
        
    def visit_If(self, node):
        old_conditional = self.in_conditional
        self.in_conditional = True
        self.visit(node.test)
        for item in node.body:
            self.visit(item)
        for item in node.orelse:
            self.visit(item)
        self.in_conditional = old_conditional
        
    def visit_While(self, node):
        old_conditional = self.in_conditional
        self.in_conditional = True
        self.generic_visit(node)
        self.in_conditional = old_conditional
        
    def visit_For(self, node):
        old_conditional = self.in_conditional
        self.in_conditional = True
        self.generic_visit(node)
        self.in_conditional = old_conditional
        
    def visit_Call(self, node):
        if not self.current_function:
            return
            
        called = self.get_callable_name(node.func)
        if not called or not self.should_include_call(called):
            return

        # Create unique name for this call instance
        unique_name = self.get_unique_name(called, node.lineno)
        
        # Store original name for reference
        self.unique_calls[unique_name] = {
            'original_name': called,
            'lineno': node.lineno,
            'in_conditional': self.in_conditional
        }

        # Initialize entry in execution flow
        if unique_name not in self.execution_flow:
            self.execution_flow[unique_name] = set()

        # Handle nested calls
        if self.call_stack:
            parent_call = self.call_stack[-1]
            if parent_call not in self.execution_flow:
                self.execution_flow[parent_call] = set()
            self.execution_flow[parent_call].add(unique_name)
            
            if self.in_conditional:
                self.conditional_calls.add((parent_call, unique_name))
        else:
            # Only add to current function's flow if not nested
            self.execution_flow[self.current_function].add(unique_name)
            if self.in_conditional:
                self.conditional_calls.add((self.current_function, unique_name))

        self.call_stack.append(unique_name)
        
        # Visit arguments to handle nested calls
        for arg in node.args:
            self.visit(arg)
        for keyword in node.keywords:
            self.visit(keyword.value)
        
        self.call_stack.pop()

    def get_unique_name(self, base_name, lineno):
        key = f"{base_name}_{lineno}"
        if key not in self.call_counter:
            self.call_counter[key] = 0
        else:
            self.call_counter[key] += 1
        count = self.call_counter[key]
        return f"{base_name}_{lineno}_{count}" if count > 0 else f"{base_name}_{lineno}"
        
    def get_callable_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return None
        
    def handle_function(self, node, is_async=False):
        name = node.name
        if hasattr(node, 'parent_class'):
            name = f"{node.parent_class}.{name}"
        elif is_async:
            name = f"async {name}"
            
        if name not in self.execution_flow:
            self.execution_flow[name] = set()
            
        prev_function = self.current_function
        self.current_function = name
        
        self.generic_visit(node)
        self.current_function = prev_function
        
    def visit_FunctionDef(self, node):
        self.handle_function(node)
        
    def visit_AsyncFunctionDef(self, node):
        self.handle_function(node, is_async=True)
        
    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call):
            called = self.get_callable_name(node.value.func)
            if called:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.assignments[target.id] = called
                        if called not in self.execution_flow:
                            self.execution_flow[called] = set()
                        self.execution_flow[called].add(f"RETURN_TO_{self.current_function}")
        self.generic_visit(node)

    def visit_Return(self, node):
        if self.current_function:
            self.returns.add(self.current_function)
            if node.value:
                if isinstance(node.value, ast.Call):
                    called = self.get_callable_name(node.value.func)
                    if called:
                        if called not in self.execution_flow:
                            self.execution_flow[called] = set()
                        self.execution_flow[called].add(f"RETURN_TO_{self.current_function}")
                elif isinstance(node.value, ast.Name) and node.value.id in self.assignments:
                    source = self.assignments[node.value.id]
                    if source in self.execution_flow:
                        self.execution_flow[source].add(f"RETURN_TO_{self.current_function}")

class ExecutionScene(BlueprintScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor(25, 25, 35)))  # Slightly different dark background

class ExecutionView(BlueprintView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)

class ExecutionGraphWindow(QMainWindow, CustomWindowMixin):
    def __init__(self, parent=None, code_text="", current_file=None):
        super().__init__(parent)
        self.setStyleSheet("QMainWindow { background: #2c3e50; color: white; }")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.currentFile = current_file
        self.grid_size = 50
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup title bar
        container, containerLayout, titleBar = self.setupCustomTitleBar("Execution Graph")
        main_layout.addWidget(titleBar)
        
        # Menu bar
        self.menuBar = QMenuBar()
        self.menuBar.setStyleSheet("""
            QMenuBar {
                background: #34495e;
                color: white;
                padding: 4px;
                border: none;
            }
            QMenuBar::item {
                background: transparent;
                padding: 4px 8px;
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
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #446380;
            }
        """)
        
        fileMenu = self.menuBar.addMenu("File")
        viewMenu = self.menuBar.addMenu("View")
        
        saveAction = QAction("Save Graph", self)
        saveAction.triggered.connect(self.save_graph)
        fileMenu.addAction(saveAction)
        
        loadAction = QAction("Load Graph", self)
        loadAction.triggered.connect(self.load_graph)
        fileMenu.addAction(loadAction)

        addCommentAction = QAction("Add Comment Box", self)
        addCommentAction.triggered.connect(lambda: self.addCommentBoxToScene(self.scene))
        viewMenu.addAction(addCommentAction)
        
        PreferencesAction = QAction("Preferences", self)
        PreferencesAction.triggered.connect(self.showPreferences)
        viewMenu.addAction(PreferencesAction)

        resetViewAction = QAction("Reset View", self)
        resetViewAction.triggered.connect(self.reset_view)
        viewMenu.addAction(resetViewAction)

        optimizeAction = QAction("Optimize Layout", self)
        optimizeAction.triggered.connect(self.optimize_layout)
        viewMenu.addAction(optimizeAction)
        
        main_layout.addWidget(self.menuBar)
        
        # Scene and view
        self.scene = ExecutionScene()
        self.view = ExecutionView(self.scene)
        main_layout.addWidget(self.view)
        
        self.setCentralWidget(central_widget)
        self.resize(800, 600)
        
        titleBar.mousePressEvent = self.titleBarMousePressEvent
        titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent
        
        self.create_execution_nodes(code_text)
        
    def addCommentBoxToScene(self, scene):
        name, ok = QInputDialog.getText(None, "New Comment Box", 
                                      "Enter comment box name:")
        if ok and name:
            # Create the comment box at a reasonable default position
            comment_box = CommentBox(name, 100, 100)
            scene.addItem(comment_box)

    def create_menus(self):
        """Create the menu bar for the execution graph window."""
        # File menu
        fileMenu = self.menubar.addMenu("File")
        
        saveAction = QAction("Save Graph", self)
        saveAction.triggered.connect(self.save_graph)
        fileMenu.addAction(saveAction)
        
        loadAction = QAction("Load Graph", self)
        loadAction.triggered.connect(self.load_graph)
        fileMenu.addAction(loadAction)
        
        # View menu
        viewMenu = self.menubar.addMenu("View")
        
        resetViewAction = QAction("Reset View", self)
        resetViewAction.triggered.connect(self.reset_view)
        viewMenu.addAction(resetViewAction)
        
        # Layout menu
        layoutMenu = self.menubar.addMenu("Layout")
        
        optimizeAction = QAction("Optimize Layout", self)
        optimizeAction.triggered.connect(self.optimize_layout)
        layoutMenu.addAction(optimizeAction)

    def showPreferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            values = dialog.getValues()
            self.grid_size = values['grid_size']
            self.updateGridSize()

    def updateGridSize(self):
            # Update grid size in execution view
            if hasattr(self, 'view') and isinstance(self.view, BlueprintView):
                self.view.grid_size = self.grid_size
                self.view.viewport().update()
                
                # Update grid size for all items
                for item in self.scene.items():
                    if isinstance(item, (DraggableRect, ExecutionDraggableRect)):
                        item.grid_size = self.grid_size
                        item.setPos(
                            item.snapToGrid(item.pos().x()),
                            item.snapToGrid(item.pos().y())
                        )

    def optimize_layout(self):
        """Re-run the layout optimization."""
        optimizer = GraphLayoutOptimizer(self.scene)
        optimizer.optimize()
        return

    def reset_view(self):
        """Reset the view to show all items."""
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.scale(0.9, 0.9)
        return

    def create_execution_graph(self, code_text):
        try:
            visitor = FunctionCallVisitor()
            tree = ast.parse(code_text)
            visitor.visit(tree)
            return visitor.execution_flow
        except Exception as e:
            print(f"Error parsing code: {e}")
            return {}

    def save_graph(self):
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Execution Graph", "", "Execution Graph (*.veg)", options=options)
            if filepath:
                graph_data = {
                    'nodes': [],
                    'connections': []
                }
                
                for item in self.scene.items():
                    if isinstance(item, ExecutionDraggableRect):
                        node_data = {
                            'name': item.name,
                            'content': item.full_content,
                            'x': item.pos().x(),
                            'y': item.pos().y(),
                            'is_class': item.is_class,
                            'has_return': any(isinstance(conn, Connection) and 
                                            conn.pen().color().name() == '#ff00ff' 
                                            for conn in item.output_point.connections)
                        }
                        graph_data['nodes'].append(node_data)
                    elif isinstance(item, Connection):
                        if isinstance(item.start_point, ConnectionPoint) and isinstance(item.end_point, ConnectionPoint):
                            color_name = item.pen().color().name().lower()
                            conn_type = 'normal'
                            if color_name == '#ff00ff':  # Magenta
                                conn_type = 'return'
                            elif color_name == '#ffa500':  # Orange
                                conn_type = 'conditional'
                            
                            conn_data = {
                                'start_node': item.start_point.parentItem().name,
                                'end_node': item.end_point.parentItem().name,
                                'type': conn_type
                            }
                            graph_data['connections'].append(conn_data)
                            
                with open(filepath, 'w') as f:
                    json.dump(graph_data, f, indent=4)
                
    def load_graph(self):
            options = QFileDialog.Options()
            filepath, _ = QFileDialog.getOpenFileName(self, "Load Execution Graph", "", "Execution Graph (*.veg)", options=options)
            if filepath:
                try:
                    with open(filepath) as f:
                        graph_data = json.load(f)
                       
                    self.scene.clear()
                    nodes = {}
                   
                    # Create nodes
                    for node_data in graph_data['nodes']:
                        node = ExecutionDraggableRect(
                            name=node_data['name'],
                            content=node_data['content'],
                            x=node_data['x'],
                            y=node_data['y'],
                            width=300,
                            height=200,
                            scene=self.scene,
                            is_class=node_data['is_class']
                        )
                        self.scene.addItem(node)
                        nodes[node_data['name']] = node
                    
                    # Create connections with proper colors
                    for conn_data in graph_data['connections']:
                        if conn_data['start_node'] in nodes and conn_data['end_node'] in nodes:
                            start_node = nodes[conn_data['start_node']]
                            end_node = nodes[conn_data['end_node']]
                            
                            connection = Connection(start_node.output_point, end_node.input_point, self.scene)
                            
                            # Set color based on connection type
                            if conn_data['type'] == 'return':
                                connection.setPen(QPen(QColor(255, 0, 255), 2))  # Magenta for returns
                            elif conn_data['type'] == 'conditional':
                                connection.setPen(QPen(QColor(255, 165, 0), 2))  # Orange for conditional
                            else:  # normal
                                connection.setPen(QPen(QColor(0, 255, 0), 2))    # Green for normal calls
                            
                            connection.setEndPoint(end_node.input_point)
                            self.scene.addItem(connection)

                    QMessageBox.information(self, "Success", "Execution graph loaded successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load graph: {str(e)}")
    
    def reset_view(self):
        """Reset the view to show all items."""
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.view.scale(0.9, 0.9)  # Slight zoom out to show everything with margins

    def optimize_layout(self):
        """Re-run the layout optimization."""
        optimizer = GraphLayoutOptimizer(self.scene)
        optimizer.optimize()

    def create_execution_nodes(self, code_text):
        tracked_libraries = {
            'udefs', 'usql', 'embeds', 'cmds', 'crypto', 'crypto_defs', 'ddefs',
            'deposit_monitor_thread', 'translation', 'ulang'
        }
        
        excluded_calls = {
            'int', 'str', 'len', 'print', 'list', 'dict', 'set',
            'append', 'extend', 'pop', 'remove', 'clear', 'sort',
            'items', 'keys', 'values', 'split', 'join', 'strip',
            'replace', 'format', 'startswith', 'endswith', 'find',
            'encode', 'decode', 'Embed', 'reverse', 'Decimal', 'bool', 'json',
            'lower', 'upper', 'items', 'QApplication',
            'QMainWindow', 'QTextEdit', 'QAction', 'QFileDialog', 'QMessageBox',
            'QGraphicsView', 'QGraphicsScene', 'QGraphicsRectItem',
            'QGraphicsTextItem', 'QGraphicsPathItem', 'QGraphicsEllipseItem',
            'QMenu', 'QInputDialog', 'QDialog', 'QVBoxLayout', 'QHBoxLayout',
            'QLabel', 'QSlider', 'QSpinBox', 'QPushButton', 'QGroupBox',
            'QWidget', 'QFrame', 'QMenuBar', 'QGraphicsItem', 'QGridLayout',
            'QComboBox', 'QColorDialog', 'QTabWidget', 'QLineEdit', 'QListWidget',
            'QWidget', 'QHBoxLayout', 'QIcon', 'QLabel', 'QPushButton', 'QAction',
            'QListWidget', 'QFileDialog'
        }
        
        execution_flow = self.create_execution_graph(code_text)
        nodes = {}
        x, y = 50, 50
        connection_pairs = set()
        
        # Create visitor to get call information
        visitor = FunctionCallVisitor()
        visitor.visit(ast.parse(code_text))
        
        # First pass: Create nodes
        for func_name in execution_flow.keys():
            # Skip RETURN_TO markers
            if func_name.startswith('RETURN_TO_'):
                continue
                
            # Get original name and properties for unique calls
            if func_name in visitor.unique_calls:
                original_name = visitor.unique_calls[func_name]['original_name']
                node = ExecutionDraggableRect(
                    original_name,
                    f"def {original_name}",
                    x, y, 300, 200,
                    self.scene,
                    False
                )
            else:
                node = ExecutionDraggableRect(
                    func_name,
                    f"def {func_name}",
                    x, y, 300, 200,
                    self.scene,
                    False
                )
            
            nodes[func_name] = node
            self.scene.addItem(node)
            x += 350
            if x > 1050:
                x = 50
                y += 250
        
        # Second pass: Create connections
        for source_name, targets in execution_flow.items():
            if source_name not in nodes:
                continue
                
            source_node = nodes[source_name]
            for target in targets:
                if target.startswith('RETURN_TO_'):
                    continue
                    
                if target in nodes:
                    target_node = nodes[target]
                    conn_key = (source_name, target)
                    
                    if conn_key not in connection_pairs:
                        connection_pairs.add(conn_key)
                        connection = Connection(
                            source_node.output_point,
                            target_node.input_point,
                            self.scene
                        )
                        
                        # Check if this is a conditional call
                        is_conditional = (source_name, target) in visitor.conditional_calls
                        
                        # Set connection color based on type
                        if is_conditional:
                            connection.setPen(QPen(QColor(255, 165, 0), 2))  # Orange for conditional
                        else:
                            connection.setPen(QPen(QColor(0, 255, 0), 2))  # Green for regular
                            
                        connection.setEndPoint(target_node.input_point)
                        self.scene.addItem(connection)

class BuildGraphScene(BlueprintScene):
    def __init__(self, parent_ide):
        super().__init__()
        self.parent_ide = parent_ide
        self.typing_buffer = ""
        self.typing_node = None
        self.existing_functions = set()  # Track existing function names
        self.update_existing_functions()
        
        # Initialize with default structure if no content exists
        if self.should_initialize():
            self.initialize_default_structure()

    def should_initialize(self):
        """Check if we should initialize with default structure"""
        if not self.parent_ide:
            return True
            
        # Check if we're working with a new, unedited file
        text = self.parent_ide.textEdit.toPlainText()
        return not text.strip() and not self.parent_ide.currentFile
    
    def initialize_default_structure(self):
        """Create the default if __name__ == '__main__' structure with main() function"""
        # Create main entry point node
        entry_node = BuildableNode(
            "Entry Point",
            'if __name__ == "__main__":\n    main()',
            100, 100, 400, 250, self, False, self.parent_ide
        )
        self.addItem(entry_node)
        
        # Create main function node
        main_node = BuildableNode(
            "main",
            "def main():\n    return",
            600, 100, 400, 250, self, False, self.parent_ide
        )
        self.addItem(main_node)
        
        # Create connection between nodes
        connection = Connection(entry_node.output_point, main_node.input_point, self)
        connection.setEndPoint(main_node.input_point)
        self.addItem(connection)
        
        # Update the source file
        if self.parent_ide:
            code = main_node.full_content + "\n\n" + entry_node.full_content
            self.parent_ide.textEdit.setText(code)

    def keyPressEvent(self, event):
        # Don't create new nodes if modifier keys are pressed
        if event.modifiers() & (Qt.ControlModifier | Qt.AltModifier | Qt.ShiftModifier):
            super().keyPressEvent(event)
            return

        if not self.selectedItems() or (
            len(self.selectedItems()) == 1 and 
            isinstance(self.selectedItems()[0], BuildableNode) and 
            self.selectedItems()[0].editing
        ):
            # Only create new node if there's no editing node and no modifiers
            if self.typing_node is None and not event.modifiers():
                self.typing_node = BuildableNode("New Node", "", 100, 100, 400, 250, self, False, self.parent_ide)
                self.addItem(self.typing_node)
                self.typing_node.startEditing()
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if self.typing_node and not self.typing_node.contains(self.typing_node.mapFromScene(event.scenePos())):
            self.typing_node.stopEditing()
            self.typing_node = None
        super().mousePressEvent(event)

    def update_existing_functions(self):
        """Update the set of existing function names in the scene."""
        self.existing_functions.clear()
        for item in self.items():
            if isinstance(item, BuildableNode):
                self.existing_functions.add(item.name)

    def create_function_node(self, func_name, x, y):
        """Create a new function node with a basic template."""
        template = f"def {func_name}():\n    return"
        node = BuildableNode(func_name, template, x, y, 400, 250, self, False, self.parent_ide)
        self.addItem(node)
        self.existing_functions.add(func_name)
        return node

    def check_and_create_called_functions(self, node):
        """Check for function calls in the node and create new nodes if needed."""
        content = node.text_item.toPlainText()
        print(f"Checking content for function calls: {content}")
        
        # Update existing functions list
        self.update_existing_functions()
        
        # Get all function calls
        called_functions = detect_function_calls(content)
        print(f"Detected function calls: {called_functions}")
        print(f"Existing functions: {self.existing_functions}")
        
        # Get node's position
        pos = node.pos()
        base_x = pos.x() + 450  # Place new nodes to the right
        base_y = pos.y()
        y_offset = 0
        
        # Create nodes for called functions that don't exist
        new_nodes = []
        for func_name in called_functions:
            print(f"Checking function: {func_name}")
            if func_name not in self.existing_functions and func_name != node.name:
                print(f"Creating new node for: {func_name}")
                new_node = self.create_function_node(func_name, base_x, base_y + y_offset)
                new_nodes.append(new_node)
                y_offset += 300
                
                # Create connection between nodes
                connection = Connection(node.output_point, new_node.input_point, self.scene)
                connection.setEndPoint(new_node.input_point)
                self.addItem(connection)
                print(f"Created node and connection for: {func_name}")
        
        # Always update the source file when changes occur
        if self.parent_ide:
            all_nodes = sorted(
                [item for item in self.items() if isinstance(item, BuildableNode)],
                key=lambda x: x.pos().y()
            )
            print(f"Found {len(all_nodes)} nodes to update source with")
            combined_code = [node.full_content for node in all_nodes]
            self.parent_ide.textEdit.setText("\n\n".join(combined_code))
            print("Updated source file")
            
class BuildGraphView(BlueprintView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def keyPressEvent(self, event):
        print(f"View Key press - key: {event.key()}, text: {event.text()}")
        
        # Only handle Delete key (16777223), not Backspace (16777219)
        if event.key() == 16777223:  # Delete key only
            print("Delete key detected")
            selected = self.scene().selectedItems()
            if selected:
                print(f"Found {len(selected)} selected items")
                self.deleteSelectedNodes()
                # Force scene update
                self.scene().update()
                self.viewport().update()
                event.accept()
                return
        
        # Pass all other keys to parent handler
        super().keyPressEvent(event)

    def deleteSelectedNodes(self):
        print("Attempting to delete nodes")
        to_delete = []
        
        # Collect nodes to delete
        for item in self.scene().selectedItems():
            if isinstance(item, BuildableNode) and not item.editing:
                print(f"Adding node to delete list: {item.name}")
                to_delete.append(item)
        
        if not to_delete:
            print("No nodes to delete")
            return
            
        print(f"Found {len(to_delete)} nodes to delete")
        
        # Process deletion
        for node in to_delete:
            # Remove connections
            if hasattr(node, 'input_point'):
                for conn in list(node.input_point.connections):
                    print(f"Removing input connection from {node.name}")
                    conn.cleanup()
                    self.scene().removeItem(conn)
            
            if hasattr(node, 'output_point'):
                for conn in list(node.output_point.connections):
                    print(f"Removing output connection from {node.name}")
                    conn.cleanup()
                    self.scene().removeItem(conn)
            
            # Remove from scene's item list before removal
            scene_items = self.scene().items()
            if node in scene_items:
                print(f"Node {node.name} found in scene items")
            
            # Remove the node
            self.scene().removeItem(node)
            node.setParentItem(None)  # Explicitly remove parent
            del node  # Explicitly delete the node
            
            # Verify removal
            scene_items_after = self.scene().items()
            print(f"Scene items before: {len(scene_items)}, after: {len(scene_items_after)}")

        # Update IDE content
        if isinstance(self.scene(), BuildGraphScene) and self.scene().parent_ide:
            remaining_nodes = sorted(
                [node for node in self.scene().items() if isinstance(node, BuildableNode)],
                key=lambda x: x.pos().y()
            )
            print(f"Remaining buildable nodes: {len(remaining_nodes)}")
            
            combined_code = [node.full_content for node in remaining_nodes]
            self.scene().parent_ide.textEdit.setText("\n".join(combined_code))
            print("Updated IDE content")
        
        # Force scene to update
        self.scene().update()
        self.viewport().update()

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)

class BuildGraphWindow(QMainWindow):
    def __init__(self, parent, code_text):
        super().__init__()
        # Store parent reference for IDE access
        self.parent_ide = parent
        self.setWindowTitle("Build Graph")
        # Set the window to stay on top of the IDE window
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # Check if there's existing code that would conflict
        if code_text.strip() and not self.confirm_code_replacement():
            # User cancelled - don't create window
            self.cancelled = True
            return
            
        super().__init__(parent)
        self.cancelled = False
        self.setStyleSheet("QMainWindow { background: #2c3e50; color: white; }")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create container for contents
        container = QWidget()
        containerLayout = QVBoxLayout(container)
        
        # Create menu bar
        menubar = QMenuBar()
        self.setup_menus(menubar)
        containerLayout.addWidget(menubar)
        
        # Create scene and view
        self.scene = BuildGraphScene(self.parent_ide)
        self.view = BuildGraphView(self.scene)
        containerLayout.addWidget(self.view)
        
        self.setCentralWidget(container)
        self.resize(800, 600)

    def confirm_code_replacement(self):
        """Confirm with user if they want to replace existing code"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Existing Code Detected")
        msg.setText("The code build graph builds code from scratch and cannot import existing code.")
        msg.setInformativeText("Do you want to clear the existing code and start fresh?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        return msg.exec_() == QMessageBox.Yes

    def create_initial_nodes(self, code_text):
        current_block = []
        y_offset = 50
        
        for line in code_text.splitlines():
            if line.strip():
                current_block.append(line)
            elif current_block:
                content = "\n".join(current_block)
                node = BuildableNode("Code Block", content, 100, y_offset, 400, 250, self, False, self.parent_ide)
                self.scene.addItem(node)
                y_offset += 300
                current_block = []
        
        if current_block:
            content = "\n".join(current_block)
            node = BuildableNode("Code Block", content, 100, y_offset, 400, 250, self, False, self.parent_ide)
            self.scene.addItem(node)

    def setup_menus(self, menubar):
        """Setup the window's menu bars"""
        # File menu
        fileMenu = menubar.addMenu("File")
        saveAction = QAction("Save Graph", self)
        loadAction = QAction("Load Graph", self)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(loadAction)
        
        # Edit menu
        editMenu = menubar.addMenu("Edit")
        addCommentAction = QAction("Add Comment Box", self)
        editMenu.addAction(addCommentAction)
        
        # Connect actions
        if self.parent_ide:
            saveAction.triggered.connect(lambda: self.parent_ide.saveBlueprintWorkspace(self.scene))
            loadAction.triggered.connect(lambda: self.parent_ide.loadBlueprintWorkspace(self.scene))
            addCommentAction.triggered.connect(lambda: self.parent_ide.addCommentBoxToScene(self.scene))
