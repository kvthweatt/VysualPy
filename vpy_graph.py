import re

from PyQt5.QtWidgets import (
    QGraphicsRectItem, QGraphicsTextItem, QInputDialog, QGraphicsItem
    )

from PyQt5.QtCore import (
    QRectF, Qt
    )

from PyQt5.QtGui import (
    QColor, QBrush, QPen, QFont
    )

from vpy_connection import Connection, ConnectionPoint

class CommentBox(QGraphicsRectItem):
    def __init__(self, name, x, y, width=300, height=200):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable)
        
        # Set resize handles
        self.setAcceptHoverEvents(True)
        self.resizing = False
        self.resizeHandle = QRectF(width - 10, height - 10, 10, 10)
        
        # Set appearance
        color = QColor(0, 0, 0)
        color.setAlphaF(0.1)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.magenta, 1))
        
        # Create title
        self.name = name
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setPlainText(name)
        self.title_item.setDefaultTextColor(Qt.white)
        self.title_item.setPos(10, 5)
        
        # Set font
        font = QFont("Arial", 14, QFont.Bold)
        self.title_item.setFont(font)
        
        self.setPos(x, y)
        self.setZValue(-1)

    def mousePressEvent(self, event):
        if self.resizeHandle.contains(event.pos()):
            self.resizing = True
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            new_width = max(100, event.pos().x())
            new_height = max(100, event.pos().y())
            self.setRect(0, 0, new_width, new_height)
            self.resizeHandle = QRectF(new_width - 10, new_height - 10, 10, 10)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        
        if self.scene and self.scene.views():
            view = self.scene.views()[0]
            scale = view.transform().m11()
            
            # Scale font
            font = self.title_item.font()
            font.setPointSizeF(14 / scale)
            self.title_item.setFont(font)
            
            # Scale resize handle
            handle_size = 10 / scale
            rect = self.rect()
            self.resizeHandle = QRectF(
                rect.width() - handle_size,
                rect.height() - handle_size,
                handle_size,
                handle_size
            )
            
        painter.fillRect(self.resizeHandle, Qt.green)

    def mouseDoubleClickEvent(self, event):
        current_name = self.name
        new_name, ok = QInputDialog.getText(None, "Rename Comment Box", 
                                          "Enter new name:", text=current_name)
        if ok and new_name:
            self.name = new_name
            self.title_item.setPlainText(new_name)

class DraggableRect(QGraphicsRectItem):
    def __init__(self, name, content, x, y, width, height, scene, is_class: bool):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        self.is_class = is_class  # Store whether this is a class or function
        self.full_content = content
        self.name = name
        self.setPos(x, y)

        self.grid_size = 50

        # Set slate gray background with thin gray border
        self.setBrush(QColor(47, 79, 79))  # Slate gray
        self.setPen(QPen(Qt.gray, 1))  # Thin gray border

        # Title of the box with white text
        self.title_item = QGraphicsTextItem(name, self)
        self.title_item.setFont(QFont("Arial", 10, QFont.Bold))
        self.title_item.setDefaultTextColor(Qt.white)
        self.title_item.setPos(5, 5)

        # Content of the box with white text
        self.content_item = QGraphicsTextItem(self)
        self.content_item.setFont(QFont("Courier", 9))
        self.content_item.setDefaultTextColor(Qt.white)
        self.content_item.setPos(5, 25)

        # Add connection points
        self.input_point = ConnectionPoint(scene, self, False)
        self.output_point = ConnectionPoint(scene, self, True)
        self.updateConnectionPoints()

        self.setContent(content)
        self.setAcceptHoverEvents(True)

    def snapToGrid(self, value):
        return round(value / self.grid_size) * self.grid_size

    def updateConnectionPoints(self):
        self.input_point.setPos(0, self.boundingRect().height() / 2)
        self.output_point.setPos(self.boundingRect().width(), self.boundingRect().height() / 2)

    def updateConnectedLines(self, selected):
        # Get all connections from input and output points
        all_connections = []
        if hasattr(self, 'input_point'):
            all_connections.extend(self.input_point.connections)
        if hasattr(self, 'output_point'):
            all_connections.extend(self.output_point.connections)

        for connection in all_connections:
            start_rect = connection.start_point.parentItem()
            end_rect = connection.end_point.parentItem()
            
            # Get original color
            color = connection.pen().color()
            pen = connection.pen()
            
            if selected:
                # If this node is selected, highlight its direct connections
                if start_rect == self or end_rect == self:
                    pen.setWidth(2)
                    pen.setColor(color)
                else:
                    # Dim other connections
                    dimmed_color = QColor(color.red(), color.green(), color.blue(), 50)
                    pen.setWidth(1)
                    pen.setColor(dimmed_color)
            else:
                # Restore original appearance
                pen.setWidth(2)
                pen.setColor(color)
                
            connection.setPen(pen)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            # Update all nodes in scene
            for item in self.scene().items():
                if isinstance(item, DraggableRect):
                    item.updateConnectedLines(item == self)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # Get current position
        pos = self.pos()
        # Snap to grid
        new_x = self.snapToGrid(pos.x())
        new_y = self.snapToGrid(pos.y())
        # Set new position
        self.setPos(new_x, new_y)
        # Update all connected paths for both input and output points
        for point in [self.input_point, self.output_point]:
            for connection in point.connections:
                connection.updatePath()

    def mouseDoubleClickEvent(self, event):
        self.viewer = CodeViewerWindow(self.name, self.full_content)
        self.viewer.show()
        super().mouseDoubleClickEvent(event)

    def setContent(self, content):
        max_lines = 10
        max_width = 40

        lines = content.splitlines()
        truncated_lines = []

        for i, line in enumerate(lines):
            if i >= max_lines:
                truncated_lines.append("...")
                break
            
            if len(line) > max_width:
                truncated_lines.append(line[:max_width] + "...")
            else:
                truncated_lines.append(line)

        display_content = "\n".join(truncated_lines)
        self.content_item.setPlainText(display_content)

