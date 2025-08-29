"""
Base node system for VysualPy graph architecture.

This module provides the foundation for a unified node system that eliminates
code duplication and provides clear interfaces for different node types.
"""

from abc import ABCMeta, abstractmethod
from typing import Dict, List, Any, Optional, Set, Union, Callable
from enum import Enum
import uuid
import json

from PyQt5.QtCore import QPointF, QRectF, QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtGui import QPainter


class QGraphicsABCMeta(type(QGraphicsRectItem), ABCMeta):
    """Custom metaclass to resolve conflict between QGraphicsRectItem and ABC."""
    pass


class NodeType(Enum):
    """Enumeration of available node types."""
    BLUEPRINT = "blueprint"
    EXECUTION = "execution"
    BUILDABLE = "buildable"
    COMMENT = "comment"


class PortType(Enum):
    """Enumeration of port types for connections."""
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"


class ConnectionPort:
    """Represents a connection port on a node."""
    
    def __init__(self, 
                 port_id: str,
                 port_type: PortType,
                 node: 'BaseNode',
                 position: QPointF = None,
                 data_type: str = "any",
                 label: str = ""):
        self.id = port_id
        self.type = port_type
        self.node = node
        self.position = position or QPointF(0, 0)
        self.data_type = data_type
        self.label = label
        self.connections: Set['BaseConnection'] = set()
        
    def can_connect_to(self, other_port: 'ConnectionPort') -> bool:
        """Check if this port can connect to another port."""
        # Basic validation rules
        if other_port.node == self.node:
            return False  # No self-connections
            
        if self.type == PortType.OUTPUT and other_port.type == PortType.INPUT:
            return True
        if self.type == PortType.INPUT and other_port.type == PortType.OUTPUT:
            return True
        if self.type == PortType.BIDIRECTIONAL or other_port.type == PortType.BIDIRECTIONAL:
            return True
            
        return False
        
    def add_connection(self, connection: 'BaseConnection'):
        """Add a connection to this port."""
        self.connections.add(connection)
        
    def remove_connection(self, connection: 'BaseConnection'):
        """Remove a connection from this port."""
        self.connections.discard(connection)


class BaseConnection:
    """Base class for connections between nodes."""
    
    def __init__(self, 
                 start_port: ConnectionPort,
                 end_port: ConnectionPort,
                 connection_id: str = None):
        self.id = connection_id or str(uuid.uuid4())
        self.start_port = start_port
        self.end_port = end_port
        self.metadata: Dict[str, Any] = {}
        
        # Register with ports
        start_port.add_connection(self)
        end_port.add_connection(self)
        
    def disconnect(self):
        """Remove this connection."""
        self.start_port.remove_connection(self)
        self.end_port.remove_connection(self)
        
    def serialize(self) -> Dict[str, Any]:
        """Serialize connection to dictionary."""
        return {
            'id': self.id,
            'start_node': self.start_port.node.id,
            'start_port': self.start_port.id,
            'end_node': self.end_port.node.id,
            'end_port': self.end_port.id,
            'metadata': self.metadata
        }


class NodeState(Enum):
    """Enumeration of node states."""
    NORMAL = "normal"
    SELECTED = "selected"
    HIGHLIGHTED = "highlighted"
    EDITING = "editing"
    ERROR = "error"
    DISABLED = "disabled"


