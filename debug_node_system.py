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
        
        # Enhanced tooltip with connection information
        self.update_tooltip()
        
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
        
        # Update tooltip with completed connection information
        self.update_tooltip()
        
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
        
    def update_tooltip(self):
        """Update tooltip with enhanced connection information."""
        if self.is_completed and self.end_port:
            # Complete connection - show detailed info
            start_node = self.start_port.node
            end_node = self.end_port.node
            
            # Determine node types
            start_type = "Unknown"
            end_type = "Unknown"
            if hasattr(start_node, 'node_type'):
                start_type = start_node.node_type.value.capitalize()
            if hasattr(end_node, 'node_type'):
                end_type = end_node.node_type.value.capitalize()
            
            # Create detailed tooltip
            tooltip_parts = [
                f"🔗 {start_type} Connection",
                f"Source: {start_node.name} [{self.start_port.id}]",
                f"Target: {end_node.name} [{self.end_port.id}]",
                "",
                "Connection Details:"
            ]
            
            # Add node type specific information
            if start_type == "Blueprint" and end_type == "Blueprint":
                tooltip_parts.append("📦 Structural relationship between code components")
                tooltip_parts.append("• Shows function call or class dependency")
                tooltip_parts.append("• Bidirectional logical connection")
                
            elif start_type == "Execution" and end_type == "Execution":
                tooltip_parts.append("⚡ Runtime execution flow")
                tooltip_parts.append("• Shows actual function call sequence")
                tooltip_parts.append("• Directional execution path")
                
            elif start_type == "Buildable" and end_type == "Buildable":
                tooltip_parts.append("🔧 Code reference dependency")
                tooltip_parts.append("• Automatically detected from code analysis")
                tooltip_parts.append("• Shows variable/function references")
                
            # Add interaction hints
            tooltip_parts.extend([
                "",
                "Interaction:",
                "• Drag to move both connected nodes",
                "• Right-click to break connection",
                "• Hover for highlight and thickness change"
            ])
            
            tooltip_text = "\n".join(tooltip_parts)
            
        elif self.start_port:
            # Incomplete connection - show creation info
            start_node = self.start_port.node
            start_type = "Unknown"
            if hasattr(start_node, 'node_type'):
                start_type = start_node.node_type.value.capitalize()
                
            tooltip_text = f"🚧 Creating {start_type} Connection\n\nSource: {start_node.name} [{self.start_port.id}]\n\nDrag to a compatible input port to complete the connection."
            
        else:
            # Fallback for incomplete state
            tooltip_text = "🔗 Connection Line\n\nHover for details when connection is complete."
            
        self.setToolTip(tooltip_text)

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
            
            # If this is a BuildableNode and we have a connected global editor, add it
            if (node_type == "Buildable" and hasattr(self, 'global_editor') and 
                self.global_editor is not None):
                self.global_editor.add_node(node)
                print(f"Added new BuildableNode '{data['name']}' to global editor")
            
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
                            # For Blueprint nodes only: Check if this connection already exists
                            if (hasattr(start_node, 'node_type') and 
                                start_node.node_type.value == 'blueprint'):
                                
                                # Check if a connection already exists between these two nodes
                                connection_exists = self.check_blueprint_connection_exists(
                                    start_node, end_node
                                )
                                
                                if connection_exists:
                                    print(f"❌ Blueprint connection already exists between '{start_node.name}' and '{end_node.name}' - duplicate connections not allowed")
                                    continue  # Skip this connection and continue checking other targets
                            
                            # Connection is valid - create it
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
            
        # DISABLE MANUAL CONNECTIONS FOR BUILDABLE NODES - they are code-driven
        if (hasattr(source_node, 'node_type') and source_node.node_type.value == 'buildable') or \
           (hasattr(target_node, 'node_type') and target_node.node_type.value == 'buildable'):
            print(f"❌ Manual connections disabled for BuildableNodes - use code references instead")
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
    
    def check_blueprint_connection_exists(self, start_node, end_node):
        """Check if a connection already exists between two blueprint nodes.
        
        Args:
            start_node: The source node of the potential connection
            end_node: The target node of the potential connection
            
        Returns:
            bool: True if a connection already exists between these nodes (in either direction)
        """
        # Only check for blueprint nodes
        if not (hasattr(start_node, 'node_type') and hasattr(end_node, 'node_type')):
            return False
            
        if start_node.node_type.value != 'blueprint' or end_node.node_type.value != 'blueprint':
            return False
        
        # Check all existing connections in the scene
        if hasattr(self, 'connections'):
            for connection in self.connections:
                if (hasattr(connection, 'start_port') and hasattr(connection, 'end_port') and 
                    connection.end_port is not None):
                    
                    connection_start = connection.start_port.node
                    connection_end = connection.end_port.node
                    
                    # Check if this connection already exists (in either direction)
                    # Blueprint connections are bidirectional in terms of preventing duplicates
                    if ((connection_start == start_node and connection_end == end_node) or
                        (connection_start == end_node and connection_end == start_node)):
                        return True
        
        return False
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for node operations."""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication
        
        # Get keyboard modifiers
        modifiers = QApplication.keyboardModifiers()
        
        # CTRL+S - Child Vertical Align
        if (event.key() == Qt.Key_S and 
            modifiers == Qt.ControlModifier):
            self.align_child_nodes_vertically()
            event.accept()
            return
            
        # CTRL+SHIFT+S - Full Tree Align
        if (event.key() == Qt.Key_S and 
            modifiers == (Qt.ControlModifier | Qt.ShiftModifier)):
            self.align_full_tree()
            event.accept()
            return
            
        # Let parent handle other key events
        super().keyPressEvent(event)
        
    def align_child_nodes_vertically(self):
        """Align direct children of selected nodes vertically to the right."""
        selected_items = [item for item in self.selectedItems() if hasattr(item, 'node_type')]
        
        if not selected_items:
            print("❌ No nodes selected for child alignment")
            return
            
        aligned_count = 0
        
        for parent_node in selected_items:
            # Find direct children (nodes connected via output ports)
            children = self.get_direct_children(parent_node)
            
            if not children:
                print(f"ℹ️  Node '{parent_node.name}' has no direct children to align")
                continue
                
            # Sort children by current Y position for consistent ordering
            children.sort(key=lambda child: child.pos().y())
            
            # Calculate alignment position (to the right of parent)
            parent_pos = parent_node.pos()
            parent_width = parent_node.boundingRect().width()
            align_x = parent_pos.x() + parent_width + 100  # 100px spacing
            
            # Calculate vertical spacing
            if len(children) > 1:
                total_height = sum(child.boundingRect().height() for child in children)
                spacing = max(50, total_height / len(children) * 0.3)  # Minimum 50px spacing
            else:
                spacing = 0
            
            # Start Y position (center children around parent's center)
            parent_center_y = parent_pos.y() + parent_node.boundingRect().height() / 2
            total_children_height = (len(children) - 1) * spacing
            start_y = parent_center_y - total_children_height / 2
            
            # Align children vertically
            for i, child in enumerate(children):
                new_y = start_y + (i * spacing)
                child.setPos(align_x, new_y)
                aligned_count += 1
                
            print(f"✅ Aligned {len(children)} children of '{parent_node.name}' vertically")
        
        # Update all connections after moving nodes
        self.update_all_connections()
        
        if aligned_count > 0:
            print(f"🎯 CTRL+S: Aligned {aligned_count} child nodes vertically")
        else:
            print("ℹ️  No child nodes found to align")
            
    def align_full_tree(self):
        """Recursively align entire node tree with intelligent spacing."""
        selected_items = [item for item in self.selectedItems() if hasattr(item, 'node_type')]
        
        if not selected_items:
            print("❌ No nodes selected for tree alignment")
            return
            
        aligned_count = 0
        processed_nodes = set()
        
        for root_node in selected_items:
            if root_node in processed_nodes:
                continue
                
            # Perform recursive tree alignment
            aligned_in_tree = self.align_node_tree_recursive(root_node, 0, processed_nodes)
            aligned_count += aligned_in_tree
            
        # Update all connections after moving nodes
        self.update_all_connections()
        
        if aligned_count > 0:
            print(f"🌳 CTRL+SHIFT+S: Aligned {aligned_count} nodes in full tree structure")
        else:
            print("ℹ️  No tree structure found to align")
            
    def align_node_tree_recursive(self, node, depth, processed_nodes, start_y=None):
        """Recursively align a node and all its descendants."""
        if node in processed_nodes:
            return 0
            
        processed_nodes.add(node)
        aligned_count = 0
        
        # Get direct children
        children = self.get_direct_children(node)
        
        if not children:
            return aligned_count  # Leaf node
            
        # Sort children by current Y position for consistent ordering
        children.sort(key=lambda child: child.pos().y())
        
        # Calculate horizontal position based on depth
        node_pos = node.pos()
        node_width = node.boundingRect().width()
        child_x = node_pos.x() + node_width + (120 + depth * 20)  # Increasing spacing per depth
        
        # Calculate vertical positioning
        if start_y is None:
            # For root level, center around the parent
            node_center_y = node_pos.y() + node.boundingRect().height() / 2
        else:
            node_center_y = start_y + node.boundingRect().height() / 2
            
        # Calculate total space needed for all children and their subtrees
        child_heights = []
        for child in children:
            subtree_height = self.calculate_subtree_height(child, processed_nodes.copy())
            child_heights.append(max(child.boundingRect().height(), subtree_height))
            
        total_height = sum(child_heights) + (len(children) - 1) * 60  # 60px between child groups
        start_y = node_center_y - total_height / 2
        
        # Position and recursively align children
        current_y = start_y
        for i, child in enumerate(children):
            child.setPos(child_x, current_y)
            aligned_count += 1
            
            # Recursively align the child's subtree
            subtree_aligned = self.align_node_tree_recursive(
                child, depth + 1, processed_nodes, current_y
            )
            aligned_count += subtree_aligned
            
            # Move to next child position
            current_y += child_heights[i] + 60
            
        print(f"🌿 Aligned node '{node.name}' with {len(children)} children at depth {depth}")
        return aligned_count
        
    def calculate_subtree_height(self, node, processed_nodes):
        """Calculate the total height needed for a node's subtree."""
        if node in processed_nodes:
            return node.boundingRect().height()
            
        processed_nodes.add(node)
        children = self.get_direct_children(node)
        
        if not children:
            return node.boundingRect().height()
            
        child_heights = [self.calculate_subtree_height(child, processed_nodes) for child in children]
        total_children_height = sum(child_heights) + (len(children) - 1) * 60
        
        return max(node.boundingRect().height(), total_children_height)
        
    def get_direct_children(self, parent_node):
        """Get all nodes directly connected as children from this node's output ports."""
        children = []
        
        if not hasattr(self, 'connections'):
            return children
            
        for connection in self.connections:
            if (hasattr(connection, 'start_port') and hasattr(connection, 'end_port') and
                connection.start_port and connection.end_port and
                connection.start_port.node == parent_node):
                # This connection starts from the parent node
                child_node = connection.end_port.node
                if child_node not in children:
                    children.append(child_node)
                    
        return children

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
                    
    def analyze_node_references(self, node):
        """Analyze a node's content to find references to other nodes and create automatic connections."""
        if not hasattr(node, 'node_type') or node.node_type.value != 'buildable':
            return  # Only analyze BuildableNodes
            
        if not hasattr(node, 'content') or not node.content.strip():
            return  # No content to analyze
            
        # Find all nodes in the scene
        all_nodes = [item for item in self.items() if hasattr(item, 'node_type')]
        buildable_nodes = [n for n in all_nodes if n.node_type.value == 'buildable' and n != node]
        
        if not buildable_nodes:
            return  # No other BuildableNodes to connect to
            
        # Analyze code content for function/variable references
        import re
        import ast
        
        try:
            # Parse the content as AST to find function calls and name references
            parsed = ast.parse(node.content)
            referenced_names = set()
            
            # Walk the AST to find Name and Call nodes
            for ast_node in ast.walk(parsed):
                if isinstance(ast_node, ast.Name):
                    referenced_names.add(ast_node.id)
                elif isinstance(ast_node, ast.Call):
                    if isinstance(ast_node.func, ast.Name):
                        referenced_names.add(ast_node.func.id)
                    elif isinstance(ast_node.func, ast.Attribute):
                        # Handle method calls like obj.method()
                        if isinstance(ast_node.func.value, ast.Name):
                            referenced_names.add(ast_node.func.value.id)
                            
            # Remove common built-in names that shouldn't trigger connections
            builtin_names = {'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
                           'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed',
                           'min', 'max', 'sum', 'abs', 'round', 'isinstance', 'hasattr', 'getattr',
                           'setattr', 'import', 'from', 'def', 'class', 'if', 'else', 'elif',
                           'for', 'while', 'try', 'except', 'finally', 'with', 'return', 'yield',
                           'pass', 'break', 'continue', 'None', 'True', 'False'}
            referenced_names = referenced_names - builtin_names
            
            # Check each referenced name against other BuildableNode names
            for target_node in buildable_nodes:
                target_name = target_node.name.lower().strip()
                
                # Check if any referenced name matches the target node name
                for ref_name in referenced_names:
                    if self.names_match(ref_name.lower(), target_name):
                        # Create automatic connection if it doesn't exist
                        self.create_automatic_connection(target_node, node, ref_name)
                        break
                        
        except Exception as e:
            print(f"Error analyzing node references for {node.name}: {e}")
            
    def names_match(self, ref_name, node_name):
        """Check if a referenced name matches a node name (with some fuzzy matching)."""
        # Direct match
        if ref_name == node_name:
            return True
            
        # Remove common prefixes/suffixes and check
        clean_ref = ref_name.replace('_', '').replace('-', '')
        clean_node = node_name.replace('_', '').replace('-', '').replace('node', '').replace('code', '')
        
        if clean_ref == clean_node:
            return True
            
        # Check if reference is contained in node name or vice versa
        if len(ref_name) > 3 and (ref_name in node_name or node_name in ref_name):
            return True
            
        return False
        
    def create_automatic_connection(self, source_node, target_node, reference_name):
        """Create an automatic connection between two BuildableNodes."""
        # Check if connection already exists
        if self.connection_exists_between_nodes(source_node, target_node):
            return  # Connection already exists
            
        # Find suitable ports for connection
        source_output_port = None
        target_input_port = None
        
        # Find the best output port on source node (prefer exec_out)
        if 'exec_out' in source_node.output_ports:
            source_output_port = source_node.output_ports['exec_out']
        elif source_node.output_ports:
            # Use any available output port
            source_output_port = next(iter(source_node.output_ports.values()))
            
        # Find the best input port on target node (prefer exec_in)
        if 'exec_in' in target_node.input_ports:
            target_input_port = target_node.input_ports['exec_in']
        elif target_node.input_ports:
            # Use any available input port
            target_input_port = next(iter(target_node.input_ports.values()))
            
        if source_output_port and target_input_port:
            # Create the connection
            start_pos = source_node.mapToScene(source_output_port.position)
            connection = SimpleConnection(source_output_port, start_pos, self)
            connection.setEndPoint(target_input_port)
            
            print(f"🔗 Automatic connection created: {source_node.name} → {target_node.name} (reference: '{reference_name}')")
            
    def connection_exists_between_nodes(self, node1, node2):
        """Check if a connection already exists between two nodes (in either direction)."""
        if not hasattr(self, 'connections'):
            return False
            
        for connection in self.connections:
            if (hasattr(connection, 'start_port') and hasattr(connection, 'end_port') and 
                connection.end_port is not None):
                
                start_node = connection.start_port.node
                end_node = connection.end_port.node
                
                # Check both directions
                if ((start_node == node1 and end_node == node2) or
                    (start_node == node2 and end_node == node1)):
                    return True
                    
        return False
        
    def set_global_editor(self, global_editor):
        """Connect this scene to a global text editor for real-time node tracking."""
        self.global_editor = global_editor
        
        # Scan existing BuildableNodes and add them to the editor
        existing_buildable_nodes = [item for item in self.items() 
                                   if hasattr(item, 'node_type') and 
                                   item.node_type.value == 'buildable']
        
        for node in existing_buildable_nodes:
            self.global_editor.add_node(node)
            
        print(f"Connected scene to global editor - tracking {len(existing_buildable_nodes)} existing BuildableNodes")

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
            "• Hover over connections for detailed tooltips\n" +
            "• Drag to select multiple nodes (rubber band selection)\n" +
            "• Ctrl+Click to add/remove nodes from selection\n" +
            "• Drag selected nodes to move them together\n" +
            "• Right-click on selected nodes for group operations\n" +
            "• Right-click connection lines to break them\n" +
            "• Ctrl+S: Align direct children vertically\n" +
            "• Ctrl+Shift+S: Align entire tree structure\n" +
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
        
        # Open external text editor window for demo
        self.open_demo_text_editor()
        
    def create_sample_nodes(self):
        """Create some sample nodes to demonstrate functionality."""
        # Sample Blueprint node
        blueprint_node = BlueprintNode(
            name="sample_function",
            content="def sample_function(x, y):\n    \"\"\"Sample function for testing.\"\"\"\n    return x + y"
        )
        blueprint_node.setPos(-200, -100)
        self.scene.addItem(blueprint_node)
        
        # Sample Buildable node
        buildable_node = BuildableNode(
            name="test_code",
            content="# Test buildable code\nresult = sample_function(5, 10)\nprint(f'Result: {result}')"
        )
        buildable_node.setPos(-50, 100)
        self.scene.addItem(buildable_node)
        
        # Create interconnected execution nodes to demonstrate function call relationships
        
        # Main function - calls validate_input and process_data
        main_exec = ExecutionNode(
            name="main_workflow",
            original_name="Main Workflow Function"
        )
        main_exec.setPos(300, -200)
        self.scene.addItem(main_exec)
        
        # Input validation function - called by main, calls log_error
        validate_exec = ExecutionNode(
            name="validate_input", 
            original_name="Input Validation Function"
        )
        validate_exec.setPos(500, -100)
        self.scene.addItem(validate_exec)
        
        # Data processing function - called by main, calls save_result and log_info
        process_exec = ExecutionNode(
            name="process_data",
            original_name="Data Processing Function"
        )
        process_exec.setPos(500, -300)
        self.scene.addItem(process_exec)
        
        # Logging functions - called by various other functions
        log_error_exec = ExecutionNode(
            name="log_error",
            original_name="Error Logging Function"
        )
        log_error_exec.setPos(700, -50)
        self.scene.addItem(log_error_exec)
        
        log_info_exec = ExecutionNode(
            name="log_info",
            original_name="Info Logging Function"
        )
        log_info_exec.setPos(700, -150)
        self.scene.addItem(log_info_exec)
        
        # Utility functions
        save_result_exec = ExecutionNode(
            name="save_result",
            original_name="Save Result Function"
        )
        save_result_exec.setPos(700, -250)
        self.scene.addItem(save_result_exec)
        
        # Helper function - called by process_data and save_result
        format_output_exec = ExecutionNode(
            name="format_output",
            original_name="Format Output Function"
        )
        format_output_exec.setPos(700, -350)
        self.scene.addItem(format_output_exec)
        
        self.node_count = 9
        self.update_window_title()
        
    def update_window_title(self):
        """Update window title with current node count."""
        total_nodes = len([item for item in self.scene.items() if hasattr(item, 'node_type')])
        self.setWindowTitle(f"VysualPy Node System Debug - {total_nodes} nodes")
        
    def open_demo_text_editor(self):
        """Open a global text editor that tracks all BuildableNodes."""
        try:
            # Import the new global text editor
            from vpy_editor import GlobalNodeTextEditor
            
            # Create the global editor
            self.global_editor = GlobalNodeTextEditor(
                title="Debug Environment",
                parent=None  # Make it standalone
            )
            
            # IMPORTANT: Connect the scene to the global editor for real-time updates
            if hasattr(self.scene, 'set_global_editor'):
                self.scene.set_global_editor(self.global_editor)
            
            # Position it next to the debug window
            debug_geometry = self.geometry()
            editor_x = debug_geometry.x() + debug_geometry.width() + 20
            editor_y = debug_geometry.y()
            self.global_editor.move(editor_x, editor_y)
            
            # Show the editor
            self.global_editor.show()
            
            print("\n📝 GLOBAL NODE TEXT EDITOR OPENED")
            print("=" * 50)
            print("This editor automatically tracks ALL BuildableNodes:")
            print("  • Creates new nodes by coding (automatic connections)")
            print("  • Switch between nodes using the dropdown")
            print("  • Click 'Refresh Nodes' to find newly created nodes")
            print("  • Edit content and save to sync with the graph")
            print("  • Automatic connection detection based on code references")
            print("=" * 50)
            
        except Exception as e:
            print(f"Error opening global text editor: {e}")
            import traceback
            traceback.print_exc()

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