class ExecutionDraggableRect(DraggableRect):
    def __init__(self, name, content, x, y, width, height, scene, is_class: bool):
        super().__init__(name, content, x, y, width, height, scene, is_class)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # Add item change notification
        self.setFlag(QGraphicsRectItem.ItemSendsScenePositionChanges)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        
        # Set connection points for return and data input
        self.input_point = ConnectionPoint(scene, self, False)  # Data reception connection point on left  # Data reception connection point on left
        self.return_point = ConnectionPoint(scene, self, True)  # Return connection point on right
        
        # Set appearance
        self.setBrush(QColor(44, 62, 80))  # Darker blue for execution nodes
        self.setPen(QPen(QColor(52, 152, 219), 2))  # Bright blue border

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            # When selection state changes
            if value:  # Item is being selected
                for item in self.scene().items():
                    if isinstance(item, Connection):
                        start_rect = item.start_point.parentItem()
                        end_rect = item.end_point.parentItem()
                        pen = item.pen()
                        color = pen.color()
                        
                        if start_rect == self or end_rect == self:
                            # Keep original color and width for connected lines
                            pen.setWidth(2)
                            pen.setColor(QColor(color.red(), color.green(), color.blue(), 255))
                        else:
                            # Dim unconnected lines
                            pen.setColor(QColor(color.red(), color.green(), color.blue(), 40))
                            pen.setWidth(1)
                        item.setPen(pen)
            else:  # Item is being deselected
                # Restore all connections to original appearance
                for item in self.scene().items():
                    if isinstance(item, Connection):
                        pen = item.pen()
                        color = pen.color()
                        pen.setColor(QColor(color.red(), color.green(), color.blue(), 255))
                        pen.setWidth(2)
                        item.setPen(pen)
                        
        return super().itemChange(change, value)

    def updateConnectedLines(self, selected):
        # Get all connections from input and output points
        all_connections = []
        if hasattr(self, 'input_point'):
            all_connections.extend(self.input_point.connections)
        if hasattr(self, 'output_point'):
            all_connections.extend(self.output_point.connections)

        for connection in all_connections:
            start_rect = connection.start_point.parentItem()
            end_rect = connection.end_point.parentItem()
            
            # Get original color
            color = connection.pen().color()
            pen = connection.pen()
            
            if selected:
                # If this node is selected, highlight its direct connections
                if start_rect == self or end_rect == self:
                    pen.setWidth(2)
                    pen.setColor(color)
                else:
                    # Dim other connections
                    dimmed_color = QColor(color.red(), color.green(), color.blue(), 50)
                    pen.setWidth(1)
                    pen.setColor(dimmed_color)
            else:
                # Restore original appearance
                pen.setWidth(2)
                pen.setColor(color)
                
            connection.setPen(pen)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            # Update all nodes in scene
            for item in self.scene().items():
                if isinstance(item, DraggableRect):
                    item.updateConnectedLines(item == self)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos = self.pos()
        new_x = self.snapToGrid(pos.x())
        new_y = self.snapToGrid(pos.y())
        self.setPos(new_x, new_y)
        # Update all connections
        for point in [self.input_point, self.output_point, self.return_point]:
            if hasattr(point, 'connections'):
                for connection in point.connections:
                    connection.updatePath()

