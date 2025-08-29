#!/usr/bin/env python3
"""
Comprehensive debug application for VysualPy node system.

Features:
- Right-click context menus for creating nodes
- Full support for Blueprint, Execution, and Buildable nodes
- Multi-selection and group operations
- Node editing and property management
- Visual feedback and state management
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QMenu, QAction, QInputDialog, QMessageBox, QTextEdit, 
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QColor, QFont

# Import the new node classes and blueprint system
from vpy_node_types import BlueprintNode, ExecutionNode, BuildableNode
from vpy_blueprints import BlueprintScene, BlueprintView
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsPathItem
from PyQt5.QtGui import QPen, QPainterPath

class NodeCreationDialog(QDialog):
    """Dialog for creating new nodes with custom properties."""
    
    def __init__(self, node_type, parent=None):
        super().__init__(parent)
        self.node_type = node_type
        self.setWindowTitle(f"Create {node_type} Node")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Form layout for node properties
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setText(f"New {node_type}")
        form_layout.addRow("Name:", self.name_edit)
        
        # Content field (for blueprint and buildable nodes)
        if node_type in ["Blueprint", "Buildable"]:
            self.content_edit = QTextEdit()
            self.content_edit.setPlainText(self.get_default_content(node_type))
            self.content_edit.setFont(QFont("Courier New", 10))
            form_layout.addRow("Content:", self.content_edit)
        else:
            self.content_edit = None
            
        # Original name field (for execution nodes)
        if node_type == "Execution":
            self.original_name_edit = QLineEdit()
            self.original_name_edit.setText(f"Original {node_type}")
            form_layout.addRow("Original Name:", self.original_name_edit)
        else:
            self.original_name_edit = None
            
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_button = QPushButton("Create")
        create_button.clicked.connect(self.accept)
        create_button.setDefault(True)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def get_default_content(self, node_type):
        """Get default content for different node types."""
        if node_type == "Blueprint":
            return "def new_function():\n    \"\"\"A new function.\"\"\"\n    pass"
        elif node_type == "Buildable":
            return "# Buildable code block\nprint('Hello from buildable node')"
        return ""
        
    def get_node_data(self):
        """Get the data needed to create the node."""
        data = {
            'name': self.name_edit.text().strip() or f"New {self.node_type}"
        }
        
        if self.content_edit:
            data['content'] = self.content_edit.toPlainText()
            
        if self.original_name_edit:
            data['original_name'] = self.original_name_edit.text().strip()
            
        return data

class SimpleConnection(QGraphicsPathItem):
    """Curved connection line for blueprint nodes (like Unreal Engine)."""
    
    def __init__(self, start_port, start_pos, scene):
        super().__init__()
        self.start_port = start_port
        self.end_port = None  # Will be set when connection is completed
        self.end_pos = start_pos
        self.scene = scene
        
        # Animation and hover state
        self.is_hovered = False
        self.is_completed = False
        self.current_width = 1.0  # Start thin
        self.target_width = 1.0
        self.animation_speed = 0.2  # Animation interpolation factor
        
        # Set initial visual style - thin line
        self.normal_pen = QPen(QColor(255, 255, 255, 150), 1)  # Thin, semi-transparent white
        self.normal_pen.setCapStyle(Qt.RoundCap)
        self.normal_pen.setJoinStyle(Qt.RoundJoin)
        
        self.hover_pen = QPen(QColor(255, 255, 255, 220), 4)  # Thicker on hover
        self.hover_pen.setCapStyle(Qt.RoundCap)
        self.hover_pen.setJoinStyle(Qt.RoundJoin)
        
        # Completed connection style (green)
        self.completed_pen = QPen(QColor(0, 255, 100, 180), 1)  # Thin green
        self.completed_pen.setCapStyle(Qt.RoundCap)
        self.completed_pen.setJoinStyle(Qt.RoundJoin)
        
        self.completed_hover_pen = QPen(QColor(0, 255, 100, 220), 4)  # Thick green on hover
        self.completed_hover_pen.setCapStyle(Qt.RoundCap)
        self.completed_hover_pen.setJoinStyle(Qt.RoundJoin)
        
        # Set initial pen
        self.setPen(self.normal_pen)
        
        # Enable hover events
        self.setAcceptHoverEvents(True)
        
        # Enable drag functionality for connection lines - IMPORTANT: Make sure we can receive events
        self.setFlag(QGraphicsPathItem.ItemIsMovable, False)  # We'll handle movement manually
        self.setFlag(QGraphicsPathItem.ItemIsSelectable, True)  # Need to be selectable to receive events
        self.setFlag(QGraphicsPathItem.ItemIsFocusable, False)  # Don't take focus
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)  # Only handle left and right clicks
        
        # Set a higher z-value to ensure connection lines are on top of nodes for event handling
        self.setZValue(100)  # Higher than nodes so we get mouse events
        
        # Dragging state for connection lines
        self.is_dragging_connection = False
        self.drag_start_scene_pos = QPointF()
        self.drag_threshold = 5.0  # Minimum pixels to move before starting drag
        
        # Store initial positions for consistent dragging
        self.initial_start_node_pos = QPointF()
        self.initial_end_node_pos = QPointF()
        self.initial_drag_pos = QPointF()
        
        # Tooltip (empty for now as requested)
        self.setToolTip("")
        
        # Add to scene
        scene.addItem(self)
        self.updatePath()
        
        # Track this connection in the scene for updates when nodes move
        if hasattr(scene, 'connections'):
            scene.connections.append(self)
        
    def updatePath(self):
        """Update the curved path like Unreal Engine blueprints."""
        # Get start position in scene coordinates
        start_pos = self.start_port.node.mapToScene(self.start_port.position)
        
        # Convert to local coordinates
        local_start = self.mapFromScene(start_pos)
        local_end = self.mapFromScene(self.end_pos)
        
        # Create bezier curve path
        path = QPainterPath()
        path.moveTo(local_start)
        
        # Calculate direction and distance
        dx = local_end.x() - local_start.x()
        dy = local_end.y() - local_start.y()
        
        # Dynamic control point calculation based on direction
        # Base offset that scales with distance
        base_offset = max(abs(dx) * 0.4, 60)
        
        # Adjust curve based on the relative positions
        if dx >= 0:
            # Normal left-to-right connection
            control_offset_x = base_offset
        else:
            # Backwards connection - make tighter curves
            control_offset_x = min(base_offset, abs(dx) * 0.8)
        
        # Add vertical adjustment for better curves when going up/down
        vertical_influence = min(abs(dy) * 0.2, 50)
        
        # Determine port orientation (output goes right, input comes from left)
        if hasattr(self.start_port, 'type') and self.start_port.type.value == 'output':
            # Output port - curve extends to the right
            control1 = QPointF(local_start.x() + control_offset_x, local_start.y())
        else:
            # Input port - curve extends to the left
            control1 = QPointF(local_start.x() - control_offset_x, local_start.y())
        
        # End control point - always opposite direction from the start
        if dx >= 0:
            # Normal flow - end control point extends left from end
            control2 = QPointF(local_end.x() - control_offset_x, local_end.y())
        else:
            # Backwards flow - create an S-curve that looks natural
            control2 = QPointF(local_end.x() + control_offset_x * 0.5, local_end.y())
        
        # Add some vertical curve influence for smoother transitions
        if abs(dy) > 20:  # Only add vertical influence for significant height differences
            if dy > 0:  # Going down
                control1 = QPointF(control1.x(), control1.y() + vertical_influence)
                control2 = QPointF(control2.x(), control2.y() - vertical_influence)
            else:  # Going up
                control1 = QPointF(control1.x(), control1.y() - vertical_influence)
                control2 = QPointF(control2.x(), control2.y() + vertical_influence)
        
        # Create smooth cubic bezier curve
        path.cubicTo(control1, control2, local_end)
        
        self.setPath(path)
        
    def paint(self, painter, option, widget):
        """Custom paint with smooth width animation."""
        # Update animation if needed
        if abs(self.current_width - self.target_width) > 0.1:
            self.current_width += (self.target_width - self.current_width) * self.animation_speed
            self.update()  # Trigger repaint for smooth animation
        else:
            self.current_width = self.target_width
        
        # Create animated pen based on current state
        if self.is_completed:
            if self.is_hovered:
                color = QColor(0, 255, 100, 220)
            else:
                color = QColor(0, 255, 100, 180)
        else:
            if self.is_hovered:
                color = QColor(255, 255, 255, 220)
            else:
                color = QColor(255, 255, 255, 150)
        
        # Create pen with current animated width
        animated_pen = QPen(color, max(1, self.current_width))
        animated_pen.setCapStyle(Qt.RoundCap)
        animated_pen.setJoinStyle(Qt.RoundJoin)
        
        # Draw the connection line
        painter.setPen(animated_pen)
        painter.drawPath(self.path())
        
    def setEndPoint(self, end_port):
        """Complete the connection to an end port."""
        # Store the end port for dynamic updates
        self.end_port = end_port
        
        # Update the end position to the target port
        end_pos = end_port.node.mapToScene(end_port.position)
        self.end_pos = end_pos
        
        # Update the curve
        self.updatePath()
        
        # Mark as completed for styling
        self.is_completed = True
        
        # Update pen based on current hover state
        self.update_pen_style()
        
        print(f"Connection completed from {self.start_port.node.name}:{self.start_port.id} to {end_port.node.name}:{end_port.id}")
        
    def updateForNodeMovement(self):
        """Update connection when connected nodes have moved."""
        if self.end_port:
            # Both ends are connected to ports - update both positions
            start_pos = self.start_port.node.mapToScene(self.start_port.position)
            end_pos = self.end_port.node.mapToScene(self.end_port.position)
            self.end_pos = end_pos
            self.updatePath()
        else:
            # Only start is connected, end is free-floating
            self.updatePath()
            
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter - start thickening animation."""
        self.is_hovered = True
        self.target_width = 4.0  # Target thickness on hover
        self.update_pen_style()
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave - start thinning animation."""
        self.is_hovered = False
        self.target_width = 1.0  # Target thickness when not hovered
        self.update_pen_style()
        super().hoverLeaveEvent(event)
        
    def update_pen_style(self):
        """Update pen style based on current state."""
        if self.is_completed:
            if self.is_hovered:
                self.setPen(self.completed_hover_pen)
            else:
                self.setPen(self.completed_pen)
        else:
            if self.is_hovered:
                self.setPen(self.hover_pen)
            else:
                self.setPen(self.normal_pen)
        
        # Trigger repaint to show changes
        self.update()
        
    def mousePressEvent(self, event):
        """Handle mouse press on connection line for dragging."""
        if event.button() == Qt.LeftButton and self.is_completed and self.end_port:
            # Only allow dragging of completed connections with both ports
            self.drag_start_scene_pos = event.scenePos()
            
            # Store initial positions of both nodes to maintain relative distances
            self.initial_start_node_pos = self.start_port.node.pos()
            self.initial_end_node_pos = self.end_port.node.pos()
            self.initial_drag_pos = event.scenePos()
            
            # Don't set dragging flag yet - wait for mouse move to exceed threshold
            event.accept()
            return
        elif event.button() == Qt.RightButton:
            # Handle right-click for context menu
            event.accept()
            return
        
        # For other cases, don't handle the event
        event.ignore()
    
    def mouseMoveEvent(self, event):
        """Handle dragging the connection line to move both nodes."""
        if self.is_completed and self.end_port and self.drag_start_scene_pos is not None:
            current_scene_pos = event.scenePos()
            
            # Check if we should start dragging (threshold exceeded)
            if not self.is_dragging_connection:
                dx = current_scene_pos.x() - self.initial_drag_pos.x()
                dy = current_scene_pos.y() - self.initial_drag_pos.y()
                distance = (dx * dx + dy * dy) ** 0.5
                
                if distance > self.drag_threshold:
                    self.is_dragging_connection = True
                    # Change cursor to indicate dragging
                    from PyQt5.QtCore import Qt
                    from PyQt5.QtWidgets import QApplication
                    QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                else:
                    return  # Don't start dragging yet
            
            if self.is_dragging_connection:
                # Calculate movement delta from initial drag position (maintains relative distances)
                delta = current_scene_pos - self.initial_drag_pos
                
                # Get both connected nodes
                start_node = self.start_port.node
                end_node = self.end_port.node
                
                # Calculate new positions based on initial positions + delta
                start_new_pos = self.initial_start_node_pos + delta
                end_new_pos = self.initial_end_node_pos + delta
                
                # Apply new positions
                start_node.setPos(start_new_pos)
                end_node.setPos(end_new_pos)
                
                # Update connections (but avoid recursion by checking if we're already updating)
                if hasattr(self.scene, '_updating_connections') and not self.scene._updating_connections:
                    self.scene._updating_connections = True
                    self.scene.update_all_connections()
                    self.scene._updating_connections = False
                
                event.accept()
                return
        
        # Don't handle other move events
        event.ignore()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging."""
        if event.button() == Qt.LeftButton:
            if self.is_dragging_connection:
                # Stop dragging and restore cursor
                self.is_dragging_connection = False
                from PyQt5.QtWidgets import QApplication
                QApplication.restoreOverrideCursor()
            
            # Reset drag positions
            self.drag_start_scene_pos = QPointF()
            self.initial_start_node_pos = QPointF()
            self.initial_end_node_pos = QPointF()
            self.initial_drag_pos = QPointF()
            event.accept()
            return
        
        # Don't handle other release events
        event.ignore()
        
    def contextMenuEvent(self, event):
        """Handle right-click context menu on connection."""
        menu = QMenu()
        
        # Only show break option if this is a completed connection
        if self.is_completed and self.end_port:
            break_action = menu.addAction("🔗 Break Connection")
            break_action.triggered.connect(self.break_connection)
            
            # Show connection info as disabled action (for context)
            info_text = f"Connection: {self.start_port.node.name}:{self.start_port.id} → {self.end_port.node.name}:{self.end_port.id}"
            info_action = menu.addAction(info_text)
            info_action.setEnabled(False)  # Make it non-clickable, just informational
            
        else:
            # For incomplete connections, offer cancel option
            cancel_action = menu.addAction("❌ Cancel Connection")
            cancel_action.triggered.connect(self.cancel_connection)
            
        # Convert event position to global coordinates
        if hasattr(event, 'screenPos'):
            global_pos = event.screenPos()
        else:
            # Fallback: use current mouse position
            from PyQt5.QtGui import QCursor
            global_pos = QCursor.pos()
            
        # Show the menu
        menu.exec_(global_pos)
        
    def break_connection(self):
        """Break this connection and remove it from the scene."""
        if self.scene and hasattr(self.scene, 'connections'):
            # Remove from scene's connection tracking
            if self in self.scene.connections:
                self.scene.connections.remove(self)
        
        # Remove from scene graphics
        if self.scene:
            self.scene.removeItem(self)
            
        # Clean up port connections if they have connection tracking
        if hasattr(self.start_port, 'remove_connection'):
            self.start_port.remove_connection(self)
        if self.end_port and hasattr(self.end_port, 'remove_connection'):
            self.end_port.remove_connection(self)
            
        print(f"Broke connection: {self.start_port.node.name}:{self.start_port.id} → {self.end_port.node.name if self.end_port else 'None'}:{self.end_port.id if self.end_port else 'None'}")
        
    def cancel_connection(self):
        """Cancel an in-progress connection."""
        if self.scene and hasattr(self.scene, 'connections'):
            # Remove from scene's connection tracking
            if self in self.scene.connections:
                self.scene.connections.remove(self)
        
        # Remove from scene graphics
        if self.scene:
            self.scene.removeItem(self)
            
        # Clean up any connection state in the scene
        if hasattr(self.scene, 'connection_in_progress') and self.scene.connection_in_progress == self:
            self.scene.connection_in_progress = None
        if hasattr(self.scene, 'active_connection_point'):
            self.scene.active_connection_point = None
            
        print("Cancelled connection creation")

