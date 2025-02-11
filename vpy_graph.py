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
        # Get all connections from all points
        all_connections = []
        
        # For ExecutionDraggableRect which uses lists
        if hasattr(self, 'input_points'):
            for point in self.input_points:
                all_connections.extend(point.connections)
        if hasattr(self, 'output_points'):
            for point in self.output_points:
                all_connections.extend(point.connections)
        if hasattr(self, 'return_points'):
            for point in self.return_points:
                all_connections.extend(point.connections)
                
        # For regular DraggableRect which uses single points
        if hasattr(self, 'input_point') and self.input_point is not None:
            all_connections.extend(self.input_point.connections)
        if hasattr(self, 'output_point') and self.output_point is not None:
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
        """Handle mouse movement with safe connection updates"""
        # First do the basic movement and grid snapping
        super().mouseMoveEvent(event)
        pos = self.pos()
        new_x = round(pos.x() / self.grid_size) * self.grid_size
        new_y = round(pos.y() / self.grid_size) * self.grid_size
        self.setPos(new_x, new_y)
        
        # Safely update all connections
        all_points = []
        
        # Add input points
        if hasattr(self, 'input_points') and self.input_points:
            all_points.extend(point for point in self.input_points if point is not None)
        if hasattr(self, 'input_point') and self.input_point is not None:
            all_points.append(self.input_point)
            
        # Add output points
        if hasattr(self, 'output_points') and self.output_points:
            all_points.extend(point for point in self.output_points if point is not None)
            
        # Add return points
        if hasattr(self, 'return_points') and self.return_points:
            all_points.extend(point for point in self.return_points if point is not None)
        
        # Update all valid connections
        for point in all_points:
            if hasattr(point, 'connections'):
                for connection in point.connections:
                    if connection is not None:
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
        # Store scene reference
        self.graph_scene = scene
        
        # Initialize lists before parent constructor
        self.output_points = []
        self.input_points = []
        self.return_points = []
        
        # Call parent constructor but skip its connection point creation
        super().__init__(name, content, x, y, width, height, scene, is_class)
        
        # Remove parent's connection points if they exist
        if hasattr(self, 'input_point') and self.input_point is not None:
            self.graph_scene.removeItem(self.input_point)
            self.input_point = None
        if hasattr(self, 'output_point') and self.output_point is not None:
            self.graph_scene.removeItem(self.output_point)
            self.output_point = None
        
        # Set flags
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.ItemSendsScenePositionChanges)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        
        # Create initial central input point
        self.input_point = self.add_input_point()
        
        # Set appearance
        self.setBrush(QColor(44, 62, 80))  # Darker blue for execution nodes
        self.setPen(QPen(QColor(52, 152, 219), 2))  # Bright blue border

    def add_output_point(self):
        """Add a new output connection point"""
        point = ConnectionPoint(self.graph_scene, self, True)
        self.output_points.append(point)
        self.updateConnectionPoints()
        return point

    def add_input_point(self):
        """Add a new input connection point"""
        point = ConnectionPoint(self.graph_scene, self, False)
        self.input_points.append(point)
        self.updateConnectionPoints()
        return point

    def add_return_point(self):
        """Add a new return connection point"""
        point = ConnectionPoint(self.graph_scene, self, True)
        self.return_points.append(point)
        self.updateConnectionPoints()
        return point

    def updateConnectionPoints(self):
        """Update positions of all connection points"""
        rect = self.boundingRect()
        
        # Position single input point in center-left
        for point in self.input_points:
            point.setPos(0, rect.height() / 2)
        
        # Position output points evenly along right side
        if self.output_points:
            spacing = rect.height() / (len(self.output_points) + 1)
            for i, point in enumerate(self.output_points):
                point.setPos(rect.width(), spacing * (i + 1))
        
        # Position return points evenly along bottom
        if self.return_points:
            spacing = rect.width() / (len(self.return_points) + 1)
            for i, point in enumerate(self.return_points):
                point.setPos(spacing * (i + 1), rect.height())

    def add_conditional_output(self):
        """Add a new conditional output point"""
        point = ConnectionPoint(self.graph_scene, self, True)
        point.is_conditional = True
        self.output_points.append(point)
        self.updateConnectionPoints()
        return point

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos = self.pos()
        new_x = self.snapToGrid(pos.x())
        new_y = self.snapToGrid(pos.y())
        self.setPos(new_x, new_y)
        
        # Update all connections for all points
        self.updateAllConnections()

    def updateAllConnections(self):
        """Update all connected paths"""
        for points in [self.input_points, self.output_points, self.return_points]:
            for point in points:
                for connection in point.connections:
                    connection.updatePath()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.updateAllConnections()
        elif change == QGraphicsItem.ItemSelectedChange:
            self.updateConnectionHighlighting(value)
        return super().itemChange(change, value)

    def updateConnectionHighlighting(self, selected):
        """Update the appearance of all connected paths"""
        all_points = self.input_points + self.output_points + self.return_points
        for point in all_points:
            for connection in point.connections:
                pen = connection.pen()
                color = pen.color()
                if selected:
                    if connection.start_point in all_points or connection.end_point in all_points:
                        pen.setWidth(2)
                        pen.setColor(color)
                    else:
                        dimmed_color = QColor(color.red(), color.green(), color.blue(), 50)
                        pen.setWidth(1)
                        pen.setColor(dimmed_color)
                else:
                    pen.setWidth(2)
                    pen.setColor(color)
                connection.setPen(pen)

