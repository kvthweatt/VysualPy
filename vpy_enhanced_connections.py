#!/usr/bin/env python3
"""
Enhanced connection system for VysualPy.

This module provides the SimpleConnection class extracted from debug_node_system.py
with production-ready enhancements and integration with the main VysualPy system.
"""

from PyQt5.QtWidgets import QGraphicsPathItem, QMenu, QApplication
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QPainterPath, QCursor

class SimpleConnection(QGraphicsPathItem):
    """Enhanced connection line for node graphs (Unreal Engine Blueprint style)."""
    
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
        
        # Enable drag functionality for connection lines
        self.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        
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
        if scene:
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
                    if hasattr(self.scene, 'update_all_connections'):
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
            
            tooltip_text = "\\n".join(tooltip_parts)
            
        elif self.start_port:
            # Incomplete connection - show creation info
            start_node = self.start_port.node
            start_type = "Unknown"
            if hasattr(start_node, 'node_type'):
                start_type = start_node.node_type.value.capitalize()
                
            tooltip_text = f"🚧 Creating {start_type} Connection\\n\\nSource: {start_node.name} [{self.start_port.id}]\\n\\nDrag to a compatible input port to complete the connection."
            
        else:
            # Fallback for incomplete state
            tooltip_text = "🔗 Connection Line\\n\\nHover for details when connection is complete."
            
        self.setToolTip(tooltip_text)


# Compatibility layer for integration with existing code
# This allows gradual migration from the old Connection class
class EnhancedConnection(SimpleConnection):
    """Enhanced connection with full integration to existing VysualPy systems."""
    
    def __init__(self, start_port, end_pos_or_port, scene=None, **kwargs):
        # Handle both old and new calling conventions
        if hasattr(end_pos_or_port, 'position'):
            # Called with end port
            end_pos = end_pos_or_port.node.mapToScene(end_pos_or_port.position)
            super().__init__(start_port, end_pos, scene)
            self.setEndPoint(end_pos_or_port)
        else:
            # Called with end position
            super().__init__(start_port, end_pos_or_port, scene)
    
    def validate_node_compatibility(self):
        """Enhanced node type compatibility checking."""
        if not self.start_port or not self.end_port:
            return False
            
        start_node = self.start_port.node
        end_node = self.end_port.node
        
        # Check if both nodes have node_type attribute
        if not (hasattr(start_node, 'node_type') and hasattr(end_node, 'node_type')):
            return False
            
        # Only allow connections between nodes of the same type
        return start_node.node_type == end_node.node_type
    
    def check_duplicate_connection(self, scene):
        """Check for duplicate connections in blueprint nodes."""
        if not hasattr(self.start_port.node, 'node_type'):
            return False
            
        # Only check for blueprint nodes
        if self.start_port.node.node_type.value != 'blueprint':
            return False
            
        if not hasattr(scene, 'connections'):
            return False
            
        start_node = self.start_port.node
        end_node = self.end_port.node
        
        # Check all existing connections
        for connection in scene.connections:
            if (hasattr(connection, 'start_port') and hasattr(connection, 'end_port') and 
                connection.end_port is not None and connection != self):
                
                connection_start = connection.start_port.node
                connection_end = connection.end_port.node
                
                # Check if this connection already exists (in either direction)
                if ((connection_start == start_node and connection_end == end_node) or
                    (connection_start == end_node and connection_end == start_node)):
                    return True
        
        return False
