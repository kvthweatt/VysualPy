"""
Concrete implementations of different node types for VysualPy.

These classes combine the BaseNode with appropriate mixins to create
specialized node types for different use cases.
"""

import ast
import re
from typing import Dict, List, Any, Optional

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QColor, QFontMetrics, QFont

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
        
        # Dynamic sizing properties
        self.min_width = 120  # Minimum width for ports and title
        self.min_height = 60  # Minimum height
        self.padding_x = 16   # Horizontal padding (8px on each side)
        self.padding_y = 40   # Vertical padding (for title + margins)
        self.line_height = 12 # Height per line of code
        
        # Add default ports
        self.add_input_port("input", "code", "Input")
        self.add_output_port("output", "code", "Output")
        
        # Analyze content and resize on creation
        if content.strip():
            self.analyze_content()
        self.auto_resize_to_content()
            
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
            return f"[Class] {self.name}"
        elif self.content.strip().startswith(('def ', 'async def ')):
            return f"[Func] {self.name}"
        else:
            return f"[Code] {self.name}"
            
    def get_tooltip_text(self) -> str:
        """Get tooltip text for this node."""
        content_preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"{self.name}\n\n{content_preview}"
        
    def auto_resize_to_content(self):
        """Automatically resize the node to fit its content."""
        # Get fonts (matching RenderMixin fonts)
        title_font = QFont("Courier New", 10, QFont.Bold)
        content_font = QFont("Courier New", 8)
        
        # Calculate dimensions needed for content
        required_width, required_height = self.calculate_content_dimensions(
            title_font, content_font
        )
        
        # Ensure minimum dimensions
        final_width = max(required_width, self.min_width)
        final_height = max(required_height, self.min_height)
        
        # Create new rect and update
        current_rect = self.rect()
        new_rect = QRectF(
            current_rect.x(),
            current_rect.y(), 
            final_width,
            final_height
        )
        
        # Update size and rect
        self.size = new_rect
        self.setRect(new_rect)
        
        # Update port positions to match new size
        self._update_port_positions()
        
        # Update scene connections if we have them
        if hasattr(self, 'scene') and self.scene():
            scene = self.scene()
            if hasattr(scene, 'update_all_connections'):
                scene.update_all_connections()
                
    def calculate_content_dimensions(self, title_font: QFont, content_font: QFont) -> tuple:
        """Calculate required width and height for the node content."""
        title_metrics = QFontMetrics(title_font)
        content_metrics = QFontMetrics(content_font)
        
        # Calculate title dimensions
        title_text = self.get_display_name() if hasattr(self, 'get_display_name') else self.name
        title_width = title_metrics.horizontalAdvance(title_text)
        title_height = title_metrics.height()
        
        # Calculate content dimensions
        content_width = 0
        content_height = 0
        
        if self.content.strip():
            lines = self.content.split('\n')
            content_height = len(lines) * content_metrics.height()
            
            # Find the widest line
            for line in lines:
                line_width = content_metrics.horizontalAdvance(line)
                content_width = max(content_width, line_width)
        
        # Calculate total required dimensions
        required_width = max(title_width, content_width) + self.padding_x
        required_height = title_height + content_height + self.padding_y
        
        return required_width, required_height
        
    def can_accept_content(self, content: str) -> bool:
        """Check if this node can accept the given content."""
        # Blueprint nodes can accept any Python code
        return True
        
    def process_content_change(self, old_content: str, new_content: str):
        """Process a change in node content."""
        self.content = new_content
        self.full_content = new_content
        self.analyze_content()
        
        # Auto-resize to fit new content
        self.auto_resize_to_content()
        
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
        prefix = "[Cond]" if self.is_conditional else "[Exec]"
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
    
    Looks like a mini text editor with:
    - Top left: Input connection (execution flow in)
    - Bottom left: Return connection (execution flow out)  
    - Right side: Multiple outputs for each function call made in the code
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
        
        # Mini text editor sizing properties
        self.min_width = 200   # Wider for text editor look
        self.min_height = 120  # Taller for multiple lines
        self.padding_x = 12    # Text editor padding
        self.padding_y = 45    # Space for title and margins
        self.line_height = 14  # Readable line height for code
        
        # Set buildable-specific visual properties (clean text editor style)
        self.background_color = QColor(240, 240, 240)   # Light gray background
        self.border_color = QColor(180, 180, 180)       # Medium gray border
        self.text_color = QColor(60, 60, 60)            # Dark gray text
        self.corner_radius = 0                          # Sharp corners for clean look
        
        # Setup initial port layout
        self._setup_initial_ports()
        
        # Analyze content on creation
        if content.strip():
            self.analyze_and_update()
        
        # Auto-resize to fit content like a text editor
        self.auto_resize_to_content()
            
    def _setup_initial_ports(self):
        """Setup the initial port layout for buildable nodes."""
        # Clear any existing ports
        self.input_ports.clear()
        self.output_ports.clear()
        
        # Top left: Execution input (flow coming in)
        self.add_input_port("exec_in", "execution", "In")
        
        # Bottom left: Return/output (execution flow going out)
        self.add_output_port("exec_out", "execution", "Return")
        
        # Update port positions for this specific layout
        self._update_buildable_port_positions()
        
    def _update_buildable_port_positions(self):
        """Update port positions for the buildable node layout."""
        rect = self.rect()
        port_radius = 8
        
        # Top left: Execution input
        if "exec_in" in self.input_ports:
            self.input_ports["exec_in"].position = QPointF(
                -port_radius, 
                rect.height() * 0.15  # Near the top
            )
        
        # Bottom left: Return output
        if "exec_out" in self.output_ports:
            self.output_ports["exec_out"].position = QPointF(
                -port_radius,
                rect.height() * 0.85  # Near the bottom
            )
        
        # Right side: Function call outputs (distributed vertically)
        function_output_ports = [port_id for port_id in self.output_ports.keys() 
                               if port_id.startswith("call_")]
        
        if function_output_ports:
            # Distribute function call ports evenly on the right side
            for i, port_id in enumerate(function_output_ports):
                # Calculate position for this function call port
                y_ratio = 0.2 + (0.6 * i / max(1, len(function_output_ports) - 1)) if len(function_output_ports) > 1 else 0.5
                y_pos = rect.height() * y_ratio
                
                self.output_ports[port_id].position = QPointF(
                    rect.width() + port_radius,
                    y_pos
                )
                
    def auto_resize_to_content(self):
        """Auto-resize like a text editor to fit content."""
        # Calculate dimensions based on text content
        content_font = QFont("Consolas", 9)  # Monospace font for code
        title_font = QFont("Segoe UI", 9, QFont.Bold)
        
        required_width, required_height = self.calculate_text_editor_dimensions(
            title_font, content_font
        )
        
        # Ensure minimum text editor size
        final_width = max(required_width, self.min_width)
        final_height = max(required_height, self.min_height)
        
        # Update rect
        current_rect = self.rect()
        new_rect = QRectF(
            current_rect.x(),
            current_rect.y(), 
            final_width,
            final_height
        )
        
        self.size = new_rect
        self.setRect(new_rect)
        
        # Update port positions after resize
        self._update_buildable_port_positions()
        
        # Update scene connections if available
        if hasattr(self, 'scene') and self.scene():
            scene = self.scene()
            if hasattr(scene, 'update_all_connections'):
                scene.update_all_connections()
                
    def calculate_text_editor_dimensions(self, title_font: QFont, content_font: QFont) -> tuple:
        """Calculate required dimensions for text editor appearance."""
        title_metrics = QFontMetrics(title_font)
        content_metrics = QFontMetrics(content_font)
        
        # Title dimensions
        title_text = self.get_display_name()
        title_width = title_metrics.horizontalAdvance(title_text)
        title_height = title_metrics.height()
        
        # Content dimensions (like a text editor)
        content_width = 0
        content_height = 0
        
        if self.content.strip():
            lines = self.content.split('\n')
            # Ensure minimum lines for text editor appearance
            line_count = max(len(lines), 4)  # At least 4 lines visible
            content_height = line_count * content_metrics.height()
            
            # Find widest line for width calculation
            for line in lines:
                line_width = content_metrics.horizontalAdvance(line)
                content_width = max(content_width, line_width)
                
            # Add some width for text editor appearance
            content_width = max(content_width, 180)  # Minimum readable width
        else:
            # Empty editor size
            content_width = 180
            content_height = 4 * content_metrics.height()  # 4 empty lines
        
        # Calculate total required dimensions
        required_width = max(title_width, content_width) + self.padding_x
        required_height = title_height + content_height + self.padding_y
        
        return required_width, required_height
            
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
        """Detect function calls in the content and create output ports for them."""
        # Import here to avoid circular imports
        from vpy_blueprints import detect_function_calls
        
        try:
            old_function_calls = self.function_calls.copy()
            self.function_calls = detect_function_calls(self.content)
            
            # Update function call output ports
            self._update_function_call_ports(old_function_calls, self.function_calls)
            
        except Exception as e:
            print(f"Error detecting function calls: {e}")
            self.function_calls = []
            
    def _update_function_call_ports(self, old_calls: List[str], new_calls: List[str]):
        """Update output ports based on function calls in the code."""
        # Remove ports for function calls that are no longer present
        for old_call in old_calls:
            port_id = f"call_{old_call}"
            if port_id in self.output_ports and old_call not in new_calls:
                self.remove_port(port_id)
        
        # Add ports for new function calls
        for new_call in new_calls:
            port_id = f"call_{new_call}"
            if port_id not in self.output_ports:
                self.add_output_port(port_id, "execution", new_call)
        
        # Update port positions after changes
        self._update_buildable_port_positions()
            
    def get_display_name(self) -> str:
        """Get the display name for this node."""
        if self.editing:
            return f"📝 {self.name} (editing)"
        elif self.is_class:
            return f"🏗️ {self.name}"
        elif self.content.strip().startswith(('def ', 'async def ')):
            return f"⚡ {self.name}"
        else:
            return f"📄 {self.name}"
            
    def get_tooltip_text(self) -> str:
        """Get tooltip text for this node."""
        tooltip = f"Code Editor: {self.name}"
        if self.function_calls:
            tooltip += f"\n\nFunction Calls:"
            for call in self.function_calls[:5]:  # Show up to 5 calls
                tooltip += f"\n  • {call}()"
            if len(self.function_calls) > 5:
                tooltip += f"\n  ... and {len(self.function_calls) - 5} more"
        if self.editing:
            tooltip += "\n\n📝 Editing Mode:"
            tooltip += "\n  Ctrl+Enter: Save changes"
            tooltip += "\n  Escape: Cancel editing"
        else:
            tooltip += "\n\n💡 Double-click to edit"
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
        
        # Re-analyze content and update ports
        self.analyze_and_update()
        
        # Auto-resize to fit new content
        self.auto_resize_to_content()
        
        # Update visual appearance
        self.update()
        
        # Sync with external editors (if any are open)
        self.sync_with_external_editors(new_content)
        
        # Sync with IDE if available
        if self.parent_ide and hasattr(self.scene(), 'check_and_create_called_functions'):
            self.scene().check_and_create_called_functions(self)
            
    def open_external_editor(self):
        """Open the external text editor dialog for this node."""
        # Import here to avoid circular imports
        from vpy_editor import ExternalTextEditorDialog
        
        # Create and show the external editor dialog
        dialog = ExternalTextEditorDialog(
            title=self.name,
            content=self.content,
            node_reference=self,
            parent=None  # Make it a standalone window
        )
        
        dialog.show()
        
        # Store reference to prevent garbage collection
        if not hasattr(self, '_external_editors'):
            self._external_editors = []
        self._external_editors.append(dialog)
        
        # Clean up reference when dialog closes
        def cleanup_reference():
            if dialog in getattr(self, '_external_editors', []):
                self._external_editors.remove(dialog)
                
        dialog.destroyed.connect(cleanup_reference)
        
        return dialog
        
    def sync_with_external_editors(self, new_content: str):
        """Sync content changes with any open external editors."""
        if hasattr(self, '_external_editors'):
            for editor in self._external_editors:
                # Check if the content is different to avoid infinite loops
                if editor.get_content() != new_content:
                    editor.set_content(new_content)
            
    def stopEditing(self):
        """Override to ensure proper editing cleanup and callbacks."""
        if self.editing:
            # Commit the edit first
            self.commitEdit()
            
            # Trigger the scene callback for auto-function creation
            if hasattr(self.scene(), 'check_and_create_called_functions'):
                self.scene().check_and_create_called_functions(self)


class LegacyConnectionPoint:
    """Legacy compatibility wrapper for connection points."""
    
    def __init__(self, parent_node, is_output):
        self.parent_node = parent_node
        self.is_output = is_output
        self.connections = []  # Legacy connection list
        self._pos = QPointF(0, 0)
        
    def setPos(self, x, y):
        """Set position of connection point."""
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            self._pos = QPointF(x, y)
        else:
            self._pos = x  # Assume x is a QPointF
            
    def pos(self):
        """Get position of connection point."""
        return self._pos
        
    def scenePos(self):
        """Get scene position of connection point."""
        return self.parent_node.mapToScene(self._pos)
        
    def parentItem(self):
        """Get parent item (for legacy compatibility)."""
        return self.parent_node
        
    def addConnection(self, connection):
        """Add a connection to this point."""
        if connection not in self.connections:
            self.connections.append(connection)
            
    def removeConnection(self, connection):
        """Remove a connection from this point."""
        if connection in self.connections:
            self.connections.remove(connection)


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