class EnhancedBlueprintScene(BlueprintScene):
    """Enhanced scene with comprehensive node creation capabilities."""
    
    def __init__(self):
        super().__init__()
        self.node_counter = {'Blueprint': 0, 'Execution': 0, 'Buildable': 0}
        # Use simple connection system for blueprint nodes
        self.connections = []
        # Prevent recursion in connection updates
        self._updating_connections = False
        
    def showContextMenu(self, event):
        """Enhanced context menu with node creation options."""
        menu = QMenu()
        
        # Node creation submenu
        create_menu = menu.addMenu("Create Node")
        
        # Blueprint node action
        blueprint_action = create_menu.addAction("📦 Blueprint Node")
        blueprint_action.triggered.connect(lambda: self.create_node_at_position("Blueprint", event.scenePos()))
        
        # Execution node action
        execution_action = create_menu.addAction("⚡ Execution Node")
        execution_action.triggered.connect(lambda: self.create_node_at_position("Execution", event.scenePos()))
        
        # Buildable node action
        buildable_action = create_menu.addAction("🔧 Buildable Node")
        buildable_action.triggered.connect(lambda: self.create_node_at_position("Buildable", event.scenePos()))
        
        menu.addSeparator()
        
        # Scene operations
        clear_action = menu.addAction("Clear All Nodes")
        clear_action.triggered.connect(self.clear_all_nodes)
        
        # Selection operations if there are selected items
        selected_items = self.selectedItems()
        if selected_items:
            menu.addSeparator()
            
            delete_selected_action = menu.addAction(f"Delete Selected ({len(selected_items)})")
            delete_selected_action.triggered.connect(self.delete_selected_nodes)
            
            if len(selected_items) > 1:
                align_menu = menu.addMenu("Align Selected")
                
                align_left_action = align_menu.addAction("Align Left")
                align_left_action.triggered.connect(lambda: self.align_selected_nodes("left"))
                
                align_right_action = align_menu.addAction("Align Right")
                align_right_action.triggered.connect(lambda: self.align_selected_nodes("right"))
                
                align_top_action = align_menu.addAction("Align Top")
                align_top_action.triggered.connect(lambda: self.align_selected_nodes("top"))
                
                align_bottom_action = align_menu.addAction("Align Bottom")
                align_bottom_action.triggered.connect(lambda: self.align_selected_nodes("bottom"))
                
                distribute_menu = menu.addMenu("Distribute Selected")
                
                distribute_h_action = distribute_menu.addAction("Distribute Horizontally")
                distribute_h_action.triggered.connect(lambda: self.distribute_selected_nodes("horizontal"))
                
                distribute_v_action = distribute_menu.addAction("Distribute Vertically")
                distribute_v_action.triggered.connect(lambda: self.distribute_selected_nodes("vertical"))
        
        # Legacy comment box support
        menu.addSeparator()
        addCommentAction = menu.addAction("Add Comment Box")
        
        # Convert scene position to global position for the menu
        view = self.views()[0] if self.views() else None
        if view:
            global_pos = view.mapToGlobal(view.mapFromScene(event.scenePos()))
        else:
            global_pos = event.screenPos()
        
        # Store scene position for later use
        scene_pos = event.scenePos()
        
        # Show menu and handle action
        action = menu.exec_(global_pos)
        if action == addCommentAction:
            name, ok = QInputDialog.getText(None, "New Comment Box", 
                                          "Enter comment box name:")
            if ok and name:
                from vpy_graph import CommentBox
                comment_box = CommentBox(name, scene_pos.x(), scene_pos.y())
                self.addItem(comment_box)
                
    def create_node_at_position(self, node_type, position):
        """Create a new node at the specified position."""
        # Show creation dialog
        dialog = NodeCreationDialog(node_type)
        if dialog.exec_() != QDialog.Accepted:
            return
            
        # Get node data from dialog
        data = dialog.get_node_data()
        
        # Create the appropriate node type
        try:
            if node_type == "Blueprint":
                node = BlueprintNode(
                    name=data['name'],
                    content=data.get('content', '')
                )
                # Process content change to trigger resizing
                if data.get('content', '').strip():
                    node.process_content_change("", data.get('content', ''))
            elif node_type == "Execution":
                node = ExecutionNode(
                    name=data['name'],
                    original_name=data.get('original_name', data['name'])
                )
            elif node_type == "Buildable":
                node = BuildableNode(
                    name=data['name'],
                    content=data.get('content', '')
                )
            else:
                QMessageBox.warning(None, "Error", f"Unknown node type: {node_type}")
                return
                
            # Position the node
            node.setPos(position)
            
            # Add to scene
            self.addItem(node)
            
            # Update counter
            self.node_counter[node_type] += 1
            
            print(f"Created {node_type} node '{data['name']}' at {position}")
            
        except Exception as e:
            QMessageBox.critical(None, "Error Creating Node", 
                               f"Failed to create {node_type} node:\n{str(e)}")
            
    def clear_all_nodes(self):
        """Clear all nodes from the scene."""
        reply = QMessageBox.question(
            None, "Clear All Nodes",
            "Are you sure you want to remove all nodes from the scene?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove all node items
            items_to_remove = []
            for item in self.items():
                if hasattr(item, 'node_type'):  # Our custom nodes
                    items_to_remove.append(item)
                    
            for item in items_to_remove:
                self.removeItem(item)
                
            # Reset counters
            self.node_counter = {'Blueprint': 0, 'Execution': 0, 'Buildable': 0}
            print("Cleared all nodes from scene")
            
    def delete_selected_nodes(self):
        """Delete all selected nodes."""
        selected_items = self.selectedItems()
        node_items = [item for item in selected_items if hasattr(item, 'node_type')]
        
        if not node_items:
            return
            
        reply = QMessageBox.question(
            None, "Delete Selected Nodes",
            f"Are you sure you want to delete {len(node_items)} selected node(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for item in node_items:
                # Disconnect all connections
                if hasattr(item, 'disconnect_all'):
                    item.disconnect_all()
                self.removeItem(item)
            print(f"Deleted {len(node_items)} selected nodes")
            
    def align_selected_nodes(self, alignment):
        """Align selected nodes."""
        selected_items = [item for item in self.selectedItems() if hasattr(item, 'node_type')]
        
        if len(selected_items) < 2:
            return
            
        # Get reference position (first selected node)
        ref_item = selected_items[0]
        ref_pos = ref_item.pos()
        
        for item in selected_items[1:]:
            current_pos = item.pos()
            
            if alignment == "left":
                item.setPos(ref_pos.x(), current_pos.y())
            elif alignment == "right":
                item.setPos(ref_pos.x() + ref_item.rect().width() - item.rect().width(), current_pos.y())
            elif alignment == "top":
                item.setPos(current_pos.x(), ref_pos.y())
            elif alignment == "bottom":
                item.setPos(current_pos.x(), ref_pos.y() + ref_item.rect().height() - item.rect().height())
                
        print(f"Aligned {len(selected_items)} nodes to {alignment}")
        
    def distribute_selected_nodes(self, direction):
        """Distribute selected nodes evenly."""
        selected_items = [item for item in self.selectedItems() if hasattr(item, 'node_type')]
        
        if len(selected_items) < 3:
            QMessageBox.information(None, "Info", "Need at least 3 nodes to distribute")
            return
            
        # Sort by position
        if direction == "horizontal":
            selected_items.sort(key=lambda item: item.pos().x())
        else:
            selected_items.sort(key=lambda item: item.pos().y())
            
        # Calculate spacing
        first_item = selected_items[0]
        last_item = selected_items[-1]
        
        if direction == "horizontal":
            total_distance = last_item.pos().x() - first_item.pos().x()
            spacing = total_distance / (len(selected_items) - 1)
            
            for i, item in enumerate(selected_items[1:-1], 1):
                new_x = first_item.pos().x() + (spacing * i)
                item.setPos(new_x, item.pos().y())
        else:
            total_distance = last_item.pos().y() - first_item.pos().y()
            spacing = total_distance / (len(selected_items) - 1)
            
            for i, item in enumerate(selected_items[1:-1], 1):
                new_y = first_item.pos().y() + (spacing * i)
                item.setPos(item.pos().x(), new_y)
                
        print(f"Distributed {len(selected_items)} nodes {direction}ly")
        
    def mousePressEvent(self, event):
        """Enhanced mouse press handling for connection creation."""
        if event.button() == Qt.LeftButton:
            from PyQt5.QtWidgets import QApplication
            from vpy_node_base import BaseNode
            modifiers = QApplication.keyboardModifiers()
            
            # First, check ALL nodes for port hits - including ports that extend outside node bounds
            scene_pos = event.scenePos()
            port_found = False
            
            # Check all nodes in the scene for port proximity
            for item in self.items():
                if isinstance(item, BaseNode):
                    # Check if we're close to any ports on this node
                    found_port, clicked_port = self.check_port_proximity(item, scene_pos)
                    if found_port:
                        # Start connection from this port
                        if not self.connection_in_progress:
                            self.connection_in_progress = SimpleConnection(
                                clicked_port, event.scenePos(), self
                            )
                            self.active_connection_point = clicked_port
                            port_type = "output" if clicked_port.type.value == 'output' else "input"
                            print(f"Started connection from {item.name}:{clicked_port.id} ({port_type})")
                            event.accept()  # Consume the event to prevent rubber band selection
                            port_found = True
                            return
            
            # If no port was found, handle regular scene interactions
            if not port_found:
                # Check if we're clicking on a node (but not a port)
                items = self.items(event.scenePos())
                if not items and not (modifiers & Qt.ControlModifier):
                    # Clicking on empty space without Ctrl - clear all selections
                    for item in self.selectedItems():
                        item.setSelected(False)
                        if hasattr(item, 'set_state'):
                            from vpy_node_base import NodeState
                            item.set_state(NodeState.NORMAL)
                        
        elif event.button() == Qt.RightButton:
            # Only show context menu if clicking on empty space
            items = self.items(event.scenePos())
            if not items:  # If no items under cursor
                self.showContextMenu(event)
        
        # Only call super if we didn't handle connection creation
        if not (hasattr(self, 'connection_in_progress') and self.connection_in_progress):
            super().mousePressEvent(event)
            
    def check_port_proximity(self, node, scene_pos):
        """Check if scene position is close to any port on the given node.
        
        Returns (bool, port) where bool indicates if a port was found,
        and port is the ConnectionPort object if found, None otherwise.
        """
        # Port hit detection radius
        port_radius = 30  # Generous hitbox for ports that extend outside nodes
        
        # Check output ports first
        for port_id, port in node.output_ports.items():
            # Get port position in scene coordinates
            port_scene_pos = node.mapToScene(port.position)
            
            # Calculate distance from click to port center
            dx = scene_pos.x() - port_scene_pos.x()
            dy = scene_pos.y() - port_scene_pos.y()
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= port_radius:
                return True, port
        
        # Check input ports
        for port_id, port in node.input_ports.items():
            # Get port position in scene coordinates
            port_scene_pos = node.mapToScene(port.position)
            
            # Calculate distance from click to port center
            dx = scene_pos.x() - port_scene_pos.x()
            dy = scene_pos.y() - port_scene_pos.y()
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= port_radius:
                return True, port
        
        return False, None
        
    def mouseReleaseEvent(self, event):
        """Handle connection completion."""
        if self.connection_in_progress:
            valid_connection = False
            from vpy_node_base import BaseNode
            scene_pos = event.scenePos()
            
            # Check all nodes for target port proximity (not just those under cursor)
            for item in self.items():
                if isinstance(item, BaseNode) and item != self.active_connection_point.node:
                    # Check if we're close to a compatible port
                    found_port, target_port = self.check_port_proximity_for_connection(
                        item, scene_pos, self.active_connection_point
                    )
                    
                    if found_port and target_port:
                        # STRICT node type compatibility - only same types can connect
                        start_node = self.active_connection_point.node
                        end_node = target_port.node
                        
                        # Check if both nodes have node_type attribute
                        if not (hasattr(start_node, 'node_type') and hasattr(end_node, 'node_type')):
                            print(f"Connection failed: One or both nodes missing node_type attribute")
                            continue
                            
                        # Only allow connections between nodes of the exact same type
                        nodes_compatible = (start_node.node_type == end_node.node_type)
                        
                        if nodes_compatible:
                            self.connection_in_progress.setEndPoint(target_port)
                            valid_connection = True
                            node_type_name = start_node.node_type.value.capitalize()
                            print(f"✅ Created {node_type_name} connection: {start_node.name}:{self.active_connection_point.id} → {end_node.name}:{target_port.id}")
                            break
                        else:
                            start_type = start_node.node_type.value.capitalize()
                            end_type = end_node.node_type.value.capitalize()
                            print(f"❌ Cannot connect {start_type} node '{start_node.name}' to {end_type} node '{end_node.name}' - incompatible node types")
                            # Don't break here - continue checking other potential targets
            
            if not valid_connection:
                # Remove invalid connection
                self.removeItem(self.connection_in_progress)
                if self.active_connection_point and hasattr(self.active_connection_point, 'remove_connection'):
                    self.active_connection_point.remove_connection(self.connection_in_progress)
                # Also remove from connections list
                if hasattr(self, 'connections') and self.connection_in_progress in self.connections:
                    self.connections.remove(self.connection_in_progress)
                print("❌ Connection cancelled - no valid target found")
                    
            self.connection_in_progress = None
            self.active_connection_point = None
            
        super().mouseReleaseEvent(event)
        
    def check_port_proximity_for_connection(self, node, scene_pos, source_port):
        """Check if scene position is close to a compatible port for connection.
        
        Only returns ports that can connect to the source port AND are on compatible node types.
        """
        port_radius = 30  # Match the radius from check_port_proximity
        
        # FIRST: Check node type compatibility before even looking at ports
        source_node = source_port.node
        target_node = node
        
        # Strict type checking - both nodes must have node_type and they must match
        if not (hasattr(source_node, 'node_type') and hasattr(target_node, 'node_type')):
            return False, None
            
        if source_node.node_type != target_node.node_type:
            return False, None  # Incompatible node types - don't even check ports
        
        # Node types are compatible, now check port proximity and direction
        # Determine which ports to check based on source port type
        if source_port.type.value == 'output':
            # Source is output, look for input ports
            ports_to_check = node.input_ports
        else:
            # Source is input, look for output ports  
            ports_to_check = node.output_ports
        
        # Check the appropriate ports for proximity
        for port_id, port in ports_to_check.items():
            # Get port position in scene coordinates
            port_scene_pos = node.mapToScene(port.position)
            
            # Calculate distance from click to port center
            dx = scene_pos.x() - port_scene_pos.x()
            dy = scene_pos.y() - port_scene_pos.y()
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= port_radius:
                return True, port
        
        return False, None
        
    def mouseMoveEvent(self, event):
        """Handle connection dragging."""
        if self.connection_in_progress:
            self.connection_in_progress.end_pos = event.scenePos()
            self.connection_in_progress.updatePath()
        super().mouseMoveEvent(event)
        
        # Update all completed connections when nodes move
        # This ensures connection lines follow nodes as they are dragged
        self.update_all_connections()
        
    def update_all_connections(self):
        """Update all connection lines to follow moving nodes."""
        if hasattr(self, 'connections'):
            for connection in self.connections:
                if hasattr(connection, 'updateForNodeMovement'):
                    connection.updateForNodeMovement()

class NodeSystemDebugWindow(QMainWindow):
    """Comprehensive debug window for the node system."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VysualPy Node System Debug")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add instructions
        instructions = QLabel(
            "Node System Debug Environment\n\n" +
            "• Right-click in empty space to create nodes\n" +
            "• Click and drag from output ports to input ports to create connections\n" +
            "• Drag connection lines to move both connected nodes together\n" +
            "• Drag to select multiple nodes (rubber band selection)\n" +
            "• Ctrl+Click to add/remove nodes from selection\n" +
            "• Drag selected nodes to move them together\n" +
            "• Right-click on selected nodes for group operations\n" +
            "• Right-click connection lines to break them\n" +
            "• Alt+Drag to pan view, Ctrl+Wheel to zoom\n" +
            "• Double-click nodes to edit (where supported)"
        )
        instructions.setStyleSheet(
            "color: white; background-color: #2c3e50; padding: 12px; " +
            "font-size: 11px; border: 2px solid #34495e; margin: 5px; " +
            "border-radius: 5px;"
        )
        layout.addWidget(instructions)
        
        # Create enhanced scene and view
        self.scene = EnhancedBlueprintScene()
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        
        self.view = BlueprintView(self.scene)
        layout.addWidget(self.view)
        
        # Create some sample nodes to start with
        self.create_sample_nodes()
        
        # Status tracking
        self.node_count = 0
        self.update_window_title()
        
    def create_sample_nodes(self):
        """Create some sample nodes to demonstrate functionality."""
        # Sample Blueprint node
        blueprint_node = BlueprintNode(
            name="sample_function",
            content="def sample_function(x, y):\n    \"\"\"Sample function for testing.\"\"\"\n    return x + y"
        )
        blueprint_node.setPos(-200, -100)
        self.scene.addItem(blueprint_node)
        
        # Sample Execution node
        execution_node = ExecutionNode(
            name="sample_function",
            original_name="Sample Execution"
        )
        execution_node.setPos(100, -100)
        self.scene.addItem(execution_node)
        
        # Sample Buildable node
        buildable_node = BuildableNode(
            name="test_code",
            content="# Test buildable code\nresult = sample_function(5, 10)\nprint(f'Result: {result}')"
        )
        buildable_node.setPos(-50, 100)
        self.scene.addItem(buildable_node)
        
        self.node_count = 3
        self.update_window_title()
        
    def update_window_title(self):
        """Update window title with current node count."""
        total_nodes = len([item for item in self.scene.items() if hasattr(item, 'node_type')])
        self.setWindowTitle(f"VysualPy Node System Debug - {total_nodes} nodes")

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("VysualPy Node System Debug")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("VysualPy")
    
    window = NodeSystemDebugWindow()
    window.show()
    
    print("Node System Debug Environment Started")
    print("=" * 50)
    print("Available Features:")
    print("  - Right-click context menus for node creation")
    print("  - Multi-selection and group operations")
    print("  - Node alignment and distribution tools")
    print("  - Visual feedback and state management")
    print("  - Comprehensive node editing capabilities")
    print("=" * 50)
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
