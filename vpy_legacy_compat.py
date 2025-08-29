"""
Backward compatibility layer for VysualPy refactored architecture.

This module provides compatibility wrappers and import paths for existing code
that relies on the old node and connection classes.
"""

import warnings
from typing import Any, Dict, Optional

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtWidgets import QGraphicsScene

# Import new architecture components
from vpy_node_base import BaseNode, NodeType, NodeState
from vpy_node_types import BlueprintNode, ExecutionNode, BuildableNode, CommentNode
from vpy_connection_core import Connection, ConnectionManager


def _deprecated_warning(old_name: str, new_name: str, version: str = "2.0"):
    """Generate a deprecation warning."""
    warnings.warn(
        f"{old_name} is deprecated and will be removed in version {version}. "
        f"Use {new_name} instead.",
        DeprecationWarning,
        stacklevel=3
    )


class DraggableRect(BlueprintNode):
    """
    Backward compatibility wrapper for DraggableRect.
    
    This class provides the same interface as the original DraggableRect
    but uses the new BlueprintNode implementation internally.
    """
    
    def __init__(self, name, content, x, y, width, scene, is_class=False):
        _deprecated_warning("DraggableRect", "BlueprintNode")
        
        # Convert old parameters to new format
        position = QPointF(x, y) if x is not None and y is not None else None
        size = QRectF(0, 0, width, 200) if width else None
        
        super().__init__(
            name=name,
            content=content,
            position=position,
            size=size
        )
        
        self.is_class = is_class
        self.scene_ref = scene  # Keep reference for compatibility
        
        # Add to scene if provided
        if scene:
            scene.addItem(self)
    
    @property
    def full_content(self):
        """Compatibility property."""
        return self.content
    
    @full_content.setter
    def full_content(self, value):
        """Compatibility property setter."""
        self.content = value
        
    def snapToGrid(self, value):
        """Compatibility method - now handled by BaseNode."""
        return super().snapToGrid(value)


class ExecutionDraggableRect(ExecutionNode):
    """
    Backward compatibility wrapper for ExecutionDraggableRect.
    """
    
    def __init__(self, name, content, x, y, width, height, scene, is_class=False):
        _deprecated_warning("ExecutionDraggableRect", "ExecutionNode")
        
        position = QPointF(x, y) if x is not None and y is not None else None
        size = QRectF(0, 0, width, height) if width and height else None
        
        super().__init__(
            name=name,
            position=position,
            size=size
        )
        
        self.content = content
        self.full_content = content
        self.is_class = is_class
        self.scene_ref = scene
        
        if scene:
            scene.addItem(self)
    
    @property
    def full_content(self):
        return self.content
    
    @full_content.setter  
    def full_content(self, value):
        self.content = value


# Legacy connection compatibility
class LegacyConnection:
    """
    Compatibility wrapper for the old Connection class.
    
    Maps old connection interface to new Connection system.
    """
    
    def __init__(self, start_point, end_pos, scene):
        _deprecated_warning("Connection (old)", "vpy_connection_core.Connection")
        
        # Create new connection
        if hasattr(start_point, 'parentItem'):
            # Convert old ConnectionPoint to new system
            start_node = start_point.parentItem()
            if hasattr(start_node, 'output_ports') and start_node.output_ports:
                start_port = list(start_node.output_ports.values())[0]
            else:
                # Create a default output port
                start_port = start_node.add_output_port("output", "any", "Output")
        else:
            start_port = start_point
            
        self._connection = Connection(start_port, end_pos, scene)
        
    def setEndPoint(self, end_point):
        """Compatibility method."""
        if hasattr(end_point, 'parentItem'):
            # Convert old ConnectionPoint to new system  
            end_node = end_point.parentItem()
            if hasattr(end_node, 'input_ports') and end_node.input_ports:
                end_port = list(end_node.input_ports.values())[0]
            else:
                # Create a default input port
                end_port = end_node.add_input_port("input", "any", "Input")
        else:
            end_port = end_point
            
        self._connection.setEndPoint(end_port)
        
    def updatePath(self):
        """Compatibility method."""
        self._connection.updatePath()
        
    def __getattr__(self, name):
        """Delegate unknown attributes to the new connection."""
        return getattr(self._connection, name)


class CommentBox(CommentNode):
    """
    Backward compatibility wrapper for CommentBox.
    """
    
    def __init__(self, name, x, y, width=300, height=200):
        _deprecated_warning("CommentBox", "CommentNode")
        
        position = QPointF(x, y)
        size = QRectF(0, 0, width, height)
        
        super().__init__(
            name=name,
            content="",
            position=position,
            size=size
        )


