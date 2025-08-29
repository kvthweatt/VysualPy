"""
Mixin classes for VysualPy node system.

These mixins provide shared functionality that can be composed into different
node types, promoting code reuse and separation of concerns.
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from PyQt5.QtWidgets import (
    QGraphicsTextItem, QGraphicsRectItem, QMenu, QAction, 
    QInputDialog, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QObject
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, 
    QPainterPath, QLinearGradient
)

from vpy_node_base import NodeState, NodeType


class RenderMixin:
    """
    Mixin that handles visual rendering of nodes.
    
    Provides consistent styling and visual feedback across different node types.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Clean, professional visual style properties
        self.background_color = QColor(47, 79, 79)   # Slate gray (original style)
        self.border_color = QColor(100, 100, 100)    # Medium gray
        self.selected_color = QColor(52, 152, 219)   # Subtle blue
        self.highlight_color = QColor(120, 120, 120) # Light gray
        self.error_color = QColor(231, 76, 60)       # Muted red
        self.text_color = QColor(255, 255, 255)     # White text
        
        # Subtle node type differentiation (minimal color variation)
        self.type_colors = {
            NodeType.BLUEPRINT: QColor(47, 79, 79),   # Slate gray (default)
            NodeType.EXECUTION: QColor(44, 62, 80),  # Darker blue-gray
            NodeType.BUILDABLE: QColor(47, 79, 79),  # Slate gray (same as blueprint)
            NodeType.COMMENT: QColor(60, 60, 60)     # Medium gray
        }
        
        # Monospace font settings for clean, code-like appearance
        self.title_font = QFont("Courier New", 10, QFont.Bold)
        self.content_font = QFont("Courier New", 8)
        
    def get_node_color(self) -> QColor:
        """Get the primary color for this node based on its type and state."""
        base_color = self.type_colors.get(self.node_type, self.background_color)
        
        # Modify color based on state
        if self.state == NodeState.SELECTED:
            return self.selected_color
        elif self.state == NodeState.HIGHLIGHTED:
            return self.highlight_color
        elif self.state == NodeState.ERROR:
            return self.error_color
        elif self.state == NodeState.DISABLED:
            # Make it more transparent/grayed out
            color = QColor(base_color)
            color.setAlpha(128)
            return color
        else:
            return base_color
            
    def paint(self, painter: QPainter, option, widget=None):
        """Enhanced paint method with proper styling."""
        # Don't call super().paint() to avoid default QGraphicsRectItem drawing
        
        rect = self.rect()
        
        # Enable antialiasing for smooth rendering (except for BuildableNode which wants sharp edges)
        use_antialiasing = not (hasattr(self, 'node_type') and self.node_type.value == 'buildable')
        painter.setRenderHint(QPainter.Antialiasing, use_antialiasing)
        
        # Get corner radius (BuildableNode sets this to 0 for sharp corners)
        corner_radius = getattr(self, 'corner_radius', 8)
        
        # Create path (rounded or sharp based on corner radius)
        if corner_radius > 0:
            path = QPainterPath()
            path.addRoundedRect(rect, corner_radius, corner_radius)
            
            # Fill background with gradient
            gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            node_color = self.get_node_color()
            gradient.setColorAt(0, node_color.lighter(110))
            gradient.setColorAt(1, node_color.darker(110))
            
            painter.fillPath(path, QBrush(gradient))
            
            # Draw border
            border_pen = QPen(self.get_border_color(), self.border_width)
            painter.setPen(border_pen)
            painter.drawPath(path)
        else:
            # Sharp corners for BuildableNode
            node_color = self.get_node_color()
            painter.fillRect(rect, QBrush(node_color))
            
            # Draw border
            border_pen = QPen(self.get_border_color(), self.border_width)
            painter.setPen(border_pen)
            painter.drawRect(rect)
        
        # Draw title
        self.paint_title(painter, rect)
        
        # Draw content if available
        if hasattr(self, 'content'):
            # Handle BuildableNode specially
            if hasattr(self, 'node_type') and self.node_type.value == 'buildable':
                # Always draw the text editor background
                self.paint_text_editor_background(painter, rect)
                # Only draw text content when not editing (to avoid duplication)
                if not getattr(self, 'editing', False):
                    self.paint_text_editor_content_only(painter, rect)
            # For other node types, only draw when not editing
            elif not getattr(self, 'editing', False):
                self.paint_content(painter, rect)
            
        # Draw ports
        self.paint_ports(painter)
        
        # Draw state indicators
        self.paint_state_indicators(painter, rect)
        
    def get_border_color(self) -> QColor:
        """Get the border color based on node state."""
        if self.state == NodeState.SELECTED:
            return self.selected_color.lighter(150)
        elif self.state == NodeState.HIGHLIGHTED:
            return self.highlight_color
        elif self.state == NodeState.ERROR:
            return self.error_color
        else:
            return self.border_color
            
    def paint_title(self, painter: QPainter, rect: QRectF):
        """Paint the node title."""
        painter.setPen(QPen(self.text_color))
        painter.setFont(self.title_font)
        
        # Calculate title area (top portion of node)
        title_rect = QRectF(
            rect.left() + 8, 
            rect.top() + 4,
            rect.width() - 16, 
            20
        )
        
        # Draw title text
        title = self.get_display_name() if hasattr(self, 'get_display_name') else self.name
        painter.drawText(title_rect, Qt.AlignLeft | Qt.AlignVCenter, title)
        
    def paint_content(self, painter: QPainter, rect: QRectF):
        """Paint the node content."""
        # Handle BuildableNode text editor appearance
        if hasattr(self, 'node_type') and self.node_type.value == 'buildable':
            self.paint_text_editor_content(painter, rect)
        else:
            self.paint_standard_content(painter, rect)
            
    def paint_text_editor_content(self, painter: QPainter, rect: QRectF):
        """Paint content with text editor appearance for BuildableNode."""
        painter.setFont(QFont("Consolas", 9))  # Monospace font for code
        
        # Text editor background area
        editor_rect = QRectF(
            rect.left() + 8,
            rect.top() + 28,
            rect.width() - 16,
            rect.height() - 36
        )
        
        # Draw text editor background with subtle gradient (grayscale)
        gradient = QLinearGradient(editor_rect.topLeft(), editor_rect.bottomLeft())
        gradient.setColorAt(0, QColor(250, 250, 250))  # Very light gray at top
        gradient.setColorAt(1, QColor(245, 245, 245))  # Slightly darker gray at bottom
        painter.fillRect(editor_rect, QBrush(gradient))
        
        # Draw text editor border (clean, sharp)
        editor_border = QPen(QColor(200, 200, 200), 1)  # Light gray border
        painter.setPen(editor_border)
        painter.drawRect(editor_rect)
        
        # Draw inner shadow/inset effect for depth
        inner_shadow = QPen(QColor(235, 235, 235), 1)
        painter.setPen(inner_shadow)
        inner_rect = QRectF(
            editor_rect.left() + 1,
            editor_rect.top() + 1,
            editor_rect.width() - 2,
            editor_rect.height() - 2
        )
        painter.drawRect(inner_rect)
        
        # Draw content text
        if hasattr(self, 'content') and self.content.strip():
            text_rect = QRectF(
                editor_rect.left() + 6,
                editor_rect.top() + 6,
                editor_rect.width() - 12,
                editor_rect.height() - 12
            )
            
            # Use dark text for readability on light background
            painter.setPen(QPen(QColor(40, 40, 40)))
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, self.content)
        else:
            # Show placeholder text for empty editor
            placeholder_rect = QRectF(
                editor_rect.left() + 6,
                editor_rect.top() + 6,
                editor_rect.width() - 12,
                20
            )
            painter.setPen(QPen(QColor(150, 150, 150)))  # Medium gray placeholder
            painter.drawText(placeholder_rect, Qt.AlignLeft | Qt.AlignVCenter, "# Enter code here...")
            
    def paint_text_editor_background(self, painter: QPainter, rect: QRectF):
        """Paint only the text editor background for BuildableNode (used during editing)."""
        # Text editor background area
        editor_rect = QRectF(
            rect.left() + 8,
            rect.top() + 28,
            rect.width() - 16,
            rect.height() - 36
        )
        
        # Draw text editor background with subtle gradient (grayscale)
        gradient = QLinearGradient(editor_rect.topLeft(), editor_rect.bottomLeft())
        gradient.setColorAt(0, QColor(250, 250, 250))  # Very light gray at top
        gradient.setColorAt(1, QColor(245, 245, 245))  # Slightly darker gray at bottom
        painter.fillRect(editor_rect, QBrush(gradient))
        
        # Draw text editor border (clean, sharp)
        editor_border = QPen(QColor(200, 200, 200), 1)  # Light gray border
        painter.setPen(editor_border)
        painter.drawRect(editor_rect)
        
        # Draw inner shadow/inset effect for depth
        inner_shadow = QPen(QColor(235, 235, 235), 1)
        painter.setPen(inner_shadow)
        inner_rect = QRectF(
            editor_rect.left() + 1,
            editor_rect.top() + 1,
            editor_rect.width() - 2,
            editor_rect.height() - 2
        )
        painter.drawRect(inner_rect)
        
    def paint_text_editor_content_only(self, painter: QPainter, rect: QRectF):
        """Paint only the text content for BuildableNode (without background)."""
        painter.setFont(QFont("Consolas", 9))  # Monospace font for code
        
        # Text editor background area
        editor_rect = QRectF(
            rect.left() + 8,
            rect.top() + 28,
            rect.width() - 16,
            rect.height() - 36
        )
        
        # Draw content text or placeholder
        if hasattr(self, 'content') and self.content.strip():
            text_rect = QRectF(
                editor_rect.left() + 6,
                editor_rect.top() + 6,
                editor_rect.width() - 12,
                editor_rect.height() - 12
            )
            
            # Use dark text for readability on light background
            painter.setPen(QPen(QColor(40, 40, 40)))
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, self.content)
        else:
            # Show placeholder text for empty editor
            placeholder_rect = QRectF(
                editor_rect.left() + 6,
                editor_rect.top() + 6,
                editor_rect.width() - 12,
                20
            )
            painter.setPen(QPen(QColor(150, 150, 150)))  # Medium gray placeholder
            painter.drawText(placeholder_rect, Qt.AlignLeft | Qt.AlignVCenter, "# Enter code here...")
            
    def paint_standard_content(self, painter: QPainter, rect: QRectF):
        """Paint content for standard nodes (Blueprint, Execution, etc.)."""
        painter.setPen(QPen(self.text_color.darker(150)))
        painter.setFont(self.content_font)
        
        # Calculate content area (below title)
        content_rect = QRectF(
            rect.left() + 8,
            rect.top() + 28,
            rect.width() - 16,
            rect.height() - 36
        )
        
        # For Blueprint nodes with auto-resize, show full content
        # For other nodes, truncate if too long
        content = self.content if hasattr(self, 'content') else ""
        if (hasattr(self, 'node_type') and 
            hasattr(self, 'auto_resize_to_content') and
            self.node_type.value == 'blueprint'):
            # Blueprint nodes are auto-sized, show full content
            pass  # Use full content without truncation
        else:
            # Other node types may need truncation
            if len(content) > 100:
                content = content[:97] + "..."
            
        painter.drawText(content_rect, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, content)
        
    def paint_ports(self, painter: QPainter):
        """Paint connection ports."""
        if not (hasattr(self, 'input_ports') and hasattr(self, 'output_ports')):
            return
            
        port_radius = 6
        port_color = QColor(200, 200, 200)
        port_pen = QPen(self.border_color, 2)
        
        # Paint input ports
        for port in self.input_ports.values():
            center = self.mapFromScene(self.mapToScene(port.position))
            painter.setPen(port_pen)
            painter.setBrush(QBrush(port_color))
            painter.drawEllipse(center, port_radius, port_radius)
            
        # Paint output ports  
        for port in self.output_ports.values():
            center = self.mapFromScene(self.mapToScene(port.position))
            painter.setPen(port_pen)
            painter.setBrush(QBrush(port_color))
            painter.drawEllipse(center, port_radius, port_radius)
            
    def paint_state_indicators(self, painter: QPainter, rect: QRectF):
        """Paint visual indicators for special states."""
        if self.state == NodeState.EDITING:
            # Draw editing indicator (small icon in top-right)
            indicator_rect = QRectF(rect.right() - 16, rect.top() + 4, 12, 12)
            painter.setPen(QPen(QColor(0, 255, 0), 2))
            painter.drawEllipse(indicator_rect)
            
        elif self.state == NodeState.ERROR:
            # Draw error indicator
            indicator_rect = QRectF(rect.right() - 16, rect.top() + 4, 12, 12)
            painter.setPen(QPen(self.error_color, 2))
            painter.drawLine(
                indicator_rect.topLeft() + QPointF(2, 2),
                indicator_rect.bottomRight() - QPointF(2, 2)
            )
            painter.drawLine(
                indicator_rect.topRight() + QPointF(-2, 2),
                indicator_rect.bottomLeft() + QPointF(2, -2)
            )
            
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle including border and effects."""
        rect = self.rect()
        margin = max(self.border_width * 2, 10)  # Extra margin for shadows/effects
        return rect.adjusted(-margin, -margin, margin, margin)
        
    def update_visual_style(self, **style_kwargs):
        """Update visual style properties and refresh display."""
        for key, value in style_kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.update()


class InteractionMixin:
    """
    Mixin that handles user interaction with nodes.
    
    Provides mouse event handling, context menus, and drag behavior.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Interaction state
        self.is_dragging = False
        self.drag_start_pos = QPointF()
        self.hover_port = None
        
        # Enable hover events
        self.setAcceptHoverEvents(True)
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.pos()
            
            # Check if clicking on a port
            port = self.get_port_at_position(event.pos())
            if port:
                self.handle_port_click(port, event)
                return
                
            # Handle selection based on modifiers
            modifiers = QApplication.keyboardModifiers()
            
            if modifiers & Qt.ControlModifier:
                # Ctrl+Click: Toggle selection of this node
                self.setSelected(not self.isSelected())
                if hasattr(self, 'set_state'):
                    if self.isSelected():
                        self.set_state(NodeState.SELECTED)
                    else:
                        self.set_state(NodeState.NORMAL)
            else:
                # Regular click: Clear other selections unless this node is already selected
                if not self.isSelected():
                    # Clear all other selections first
                    scene = self.scene()
                    if scene:
                        for item in scene.selectedItems():
                            if item != self:
                                item.setSelected(False)
                                if hasattr(item, 'set_state'):
                                    item.set_state(NodeState.NORMAL)
                    
                    # Select this node
                    self.setSelected(True)
                    if hasattr(self, 'set_state'):
                        self.set_state(NodeState.SELECTED)
                # If already selected, keep it selected for dragging
                    
        elif event.button() == Qt.RightButton:
            # Show context menu
            self.show_context_menu(event)
            
        # Only call super if it exists
        if hasattr(super(), 'mousePressEvent'):
            super().mousePressEvent(event)
            
    def mouseDoubleClickEvent(self, event):
        """Handle mouse double-click events."""
        if event.button() == Qt.LeftButton:
            # Start editing for editable nodes (like BuildableNode)
            if hasattr(self, 'startEditing'):
                self.startEditing()
                event.accept()
                return
                
        # Only call super if it exists
        if hasattr(super(), 'mouseDoubleClickEvent'):
            super().mouseDoubleClickEvent(event)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events with multi-selection support."""
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            # Calculate movement delta
            delta = event.pos() - self.drag_start_pos
            
            # Check if this node is part of a multi-selection
            scene = self.scene()
            selected_items = scene.selectedItems() if scene else []
            
            if len(selected_items) > 1 and self in selected_items:
                # Move all selected nodes together
                for item in selected_items:
                    if hasattr(item, 'setPos'):  # Ensure it's a movable item
                        current_pos = item.pos()
                        new_pos = current_pos + delta
                        
                        # Apply grid snapping if available
                        if hasattr(item, 'snapToGrid'):
                            new_pos.setX(item.snapToGrid(new_pos.x()))
                            new_pos.setY(item.snapToGrid(new_pos.y()))
                            
                        item.setPos(new_pos)
            else:
                # Single node movement
                new_pos = self.pos() + delta
                
                # Apply grid snapping if available
                if hasattr(self, 'snapToGrid'):
                    new_pos.setX(self.snapToGrid(new_pos.x()))
                    new_pos.setY(self.snapToGrid(new_pos.y()))
                    
                self.setPos(new_pos)
            
        # Only call super if it exists
        if hasattr(super(), 'mouseMoveEvent'):
            super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            
        # Only call super if it exists
        if hasattr(super(), 'mouseReleaseEvent'):
            super().mouseReleaseEvent(event)
        
    def hoverEnterEvent(self, event):
        """Handle hover enter events."""
        if hasattr(self, 'set_state') and self.state == NodeState.NORMAL:
            self.set_state(NodeState.HIGHLIGHTED)
        if hasattr(super(), 'hoverEnterEvent'):
            super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle hover leave events."""
        if hasattr(self, 'set_state') and self.state == NodeState.HIGHLIGHTED:
            self.set_state(NodeState.NORMAL)
        self.hover_port = None
        if hasattr(super(), 'hoverLeaveEvent'):
            super().hoverLeaveEvent(event)
        
    def hoverMoveEvent(self, event):
        """Handle hover move events."""
        # Check if hovering over a port
        port = self.get_port_at_position(event.pos())
        if port != self.hover_port:
            self.hover_port = port
            self.update()  # Refresh to show hover effect on port
            
        if hasattr(super(), 'hoverMoveEvent'):
            super().hoverMoveEvent(event)
        
    def get_port_at_position(self, pos: QPointF):
        """Get the port at the given position, if any."""
        if not (hasattr(self, 'input_ports') and hasattr(self, 'output_ports')):
            return None
            
        port_radius = 8  # Slightly larger than visual radius for easier clicking
        
        # Check input ports
        for port in self.input_ports.values():
            port_pos = port.position
            distance = (pos - port_pos).manhattanLength()
            if distance <= port_radius:
                return port
                
        # Check output ports
        for port in self.output_ports.values():
            port_pos = port.position
            distance = (pos - port_pos).manhattanLength()
            if distance <= port_radius:
                return port
                
        return None
        
    def handle_port_click(self, port, event):
        """Handle clicking on a connection port."""
        # This will be implemented by scene or connection manager
        if hasattr(self.scene(), 'handle_port_click'):
            self.scene().handle_port_click(port, event)
            
    def show_context_menu(self, event):
        """Show context menu for the node."""
        menu = QMenu()
        
        # BuildableNode specific actions
        if hasattr(self, 'node_type') and self.node_type.value == 'buildable':
            external_editor_action = QAction("📝 Open External Editor", menu)
            if hasattr(self, 'open_external_editor'):
                external_editor_action.triggered.connect(self.open_external_editor)
            else:
                external_editor_action.setEnabled(False)
            menu.addAction(external_editor_action)
            
            menu.addSeparator()
        
        # Standard actions
        delete_action = QAction("Delete", menu)
        delete_action.triggered.connect(self.request_deletion)
        menu.addAction(delete_action)
        
        duplicate_action = QAction("Duplicate", menu)
        duplicate_action.triggered.connect(self.request_duplication)
        menu.addAction(duplicate_action)
        
        menu.addSeparator()
        
        properties_action = QAction("Properties...", menu)
        properties_action.triggered.connect(self.show_properties)
        menu.addAction(properties_action)
        
        # Show the menu
        menu.exec_(event.screenPos())
        
    def request_deletion(self):
        """Request deletion of this node."""
        # Confirm deletion
        reply = QMessageBox.question(
            None, "Confirm Deletion",
            f"Are you sure you want to delete the node '{self.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if hasattr(self.scene(), 'remove_node'):
                self.scene().remove_node(self)
            else:
                # Fallback: remove from scene directly
                if hasattr(self, 'disconnect_all'):
                    self.disconnect_all()
                self.scene().removeItem(self)
                
    def request_duplication(self):
        """Request duplication of this node."""
        if hasattr(self.scene(), 'duplicate_node'):
            self.scene().duplicate_node(self)
            
    def show_properties(self):
        """Show properties dialog for this node."""
        # Simple name change dialog for now
        new_name, ok = QInputDialog.getText(
            None, "Node Properties",
            "Node name:", text=self.name
        )
        
        if ok and new_name.strip():
            self.name = new_name.strip()
            if hasattr(self, 'on_update'):
                self.on_update()
            self.update()


class EditableMixin:
    """
    Mixin that provides in-place editing functionality for nodes.
    
    Allows nodes to be edited directly in the graph view.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Editing state
        self.editing = False
        self.text_item: Optional[QGraphicsTextItem] = None
        self.original_content = ""
        
    def startEditing(self):
        """Start in-place editing of the node."""
        if self.editing:
            return
            
        self.editing = True
        self.original_content = getattr(self, 'content', '')
        
        # Set state
        if hasattr(self, 'set_state'):
            self.set_state(NodeState.EDITING)
            
        # Create text editor
        self.text_item = QGraphicsTextItem(self.original_content, self)
        self.text_item.setFont(QFont("Consolas", 9))  # Monospace for code
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        
        # Set text color based on node type
        if hasattr(self, 'node_type') and self.node_type.value == 'buildable':
            # Dark text for BuildableNode (light background)
            self.text_item.setDefaultTextColor(QColor(40, 40, 40))
        else:
            # Light text for other nodes (dark background)
            self.text_item.setDefaultTextColor(QColor(255, 255, 255))
        
        # Position the text item over the editor area
        rect = self.rect()
        editor_padding = 10 if hasattr(self, 'node_type') and self.node_type.value == 'buildable' else 8
        self.text_item.setPos(rect.left() + editor_padding, rect.top() + 32)
        
        # For BuildableNode: disable word wrapping to allow horizontal expansion
        if hasattr(self, 'node_type') and self.node_type.value == 'buildable':
            self.text_item.setTextWidth(-1)  # -1 disables word wrapping
        else:
            self.text_item.setTextWidth(rect.width() - (editor_padding * 2))
        
        # Focus the text editor
        self.text_item.setFocus()
        
        # Connect signals
        document = self.text_item.document()
        document.contentsChanged.connect(self.on_text_changed)
        
        # Force visual update to hide painted content during editing
        self.update()
        
    def stopEditing(self):
        """Stop editing and save changes."""
        if not self.editing:
            return
            
        self.commitEdit()
        
    def cancelEdit(self):
        """Cancel editing and revert changes."""
        if not self.editing:
            return
            
        # Revert to original content
        if hasattr(self, 'content'):
            self.content = self.original_content
            
        self._cleanup_editing()
        
    def commitEdit(self):
        """Commit the current edit and save changes."""
        if not self.editing or not self.text_item:
            return
            
        new_content = self.text_item.toPlainText()
        old_content = self.original_content
        
        # Process content change
        if hasattr(self, 'process_content_change'):
            self.process_content_change(old_content, new_content)
        else:
            # Default behavior: just update content
            self.content = new_content
            
        self._cleanup_editing()
        
        # Trigger auto-generation if this is a BuildableNode and content changed
        if (old_content != new_content and 
            hasattr(self, 'node_type') and 
            self.node_type.value == 'buildable' and 
            hasattr(self, 'scene') and 
            self.scene()):
            
            scene = self.scene()
            if hasattr(scene, 'check_and_create_called_functions'):
                # Trigger the auto-generation functionality
                scene.check_and_create_called_functions(self)
        
        # Trigger update hooks
        if hasattr(self, 'on_update'):
            self.on_update()
            
    def _cleanup_editing(self):
        """Clean up editing state and UI elements."""
        self.editing = False
        
        if self.text_item:
            self.scene().removeItem(self.text_item)
            self.text_item = None
            
        # Reset state
        if hasattr(self, 'set_state'):
            self.set_state(NodeState.NORMAL)
            
        self.update()
        
    def on_text_changed(self):
        """Handle text changes during editing."""
        if not self.editing or not self.text_item:
            return
            
        # Update node size based on text content
        text_rect = self.text_item.boundingRect()
        current_rect = self.rect()
        
        # Calculate minimum required dimensions
        min_height = text_rect.height() + 50  # Title + padding
        
        # For BuildableNode: also expand horizontally without word wrapping
        if hasattr(self, 'node_type') and self.node_type.value == 'buildable':
            min_width = max(text_rect.width() + 30, self.min_width)  # Text + padding + minimum
            
            # Expand both horizontally and vertically as needed
            new_width = max(current_rect.width(), min_width)
            new_height = max(current_rect.height(), min_height)
            
            if new_width != current_rect.width() or new_height != current_rect.height():
                new_rect = QRectF(
                    current_rect.x(), current_rect.y(),
                    new_width, new_height
                )
                self.setRect(new_rect)
                self.size = new_rect
                
                # Update port positions after resize
                if hasattr(self, '_update_buildable_port_positions'):
                    self._update_buildable_port_positions()
                    
                self.update()
        else:
            # Standard behavior: only expand vertically
            if current_rect.height() < min_height:
                new_rect = QRectF(
                    current_rect.x(), current_rect.y(),
                    current_rect.width(), min_height
                )
                self.setRect(new_rect)
                self.update()
            
    def keyPressEvent(self, event):
        """Handle key press events during editing."""
        if self.editing:
            if event.key() == Qt.Key_Escape:
                self.cancelEdit()
                event.accept()
                return
            elif event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
                self.commitEdit()
                event.accept()
                return
                
        # Only call super if it exists
        if hasattr(super(), 'keyPressEvent'):
            super().keyPressEvent(event)
        
    def focusOutEvent(self, event):
        """Handle focus out events."""
        if self.editing:
            # Auto-commit when losing focus
            self.commitEdit()
            
        if hasattr(super(), 'focusOutEvent'):
            super().focusOutEvent(event)