class EditableTextItem(QGraphicsTextItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_node = parent

    def mouseDoubleClickEvent(self, event):
        """Handle double click by starting edit mode"""
        if self.parent_node and hasattr(self.parent_node, 'startEditing'):
            self.parent_node.startEditing()
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        """Handle key events"""
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            print("EditableTextItem: Ctrl+Enter detected")
            if self.parent_node and hasattr(self.parent_node, 'stopEditing'):
                self.parent_node.stopEditing()
            event.accept()
            return
        super().keyPressEvent(event)

class BuildableNode(QGraphicsRectItem):
    def __init__(self, name, content, x, y, width, height, scene, is_class: bool, parent_ide):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        
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
        
        # Create editable text item using our custom class
        self.text_item = EditableTextItem(self)
        self.text_item.setDefaultTextColor(Qt.white)
        self.text_item.setFont(QFont("Courier", 10))
        self.text_item.setPos(5, 25)
        self.text_item.setTextWidth(self.fixed_width - 10)
        self.text_item.setPlainText(content)
        self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        
        # Add connection points
        self.input_point = ConnectionPoint(scene, self, False)
        self.output_point = ConnectionPoint(scene, self, True)
        self.updateConnectionPoints()
        
        self.setAcceptHoverEvents(True)

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
        """Begin editing mode"""
        print(f"Starting edit mode for node: {self.name}")
        self.editing = True
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setFocus()
        self.setSelected(True)
        if self.scene:
            self.scene.setFocusItem(self.text_item)
            print("Set focus to text item")

    def stopEditing(self):
        """End editing mode and process changes"""
        print(f"Stopping edit mode for node: {self.name}")
        if not self.editing:
            return

        self.editing = False
        self.text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        old_content = self.full_content
        self.detectNodeType()
        self.detectScope()
        self.updateTitle()
        new_content = self.text_item.toPlainText()
        self.updateContent(new_content)
        self.setSelected(False)
        
        # Only process if content actually changed
        if old_content != new_content:
            if self.scene and self.scene.__class__.__name__ == 'BuildGraphScene':
                self.scene.check_and_create_called_functions(self)
                
        if self.scene:
            self.scene.setFocusItem(None)
            if hasattr(self.scene, 'update_existing_functions'):
                self.scene.update_existing_functions()
        print("Edit mode stopped")

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        print(f"Node key press - key: {event.key()}, modifiers: {event.modifiers()}, editing: {self.editing}")
        
        if self.editing:
            if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
                print("Node: Received Ctrl+Enter while editing")
                self.stopEditing()
                event.accept()
                return
            elif event.key() == Qt.Key_Escape:
                print("Node: Received Escape")
                self.stopEditing()
                event.accept()
                return
            else:
                # Forward other keys to text_item when editing
                self.text_item.keyPressEvent(event)
                self.adjustHeight()
                event.accept()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        """Handle focus loss"""
        super().focusOutEvent(event)
        if self.editing:
            # Don't stop editing if we're just losing focus temporarily
            if not self.text_item.hasFocus():
                self.stopEditing()

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

    def mousePressEvent(self, event):
        """Handle mouse press"""
        super().mousePressEvent(event)
        if not self.editing:
            self.setFocus()  # Ensure we can receive key events

    def mouseDoubleClickEvent(self, event):
        """Handle double click to start editing"""
        if not self.editing:
            # Check if we clicked the text area
            text_pos = self.text_item.mapFromScene(event.scenePos())
            if self.text_item.contains(text_pos):
                self.startEditing()
        super().mouseDoubleClickEvent(event)
