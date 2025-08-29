"""
Enhanced connection system for VysualPy.

Provides improved connection management, validation, and visual feedback
while maintaining backward compatibility with the existing system.
"""

from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import uuid

from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsScene
from PyQt5.QtCore import QPointF, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath

from vpy_node_base import BaseConnection, ConnectionPort


class ConnectionStyle(Enum):
    """Different visual styles for connections."""
    STRAIGHT = "straight"
    CURVED = "curved" 
    ORTHOGONAL = "orthogonal"
    BEZIER = "bezier"


class ConnectionState(Enum):
    """States a connection can be in."""
    NORMAL = "normal"
    HIGHLIGHTED = "highlighted"
    SELECTED = "selected"
    INVALID = "invalid"
    DIMMED = "dimmed"


class Connection(QGraphicsPathItem, BaseConnection):
    """
    Enhanced connection class with improved visuals and functionality.
    
    Supports multiple styles, validation, and proper event handling.
    """
    
    def __init__(self, 
                 start_port: ConnectionPort, 
                 end_pos_or_port,
                 scene: QGraphicsScene = None,
                 connection_id: str = None,
                 style: ConnectionStyle = ConnectionStyle.BEZIER):
        
        # Initialize QGraphicsPathItem first
        QGraphicsPathItem.__init__(self)
        
        # Handle end position or port
        if isinstance(end_pos_or_port, ConnectionPort):
            end_port = end_pos_or_port
            end_pos = end_port.position
        else:
            end_port = None
            end_pos = end_pos_or_port
            
        # Initialize BaseConnection (only if we have both ports)
        if end_port:
            BaseConnection.__init__(self, start_port, end_port, connection_id)
        else:
            # Temporary connection during creation
            self.id = connection_id or str(uuid.uuid4())
            self.start_port = start_port
            self.end_port = None
            self.metadata = {}
            start_port.add_connection(self)
        
        # Connection properties
        self.style = style
        self.state = ConnectionState.NORMAL
        self.end_pos = end_pos
        self.is_valid = True
        
        # Visual properties
        self.line_width = 2
        self.highlight_width = 3
        self.selected_width = 4
        
        # Color scheme
        self.colors = {
            ConnectionState.NORMAL: QColor(100, 100, 100),
            ConnectionState.HIGHLIGHTED: QColor(255, 165, 0),  # Orange
            ConnectionState.SELECTED: QColor(0, 120, 215),     # Blue
            ConnectionState.INVALID: QColor(255, 100, 100),    # Red
            ConnectionState.DIMMED: QColor(60, 60, 60)         # Dark gray
        }
        
        # Event handlers
        self.on_click_handlers: List[Callable] = []
        self.on_hover_handlers: List[Callable] = []
        self.validation_handlers: List[Callable] = []
        
        # Make connection selectable and hoverable
        self.setFlag(QGraphicsPathItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Update visual path
        self.updatePath()
        
        # Add to scene if provided
        if scene:
            scene.addItem(self)
    
    def setEndPoint(self, end_port: ConnectionPort):
        """Set the end port for this connection."""
        if self.end_port:
            # Remove from old end port
            self.end_port.remove_connection(self)
            
        self.end_port = end_port
        end_port.add_connection(self)
        
        # Validate the connection
        self.validate()
        
        # Update visual
        self.end_pos = end_port.position
        self.updatePath()
        
    def updatePath(self):
        """Update the visual path of the connection."""
        if not self.start_port:
            return
            
        start_pos = self.mapFromScene(self.start_port.node.mapToScene(self.start_port.position))
        end_pos = self.mapFromScene(self.end_pos) if hasattr(self.end_pos, 'x') else self.end_pos
        
        path = QPainterPath()
        
        if self.style == ConnectionStyle.STRAIGHT:
            path.moveTo(start_pos)
            path.lineTo(end_pos)
            
        elif self.style == ConnectionStyle.CURVED:
            # Simple curved connection
            control_offset = abs(end_pos.x() - start_pos.x()) * 0.5
            control1 = QPointF(start_pos.x() + control_offset, start_pos.y())
            control2 = QPointF(end_pos.x() - control_offset, end_pos.y())
            
            path.moveTo(start_pos)
            path.cubicTo(control1, control2, end_pos)
            
        elif self.style == ConnectionStyle.BEZIER:
            # Horizontal bezier curve (like Blender/UE)
            dx = end_pos.x() - start_pos.x()
            control_offset = max(abs(dx) * 0.3, 50)
            
            control1 = QPointF(start_pos.x() + control_offset, start_pos.y())
            control2 = QPointF(end_pos.x() - control_offset, end_pos.y())
            
            path.moveTo(start_pos)
            path.cubicTo(control1, control2, end_pos)
            
        elif self.style == ConnectionStyle.ORTHOGONAL:
            # Right-angle connections
            mid_x = (start_pos.x() + end_pos.x()) / 2
            
            path.moveTo(start_pos)
            path.lineTo(mid_x, start_pos.y())
            path.lineTo(mid_x, end_pos.y())
            path.lineTo(end_pos)
            
        self.setPath(path)
        self.updatePen()
        
    def updatePen(self):
        """Update the pen based on current state."""
        color = self.colors.get(self.state, self.colors[ConnectionState.NORMAL])
        
        if self.state == ConnectionState.SELECTED:
            width = self.selected_width
        elif self.state == ConnectionState.HIGHLIGHTED:
            width = self.highlight_width
        else:
            width = self.line_width
            
        pen = QPen(color, width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        
        if not self.is_valid:
            pen.setStyle(Qt.DashLine)
            
        self.setPen(pen)
        
    def validate(self) -> bool:
        """Validate this connection and update visual state."""
        if not self.start_port or not self.end_port:
            self.is_valid = False
            return False
            
        # Basic validation
        if not self.start_port.can_connect_to(self.end_port):
            self.is_valid = False
            self.state = ConnectionState.INVALID
            self.updatePen()
            return False
            
        # Custom validation handlers
        for handler in self.validation_handlers:
            try:
                if not handler(self):
                    self.is_valid = False
                    self.state = ConnectionState.INVALID
                    self.updatePen()
                    return False
            except Exception as e:
                print(f"Error in validation handler: {e}")
                
        self.is_valid = True
        if self.state == ConnectionState.INVALID:
            self.state = ConnectionState.NORMAL
        self.updatePen()
        return True
        
    def set_state(self, new_state: ConnectionState):
        """Change the connection state and update visuals."""
        self.state = new_state
        self.updatePen()
        
    def disconnect(self):
        """Override to handle QGraphicsItem cleanup."""
        # Call parent disconnect
        super().disconnect()
        
        # Remove from scene
        if self.scene():
            self.scene().removeItem(self)
            
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
            self.set_state(ConnectionState.SELECTED)
            
            # Trigger click handlers
            for handler in self.on_click_handlers:
                try:
                    handler(self, event)
                except Exception as e:
                    print(f"Error in click handler: {e}")
                    
        elif event.button() == Qt.RightButton:
            # Show context menu
            self.show_context_menu(event)
            
        super().mousePressEvent(event)
        
    def hoverEnterEvent(self, event):
        """Handle hover enter events."""
        if self.state not in [ConnectionState.SELECTED, ConnectionState.INVALID]:
            self.set_state(ConnectionState.HIGHLIGHTED)
            
        # Trigger hover handlers
        for handler in self.on_hover_handlers:
            try:
                handler(self, True)
            except Exception as e:
                print(f"Error in hover handler: {e}")
                
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle hover leave events."""
        if self.state == ConnectionState.HIGHLIGHTED:
            self.set_state(ConnectionState.NORMAL)
            
        # Trigger hover handlers
        for handler in self.on_hover_handlers:
            try:
                handler(self, False)
            except Exception as e:
                print(f"Error in hover handler: {e}")
                
        super().hoverLeaveEvent(event)
        
    def show_context_menu(self, event):
        """Show context menu for the connection."""
        from PyQt5.QtWidgets import QMenu, QAction, QMessageBox
        
        menu = QMenu()
        
        delete_action = QAction("Delete Connection", menu)
        delete_action.triggered.connect(self.request_deletion)
        menu.addAction(delete_action)
        
        properties_action = QAction("Properties...", menu)
        properties_action.triggered.connect(self.show_properties)
        menu.addAction(properties_action)
        
        # Show menu at cursor position
        menu.exec_(event.screenPos())
        
    def request_deletion(self):
        """Request deletion of this connection."""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            None, "Delete Connection",
            "Are you sure you want to delete this connection?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.disconnect()
            
    def show_properties(self):
        """Show properties dialog for this connection."""
        from PyQt5.QtWidgets import QMessageBox
        
        info = f"Connection Properties:\n\n"
        info += f"ID: {self.id}\n"
        if self.start_port:
            info += f"From: {self.start_port.node.name} ({self.start_port.id})\n"
        if self.end_port:
            info += f"To: {self.end_port.node.name} ({self.end_port.id})\n"
        info += f"Style: {self.style.value}\n"
        info += f"Valid: {self.is_valid}\n"
        
        QMessageBox.information(None, "Connection Properties", info)
        
    def serialize(self) -> Dict[str, Any]:
        """Enhanced serialization with style and metadata."""
        data = super().serialize()
        data.update({
            'style': self.style.value,
            'line_width': self.line_width,
            'colors': {
                state.value: color.name() 
                for state, color in self.colors.items()
            }
        })
        return data


class ConnectionManager(QObject):
    """
    Manages connections within a scene.
    
    Handles creation, validation, and lifecycle management of connections.
    """
    
    # Signals
    connection_created = pyqtSignal(Connection)
    connection_deleted = pyqtSignal(Connection)
    connection_validated = pyqtSignal(Connection, bool)
    
    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene
        self.connections: Set[Connection] = set()
        self.active_connection: Optional[Connection] = None
        
        # Global validation rules
        self.validation_rules: List[Callable] = []
        
        # Style settings
        self.default_style = ConnectionStyle.BEZIER
        self.allow_multiple_connections = True
        self.allow_self_connections = False
        
    def add_validation_rule(self, rule: Callable[[Connection], bool]):
        """Add a global validation rule for all connections."""
        self.validation_rules.append(rule)
        
        # Apply to existing connections
        for conn in self.connections:
            conn.validation_handlers.append(rule)
            conn.validate()
            
    def start_connection(self, start_port: ConnectionPort, pos: QPointF) -> Connection:
        """Start creating a new connection."""
        if self.active_connection:
            # Cancel previous connection
            self.cancel_connection()
            
        self.active_connection = Connection(
            start_port, pos, self.scene, 
            style=self.default_style
        )
        
        # Add validation rules
        for rule in self.validation_rules:
            self.active_connection.validation_handlers.append(rule)
            
        return self.active_connection
        
    def update_connection(self, pos: QPointF):
        """Update the active connection endpoint."""
        if self.active_connection:
            self.active_connection.end_pos = pos
            self.active_connection.updatePath()
            
    def complete_connection(self, end_port: ConnectionPort) -> Optional[Connection]:
        """Complete the active connection to an end port."""
        if not self.active_connection:
            return None
            
        # Validate connection
        if not self.can_connect(self.active_connection.start_port, end_port):
            self.cancel_connection()
            return None
            
        # Set end port
        self.active_connection.setEndPoint(end_port)
        
        # Register connection
        connection = self.active_connection
        self.connections.add(connection)
        self.active_connection = None
        
        # Notify listeners
        self.connection_created.emit(connection)
        
        return connection
        
    def cancel_connection(self):
        """Cancel the active connection."""
        if self.active_connection:
            self.active_connection.disconnect()
            self.active_connection = None
            
    def can_connect(self, start_port: ConnectionPort, end_port: ConnectionPort) -> bool:
        """Check if two ports can be connected."""
        # Basic port compatibility
        if not start_port.can_connect_to(end_port):
            return False
            
        # Self-connection check
        if not self.allow_self_connections and start_port.node == end_port.node:
            return False
            
        # Multiple connections check
        if not self.allow_multiple_connections:
            if start_port.connections or end_port.connections:
                return False
                
        # Apply validation rules
        temp_connection = Connection(start_port, end_port.position)
        temp_connection.setEndPoint(end_port)
        
        for rule in self.validation_rules:
            try:
                if not rule(temp_connection):
                    return False
            except Exception as e:
                print(f"Error in validation rule: {e}")
                return False
                
        return True
        
    def remove_connection(self, connection: Connection):
        """Remove a connection."""
        if connection in self.connections:
            self.connections.remove(connection)
            connection.disconnect()
            self.connection_deleted.emit(connection)
            
    def get_connections_for_node(self, node) -> List[Connection]:
        """Get all connections for a specific node."""
        connections = []
        for conn in self.connections:
            if (conn.start_port.node == node or 
                (conn.end_port and conn.end_port.node == node)):
                connections.append(conn)
        return connections
        
    def get_connections_for_port(self, port: ConnectionPort) -> List[Connection]:
        """Get all connections for a specific port."""
        return list(port.connections)
        
    def clear_all_connections(self):
        """Remove all connections."""
        for connection in list(self.connections):
            self.remove_connection(connection)
            
    def validate_all_connections(self):
        """Validate all existing connections."""
        for connection in self.connections:
            was_valid = connection.is_valid
            is_valid = connection.validate()
            
            if was_valid != is_valid:
                self.connection_validated.emit(connection, is_valid)
                
    def set_connection_style(self, style: ConnectionStyle):
        """Set the default style for new connections."""
        self.default_style = style
        
    def apply_style_to_all(self, style: ConnectionStyle):
        """Apply a style to all existing connections."""
        for connection in self.connections:
            connection.style = style
            connection.updatePath()