# Connection point compatibility - map to port system
class ConnectionPoint:
    """
    Compatibility wrapper for ConnectionPoint.
    
    Maps to the new port system while maintaining old interface.
    """
    
    def __init__(self, x, y, is_output, parent_item):
        _deprecated_warning("ConnectionPoint", "ConnectionPort")
        
        self.x = x
        self.y = y
        self.is_output = is_output
        self.parent_item = parent_item
        self.connection = None
        
        # Try to map to new port system
        if hasattr(parent_item, 'add_output_port') and is_output:
            self._port = parent_item.add_output_port("output", "any", "Output")
        elif hasattr(parent_item, 'add_input_port') and not is_output:
            self._port = parent_item.add_input_port("input", "any", "Input")
        else:
            self._port = None
            
    def parentItem(self):
        """Compatibility method."""
        return self.parent_item
        
    @property
    def connections(self):
        """Compatibility property."""
        if self._port:
            return list(self._port.connections)
        return []


# Scene-level compatibility functions
def create_legacy_node(node_type: str, *args, **kwargs):
    """Factory function for creating nodes with legacy interface."""
    
    if node_type == "DraggableRect":
        return DraggableRect(*args, **kwargs)
    elif node_type == "ExecutionDraggableRect":
        return ExecutionDraggableRect(*args, **kwargs)
    elif node_type == "BuildableNode":
        # BuildableNode already exists in new system
        return BuildableNode(*args, **kwargs)
    elif node_type == "CommentBox":
        return CommentBox(*args, **kwargs)
    else:
        raise ValueError(f"Unknown legacy node type: {node_type}")


# Import compatibility - allows old import statements to work
def setup_legacy_imports():
    """
    Set up legacy import paths for backward compatibility.
    
    This allows existing code to continue using old import statements.
    """
    import sys
    
    # Create a compatibility module for vpy_graph
    class LegacyGraphModule:
        def __getattr__(self, name):
            if name == "DraggableRect":
                return DraggableRect
            elif name == "ExecutionDraggableRect":
                return ExecutionDraggableRect
            elif name == "CommentBox":
                return CommentBox
            elif name == "BuildableNode":
                return BuildableNode
            else:
                raise AttributeError(f"Module 'vpy_graph' has no attribute '{name}'")
    
    # Install the compatibility module
    sys.modules['vpy_graph_legacy'] = LegacyGraphModule()
    
    # Create compatibility for vpy_connection  
    class LegacyConnectionModule:
        def __getattr__(self, name):
            if name == "Connection":
                return LegacyConnection
            elif name == "ConnectionPoint":
                return ConnectionPoint
            else:
                raise AttributeError(f"Module 'vpy_connection' has no attribute '{name}'")
    
    sys.modules['vpy_connection_legacy'] = LegacyConnectionModule()


# Utility functions for migration
def migrate_workspace_data(old_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate old workspace data format to new format.
    
    Converts serialized data from old node format to new node format.
    """
    new_data = old_data.copy()
    
    # Migrate node data
    if 'boxes' in old_data:
        new_boxes = []
        for box in old_data['boxes']:
            new_box = box.copy()
            
            # Map old node types to new types
            if box.get('type') == 'draggable_rect':
                new_box['type'] = NodeType.BLUEPRINT.value
            elif box.get('type') == 'execution_draggable_rect':
                new_box['type'] = NodeType.EXECUTION.value
            elif box.get('type') == 'buildable_node':
                new_box['type'] = NodeType.BUILDABLE.value
                
            # Add default ports if missing
            if 'input_ports' not in new_box:
                new_box['input_ports'] = {
                    'input': {'data_type': 'any', 'label': 'Input'}
                }
            if 'output_ports' not in new_box:
                new_box['output_ports'] = {
                    'output': {'data_type': 'any', 'label': 'Output'}
                }
                
            new_boxes.append(new_box)
            
        new_data['boxes'] = new_boxes
        
    return new_data


def check_compatibility() -> Dict[str, bool]:
    """
    Check compatibility with existing codebase.
    
    Returns a dictionary of compatibility checks and their status.
    """
    checks = {}
    
    try:
        # Test node creation
        node = DraggableRect("Test", "test content", 0, 0, 200, None)
        checks['DraggableRect_creation'] = True
    except Exception as e:
        checks['DraggableRect_creation'] = False
        
    try:
        # Test execution node creation
        exec_node = ExecutionDraggableRect("Test", "test", 0, 0, 200, 200, None)
        checks['ExecutionDraggableRect_creation'] = True
    except Exception as e:
        checks['ExecutionDraggableRect_creation'] = False
        
    try:
        # Test comment box creation
        comment = CommentBox("Test", 0, 0)
        checks['CommentBox_creation'] = True
    except Exception as e:
        checks['CommentBox_creation'] = False
        
    # Test new architecture
    try:
        blueprint = BlueprintNode("Test")
        execution = ExecutionNode("Test")
        buildable = BuildableNode("Test")
        checks['new_architecture'] = True
    except Exception as e:
        checks['new_architecture'] = False
        
    return checks


# Initialize legacy compatibility when module is imported
setup_legacy_imports()
