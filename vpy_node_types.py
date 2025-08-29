"""
Concrete implementations of different node types for VysualPy.

These classes combine the BaseNode with appropriate mixins to create
specialized node types for different use cases.
"""

import ast
import re
from typing import Dict, List, Any, Optional

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QColor

from vpy_node_base import BaseNode, NodeType, NodeState, node_registry
from vpy_node_mixins import RenderMixin, InteractionMixin, EditableMixin


class BlueprintNode(BaseNode, RenderMixin, InteractionMixin):
    """
    Node type for blueprint/structural visualization.
    
    Shows code structure, classes, and functions with their relationships.
    """
    
    def __init__(self, name: str = "Blueprint Node", content: str = "", **kwargs):
        super().__init__(name=name, **kwargs)
        self.node_type = NodeType.BLUEPRINT
        self.content = content
        self.is_class = False
        self.full_content = content
        
        # Add default ports
        self.add_input_port("input", "code", "Input")
        self.add_output_port("output", "code", "Output")
        
        # Analyze content on creation
        if content.strip():
            self.analyze_content()
            
    def analyze_content(self):
        """Analyze the content to determine if it's a class or function."""
        content = self.content.strip()
        
        if content.startswith('class '):
            self.is_class = True
            # Extract class name
            try:
                first_line = content.split('\n')[0]
                class_name = first_line.split()[1].split('(')[0].split(':')[0]
                self.name = class_name
            except (IndexError, AttributeError):
                self.name = "Class"
                
        elif content.startswith(('def ', 'async def ')):
            self.is_class = False
            # Extract function name
            try:
                first_line = content.split('\n')[0]
                if content.startswith('async def '):
                    func_name = first_line.split()[2].split('(')[0]
                else:
                    func_name = first_line.split()[1].split('(')[0]
                self.name = func_name
            except (IndexError, AttributeError):
                self.name = "Function"
        else:
            self.is_class = False
            self.name = "Code Block"
            
    def get_display_name(self) -> str:
        """Get the display name for this node."""
        if self.is_class:
            return f"📦 {self.name}"
        elif self.content.strip().startswith(('def ', 'async def ')):
            return f"⚙️ {self.name}"
        else:
            return f"📄 {self.name}"
            
    def get_tooltip_text(self) -> str:
        """Get tooltip text for this node."""
        content_preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"{self.name}\n\n{content_preview}"
        
    def can_accept_content(self, content: str) -> bool:
        """Check if this node can accept the given content."""
        # Blueprint nodes can accept any Python code
        return True
        
    def process_content_change(self, old_content: str, new_content: str):
        """Process a change in node content."""
        self.content = new_content
        self.full_content = new_content
        self.analyze_content()
        
        # Update visual representation
        self.update()