class BaseNode(QGraphicsRectItem, metaclass=QGraphicsABCMeta):
    """
    Abstract base class for all node types in the VysualPy system.
    
    This class defines the common interface and functionality that all nodes
    must implement, promoting code reuse and consistent behavior.
    """
    
    def __init__(self, 
                 node_id: str = None,
                 name: str = "Node",
                 position: QPointF = None,
                 size: QRectF = None):
        super().__init__()
        
        # Core properties
        self.id = node_id or str(uuid.uuid4())
        self.name = name
        self.node_type = NodeType.BLUEPRINT  # Override in subclasses
        self.state = NodeState.NORMAL
        
        # Position and size
        if position:
            self.setPos(position)
        self.size = size or QRectF(0, 0, 200, 100)
        self.setRect(self.size)
        
        # Ports and connections
        self.input_ports: Dict[str, ConnectionPort] = {}
        self.output_ports: Dict[str, ConnectionPort] = {}
        
        # Metadata and content
        self.metadata: Dict[str, Any] = {}
        self.content: str = ""
        
        # Event hooks (can be set by external systems)
        self.on_connect_hooks: List[Callable] = []
        self.on_disconnect_hooks: List[Callable] = []
        self.on_update_hooks: List[Callable] = []
        self.on_state_change_hooks: List[Callable] = []
        
        # Grid snapping
        self.grid_size = 50
        self.snap_to_grid = True
        
        # Visual properties (to be handled by mixins)
        self.border_width = 2
        self.corner_radius = 5
        
        # Make item selectable and movable
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        
    def add_input_port(self, port_id: str, data_type: str = "any", label: str = "") -> ConnectionPort:
        """Add an input port to this node."""
        port = ConnectionPort(port_id, PortType.INPUT, self, data_type=data_type, label=label)
        self.input_ports[port_id] = port
        self._update_port_positions()
        return port
        
    def add_output_port(self, port_id: str, data_type: str = "any", label: str = "") -> ConnectionPort:
        """Add an output port to this node."""
        port = ConnectionPort(port_id, PortType.OUTPUT, self, data_type=data_type, label=label)
        self.output_ports[port_id] = port
        self._update_port_positions()
        return port
        
    def remove_port(self, port_id: str):
        """Remove a port from this node."""
        # Remove from input ports
        if port_id in self.input_ports:
            port = self.input_ports[port_id]
            # Disconnect all connections
            for connection in list(port.connections):
                connection.disconnect()
            del self.input_ports[port_id]
            
        # Remove from output ports
        if port_id in self.output_ports:
            port = self.output_ports[port_id]
            # Disconnect all connections
            for connection in list(port.connections):
                connection.disconnect()
            del self.output_ports[port_id]
            
        self._update_port_positions()
        
    def _update_port_positions(self):
        """Update the positions of all ports based on node geometry."""
        rect = self.rect()
        
        # Position input ports on the left side
        if self.input_ports:
            port_height = rect.height() / (len(self.input_ports) + 1)
            for i, port in enumerate(self.input_ports.values()):
                port.position = QPointF(rect.left(), rect.top() + port_height * (i + 1))
                
        # Position output ports on the right side
        if self.output_ports:
            port_height = rect.height() / (len(self.output_ports) + 1)
            for i, port in enumerate(self.output_ports.values()):
                port.position = QPointF(rect.right(), rect.top() + port_height * (i + 1))
                
    def get_all_connections(self) -> List[BaseConnection]:
        """Get all connections from this node."""
        connections = []
        for port in list(self.input_ports.values()) + list(self.output_ports.values()):
            connections.extend(port.connections)
        return list(set(connections))  # Remove duplicates
        
    def disconnect_all(self):
        """Disconnect all connections from this node."""
        for connection in list(self.get_all_connections()):
            connection.disconnect()
            
    def set_state(self, new_state: NodeState):
        """Change the node's state and trigger callbacks."""
        old_state = self.state
        self.state = new_state
        
        # Trigger state change hooks
        for hook in self.on_state_change_hooks:
            try:
                hook(self, old_state, new_state)
            except Exception as e:
                print(f"Error in state change hook: {e}")
                
        # Update visual representation
        self.update()
        
    def snapToGrid(self, value: float) -> float:
        """Snap a value to the grid if snapping is enabled."""
        if self.snap_to_grid and self.grid_size > 0:
            return round(value / self.grid_size) * self.grid_size
        return value
        
    def setPos(self, *args):
        """Override setPos to support grid snapping."""
        if len(args) == 1:
            pos = args[0]
            snapped_pos = QPointF(
                self.snapToGrid(pos.x()),
                self.snapToGrid(pos.y())
            )
            super().setPos(snapped_pos)
        else:
            x, y = args
            super().setPos(
                self.snapToGrid(x),
                self.snapToGrid(y)
            )
            
    def serialize(self) -> Dict[str, Any]:
        """Serialize node to dictionary for saving."""
        pos = self.pos()
        rect = self.rect()
        
        return {
            'id': self.id,
            'name': self.name,
            'type': self.node_type.value,
            'position': {'x': pos.x(), 'y': pos.y()},
            'size': {
                'x': rect.x(), 'y': rect.y(),
                'width': rect.width(), 'height': rect.height()
            },
            'content': self.content,
            'metadata': self.metadata,
            'state': self.state.value,
            'input_ports': {
                port_id: {
                    'data_type': port.data_type,
                    'label': port.label
                }
                for port_id, port in self.input_ports.items()
            },
            'output_ports': {
                port_id: {
                    'data_type': port.data_type,
                    'label': port.label
                }
                for port_id, port in self.output_ports.items()
            }
        }
        
    def deserialize(self, data: Dict[str, Any]):
        """Deserialize node from dictionary."""
        self.id = data.get('id', self.id)
        self.name = data.get('name', self.name)
        self.content = data.get('content', '')
        self.metadata = data.get('metadata', {})
        
        # Restore position
        if 'position' in data:
            pos_data = data['position']
            self.setPos(pos_data['x'], pos_data['y'])
            
        # Restore size
        if 'size' in data:
            size_data = data['size']
            self.size = QRectF(
                size_data['x'], size_data['y'],
                size_data['width'], size_data['height']
            )
            self.setRect(self.size)
            
        # Restore state
        if 'state' in data:
            try:
                self.state = NodeState(data['state'])
            except ValueError:
                self.state = NodeState.NORMAL
                
        # Restore ports (connections will be restored separately)
        if 'input_ports' in data:
            for port_id, port_data in data['input_ports'].items():
                self.add_input_port(
                    port_id,
                    port_data.get('data_type', 'any'),
                    port_data.get('label', '')
                )
                
        if 'output_ports' in data:
            for port_id, port_data in data['output_ports'].items():
                self.add_output_port(
                    port_id,
                    port_data.get('data_type', 'any'),
                    port_data.get('label', '')
                )
                
    def validate(self) -> List[str]:
        """Validate the node and return any error messages."""
        errors = []
        
        # Basic validation
        if not self.name.strip():
            errors.append("Node name cannot be empty")
            
        if self.size.width() <= 0 or self.size.height() <= 0:
            errors.append("Node size must be positive")
            
        return errors
        
    # Event hooks
    def on_connect(self, connection: BaseConnection):
        """Called when a connection is made to this node."""
        for hook in self.on_connect_hooks:
            try:
                hook(self, connection)
            except Exception as e:
                print(f"Error in connect hook: {e}")
                
    def on_disconnect(self, connection: BaseConnection):
        """Called when a connection is removed from this node."""
        for hook in self.on_disconnect_hooks:
            try:
                hook(self, connection)
            except Exception as e:
                print(f"Error in disconnect hook: {e}")
                
    def on_update(self):
        """Called when the node content or state changes."""
        for hook in self.on_update_hooks:
            try:
                hook(self)
            except Exception as e:
                print(f"Error in update hook: {e}")
                
    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def get_display_name(self) -> str:
        """Get the name to display on the node."""
        pass
        
    @abstractmethod
    def get_tooltip_text(self) -> str:
        """Get the tooltip text for this node."""
        pass
        
    @abstractmethod
    def can_accept_content(self, content: str) -> bool:
        """Check if this node can accept the given content."""
        pass
        
    @abstractmethod
    def process_content_change(self, old_content: str, new_content: str):
        """Process a change in node content."""
        pass

    # Default implementations for QGraphicsRectItem methods
    # (These will be enhanced by mixins)
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the node."""
        return self.size.adjusted(-self.border_width, -self.border_width, 
                                  self.border_width, self.border_width)
        
    def paint(self, painter: QPainter, option, widget=None):
        """Basic paint implementation - can be enhanced by mixins."""
        # Check if a mixin has overridden the paint method
        if hasattr(super(), 'paint') and hasattr(self, 'get_node_color'):
            # Call the mixin's enhanced paint method
            super().paint(painter, option, widget)
        else:
            # Fallback to basic rendering
            from PyQt5.QtGui import QPen, QBrush, QColor
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            painter.drawRect(self.rect())
            
            # Draw basic title
            if hasattr(self, 'name'):
                painter.setPen(QPen(QColor(255, 255, 255)))
                title_rect = self.rect().adjusted(5, 5, -5, -5)
                painter.drawText(title_rect, 0, self.name)


class NodeRegistry:
    """Registry for node types and factory methods."""
    
    def __init__(self):
        self._node_classes: Dict[NodeType, type] = {}
        self._factory_functions: Dict[NodeType, Callable] = {}
        
    def register_node_class(self, node_type: NodeType, node_class: type):
        """Register a node class for a given type."""
        self._node_classes[node_type] = node_class
        
    def register_factory_function(self, node_type: NodeType, factory_func: Callable):
        """Register a factory function for a given type."""
        self._factory_functions[node_type] = factory_func
        
    def create_node(self, node_type: NodeType, **kwargs) -> BaseNode:
        """Create a node of the specified type."""
        if node_type in self._factory_functions:
            return self._factory_functions[node_type](**kwargs)
        elif node_type in self._node_classes:
            return self._node_classes[node_type](**kwargs)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
            
    def get_available_types(self) -> List[NodeType]:
        """Get a list of all available node types."""
        return list(set(self._node_classes.keys()) | set(self._factory_functions.keys()))


# Global node registry instance
node_registry = NodeRegistry()