class BuildableNode(QGraphicsRectItem):
    def __init__(self, name, content, x, y, width, height, scene, is_class: bool, parent_ide):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
        self.name = name
        self.full_content = content
        self.is_class = is_class
        self.parent_ide = parent_ide
        self.editing = False
        self.grid_size = 50
        self.fixed_width = width

        self.scene = scene
        
        # Set position
        self.setPos(x, y)
        
        # Set appearance
        self.setBrush(QColor(47, 79, 79))
        self.setPen(QPen(Qt.gray, 1))
        
        # Create title
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setFont(QFont("Arial", 10, QFont.Bold))
        self.title_item.setDefaultTextColor(Qt.white)
        self.title_item.setPos(5, 5)
        self.updateTitle()
        
        # Create editable text item
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setDefaultTextColor(Qt.white)
        self.text_item.setFont(QFont("Courier", 10))
        self.text_item.setPos(5, 25)
        self.text_item.setTextWidth(self.fixed_width - 10)
        self.text_item.setPlainText(content)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        
        # Add connection points
        self.input_point = ConnectionPoint(scene, self, False)
        self.output_point = ConnectionPoint(scene, self, True)
        self.updateConnectionPoints()
        
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable)

    def updateConnectionPoints(self):
        rect = self.rect()
        # Input point on the left side
        self.input_point.setPos(0, rect.height() / 2)
        # Output point on the right side
        self.output_point.setPos(self.fixed_width, rect.height() / 2)

    def updateTitle(self):
        title_text = f"{self.name}"
        if hasattr(self, 'scope') and self.scope != "Global":
            title_text += f" [{self.scope}]"
        self.title_item.setPlainText(title_text)

    def startEditing(self):
        self.editing = True
        self.text_item.setFocus()
        self.setSelected(True)

    def stopEditing(self):
        if not self.editing:
            return

        self.editing = False
        old_content = self.full_content
        self.detectNodeType()
        self.detectScope()
        self.updateTitle()
        new_content = self.text_item.toPlainText()
        self.updateContent(new_content)
        self.setSelected(False)
        
        # Only process if content actually changed
        if old_content != new_content:
            # Check for function calls and create new nodes
            # Note: We check the class name as a string to avoid circular imports
            if self.scene.__class__.__name__ == 'BuildGraphScene':
                self.scene.check_and_create_called_functions(self)
                
                # Update the source file with all node contents
                if self.scene.parent_ide:
                    all_nodes = sorted(
                        [item for item in self.scene.items() if isinstance(item, BuildableNode)],
                        key=lambda x: x.pos().y()
                    )
                    combined_code = [node.full_content for node in all_nodes]
                    self.scene.parent_ide.textEdit.setText("\n\n".join(combined_code))
        
        if self.scene:
            self.scene.setFocusItem(None)
            self.scene.update_existing_functions()  # Update tracked functions
            
    def keyPressEvent(self, event):
        if self.editing:
            # Always forward key events to text_item when editing
            if event.key() == Qt.Key_Escape:
                self.stopEditing()
            elif event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
                self.stopEditing()
            else:
                # Forward all other keys to text_item
                cursor = self.text_item.textCursor()
                self.text_item.keyPressEvent(event)
                # Only adjust height if content actually changed
                if cursor.position() != self.text_item.textCursor().position():
                    QTimer.singleShot(0, self.adjustHeight)
            event.accept()
        else:
            super().keyPressEvent(event)

    def adjustHeight(self):
        """Adjust only the height of the node based on content"""
        doc = self.text_item.document()
        doc.setTextWidth(self.fixed_width - 10)
        new_height = max(200, doc.size().height() + 40)
        
        if abs(self.rect().height() - new_height) > 1:
            self.setRect(0, 0, self.fixed_width, new_height)
            self.text_item.setTextWidth(self.fixed_width - 10)
            self.updateConnectionPoints()
            
            # Update any connected paths
            for point in [self.input_point, self.output_point]:
                for connection in point.connections:
                    connection.updatePath()

    def detectNodeType(self):
        """Detect if the node contains a function or class definition and extract its name."""
        content = self.text_item.toPlainText().strip()
        
        # Check for class definition
        class_match = re.match(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', content)
        if class_match:
            self.is_class = True
            self.name = class_match.group(1)
            return
            
        # Check for function definition (including async)
        func_match = re.match(r'(async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)', content)
        if func_match:
            self.is_class = False
            self.name = func_match.group(2)
            if func_match.group(1):  # async was found
                self.name = f"async {self.name}"
            return
            
        # If no function or class found, check for assignment
        if '=' in content:
            assign_match = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*=', content)
            if assign_match:
                self.name = assign_match.group(1)
                return
                
        # If no patterns match, use a generic name
        first_line = content.split('\n')[0].strip()
        if first_line:
            self.name = first_line[:20] + ('...' if len(first_line) > 20 else '')
        else:
            self.name = "Code Block"

    def detectScope(self):
        """Detect the scope of the node based on indentation."""
        content = self.text_item.toPlainText()
        first_line = content.split('\n')[0]
        indent_level = len(first_line) - len(first_line.lstrip())
        
        if indent_level == 0:
            self.scope = "Global"
        else:
            spaces_per_indent = 4  # Standard Python indentation
            level = indent_level // spaces_per_indent
            self.scope = f"Nested (Level {level})"

    def updateContent(self, new_content):
        self.full_content = new_content
        if self.parent_ide:
            nodes = []
            for item in self.scene.items():
                if isinstance(item, BuildableNode):
                    nodes.append(item)
            nodes.sort(key=lambda x: x.pos().y())
            combined_code = [node.full_content for node in nodes]
            self.parent_ide.textEdit.setText("\n".join(combined_code))

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos = self.pos()
        new_x = round(pos.x() / self.grid_size) * self.grid_size
        new_y = round(pos.y() / self.grid_size) * self.grid_size
        self.setPos(new_x, new_y)
        
        for point in [self.input_point, self.output_point]:
            for connection in point.connections:
                connection.updatePath()