class ExecutionNode(BaseNode, RenderMixin, InteractionMixin):
    """
    Node type for execution flow visualization.
    
    Shows runtime execution paths and call flows between functions.
    """
    
    def __init__(self, name: str = "Execution Node", original_name: str = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.node_type = NodeType.EXECUTION
        self.original_name = original_name or name
        self.execution_metadata = {}
        self.is_conditional = False
        self.has_return = False
        
        # Add default ports for execution flow
        self.add_input_port("exec_in", "execution", "In")
        self.add_output_port("exec_out", "execution", "Out")
        
        # Set execution-specific visual properties
        self.background_color = QColor(154, 205, 50)  # Yellow green
        
    def set_conditional(self, is_conditional: bool):
        """Mark this node as part of conditional execution."""
        self.is_conditional = is_conditional
        if is_conditional:
            self.background_color = QColor(255, 165, 0)  # Orange for conditional
        else:
            self.background_color = QColor(154, 205, 50)  # Green for normal
        self.update()
        
    def set_has_return(self, has_return: bool):
        """Mark this node as having return values."""
        self.has_return = has_return
        if has_return:
            # Add return port if not present
            if "return" not in self.output_ports:
                self.add_output_port("return", "value", "Return")
        else:
            # Remove return port if present
            if "return" in self.output_ports:
                self.remove_port("return")
        self.update()
        
    def get_display_name(self) -> str:
        """Get the display name for this node."""
        prefix = "🔄" if self.is_conditional else "⚡"
        return f"{prefix} {self.name}"
        
    def get_tooltip_text(self) -> str:
        """Get tooltip text for this node."""
        tooltip = f"Function: {self.name}"
        if self.original_name != self.name:
            tooltip += f"\nOriginal: {self.original_name}"
        if self.is_conditional:
            tooltip += "\nConditional execution"
        if self.has_return:
            tooltip += "\nHas return value"
        return tooltip
        
    def can_accept_content(self, content: str) -> bool:
        """Execution nodes don't accept direct content editing."""
        return False
        
    def process_content_change(self, old_content: str, new_content: str):
        """Execution nodes don't support content changes."""
        pass


class BuildableNode(BaseNode, RenderMixin, InteractionMixin, EditableMixin):
    """
    Node type for live code editing/building.
    
    Supports in-place editing and automatically creates connections to
    undefined functions.
    """
    
    def __init__(self, name: str = "Buildable Node", content: str = "", 
                 parent_ide=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.node_type = NodeType.BUILDABLE
        self.content = content
        self.full_content = content
        self.parent_ide = parent_ide  # Reference to main IDE for live sync
        self.is_class = False
        self.function_calls = []
        
        # Add default ports
        self.add_input_port("input", "code", "Input")
        self.add_output_port("output", "code", "Output")
        
        # Set buildable-specific visual properties
        self.background_color = QColor(255, 140, 0)  # Dark orange
        
        # Analyze content on creation
        if content.strip():
            self.analyze_and_update()
            
    def analyze_and_update(self):
        """Analyze content and update node properties."""
        self.analyze_content()
        self.detect_function_calls()
        
    def analyze_content(self):
        """Analyze the content to determine its type and extract metadata."""
        content = self.content.strip()
        
        if not content:
            self.name = "Empty Node"
            self.is_class = False
            return
            
        if content.startswith('class '):
            self.is_class = True
            try:
                first_line = content.split('\n')[0]
                class_name = first_line.split()[1].split('(')[0].split(':')[0]
                self.name = class_name
            except (IndexError, AttributeError):
                self.name = "Class"
                
        elif content.startswith(('def ', 'async def ')):
            self.is_class = False
            try:
                first_line = content.split('\n')[0]
                if content.startswith('async def '):
                    func_name = first_line.split()[2].split('(')[0]
                else:
                    func_name = first_line.split()[1].split('(')[0]
                self.name = func_name
            except (IndexError, AttributeError):
                self.name = "Function"
        else:
            self.is_class = False
            # Try to infer name from content
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            if lines:
                # Use first significant line as name hint
                first_line = lines[0][:30]
                self.name = f"Code: {first_line}"
            else:
                self.name = "Code Block"
                
    def detect_function_calls(self):
        """Detect function calls in the content."""
        # Import here to avoid circular imports
        from vpy_blueprints import detect_function_calls
        
        try:
            self.function_calls = detect_function_calls(self.content)
        except Exception as e:
            print(f"Error detecting function calls: {e}")
            self.function_calls = []
            
    def get_display_name(self) -> str:
        """Get the display name for this node."""
        if self.editing:
            return f"✏️ {self.name}"
        elif self.is_class:
            return f"🏗️ {self.name}"
        elif self.content.strip().startswith(('def ', 'async def ')):
            return f"🔧 {self.name}"
        else:
            return f"📝 {self.name}"
            
    def get_tooltip_text(self) -> str:
        """Get tooltip text for this node."""
        tooltip = f"{self.name}"
        if self.function_calls:
            tooltip += f"\nCalls: {', '.join(self.function_calls[:3])}"
            if len(self.function_calls) > 3:
                tooltip += "..."
        if self.editing:
            tooltip += "\nPress Ctrl+Enter to save"
            tooltip += "\nPress Escape to cancel"
        return tooltip
        
    def can_accept_content(self, content: str) -> bool:
        """Check if this node can accept the given content."""
        # Try to parse as Python code
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            # Allow partial/invalid syntax during editing
            return True
            
    def process_content_change(self, old_content: str, new_content: str):
        """Process a change in node content."""
        self.content = new_content
        self.full_content = new_content
        
        # Re-analyze content
        self.analyze_and_update()
        
        # Sync with IDE if available
        if self.parent_ide and hasattr(self.scene(), 'check_and_create_called_functions'):
            self.scene().check_and_create_called_functions(self)
            
    def startEditing(self):
        """Override to set up BuildableNode-specific editing."""
        super().startEditing()
        
        # Additional setup for buildable nodes
        if self.text_item:
            # Set initial cursor position at end
            cursor = self.text_item.textCursor()
            cursor.movePosition(cursor.End)
            self.text_item.setTextCursor(cursor)


class CommentNode(BaseNode, RenderMixin, InteractionMixin, EditableMixin):
    """
    Node type for comments and annotations.
    
    Provides documentation and grouping functionality in graphs.
    """
    
    def __init__(self, name: str = "Comment", content: str = "", **kwargs):
        super().__init__(name=name, **kwargs)
        self.node_type = NodeType.COMMENT
        self.content = content
        
        # Comments don't have ports by default
        # Set comment-specific visual properties
        self.background_color = QColor(128, 128, 128, 180)  # Semi-transparent gray
        self.border_color = QColor(160, 160, 160)
        
        # Comments are larger by default
        self.size = QRectF(0, 0, 300, 200)
        self.setRect(self.size)
        
    def get_display_name(self) -> str:
        """Get the display name for this node."""
        return f"💬 {self.name}"
        
    def get_tooltip_text(self) -> str:
        """Get tooltip text for this node."""
        content_preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"Comment: {self.name}\n\n{content_preview}"
        
    def can_accept_content(self, content: str) -> bool:
        """Comments can accept any text content."""
        return True
        
    def process_content_change(self, old_content: str, new_content: str):
        """Process a change in comment content."""
        self.content = new_content
        
        # Auto-resize based on content
        if self.text_item:
            text_rect = self.text_item.boundingRect()
            min_width = max(300, text_rect.width() + 20)
            min_height = max(100, text_rect.height() + 50)
            
            current_rect = self.rect()
            if (current_rect.width() < min_width or 
                current_rect.height() < min_height):
                new_rect = QRectF(
                    current_rect.x(), current_rect.y(),
                    min_width, min_height
                )
                self.setRect(new_rect)
                self.size = new_rect


# Register node types with the global registry
def register_node_types():
    """Register all node types with the global registry."""
    node_registry.register_node_class(NodeType.BLUEPRINT, BlueprintNode)
    node_registry.register_node_class(NodeType.EXECUTION, ExecutionNode)  
    node_registry.register_node_class(NodeType.BUILDABLE, BuildableNode)
    node_registry.register_node_class(NodeType.COMMENT, CommentNode)
    
    # Register factory functions for backward compatibility
    def create_draggable_rect(*args, **kwargs):
        """Factory function for backward compatibility with DraggableRect."""
        import warnings
        warnings.warn(
            "DraggableRect is deprecated. Use BlueprintNode instead.",
            DeprecationWarning, stacklevel=2
        )
        return BlueprintNode(*args, **kwargs)
        
    def create_execution_draggable_rect(*args, **kwargs):
        """Factory function for backward compatibility with ExecutionDraggableRect."""
        import warnings
        warnings.warn(
            "ExecutionDraggableRect is deprecated. Use ExecutionNode instead.",
            DeprecationWarning, stacklevel=2
        )
        return ExecutionNode(*args, **kwargs)
        
    # These will be accessible via the registry for backward compatibility
    node_registry.register_factory_function("draggable_rect", create_draggable_rect)
    node_registry.register_factory_function("execution_draggable_rect", create_execution_draggable_rect)


# Initialize node type registration
register_node_types()
