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
        
        # Visual style properties
        self.background_color = QColor(60, 60, 60)
        self.border_color = QColor(100, 100, 100)
        self.selected_color = QColor(0, 120, 215)
        self.highlight_color = QColor(255, 165, 0)
        self.error_color = QColor(255, 100, 100)
        self.text_color = QColor(255, 255, 255)
        
        # Node type specific colors
        self.type_colors = {
            NodeType.BLUEPRINT: QColor(70, 130, 180),  # Steel blue
            NodeType.EXECUTION: QColor(154, 205, 50),  # Yellow green
            NodeType.BUILDABLE: QColor(255, 140, 0),   # Dark orange
            NodeType.COMMENT: QColor(128, 128, 128)    # Gray
        }
        
        # Font settings
        self.title_font = QFont("Arial", 10, QFont.Bold)
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
        rect = self.rect()
        
        # Enable antialiasing for smooth rendering
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(rect, self.corner_radius, self.corner_radius)
        
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
        
        # Draw title
        self.paint_title(painter, rect)
        
        # Draw content if available
        if hasattr(self, 'content') and self.content.strip():
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
        painter.setPen(QPen(self.text_color.darker(150)))
        painter.setFont(self.content_font)
        
        # Calculate content area (below title)
        content_rect = QRectF(
            rect.left() + 8,
            rect.top() + 28,
            rect.width() - 16,
            rect.height() - 36
        )
        
        # Truncate content if too long
        content = self.content
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
                
            # Regular selection handling
            if not self.isSelected():
                self.setSelected(True)
                if hasattr(self, 'set_state'):
                    self.set_state(NodeState.SELECTED)
                    
        elif event.button() == Qt.RightButton:
            # Show context menu
            self.show_context_menu(event)
            
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            # Handle dragging
            delta = event.pos() - self.drag_start_pos
            new_pos = self.pos() + delta
            
            # Apply grid snapping if available
            if hasattr(self, 'snapToGrid'):
                new_pos.setX(self.snapToGrid(new_pos.x()))
                new_pos.setY(self.snapToGrid(new_pos.y()))
                
            self.setPos(new_pos)
            
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            
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
        self.text_item.setFont(QFont("Courier New", 9))
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.text_item.setDefaultTextColor(QColor(255, 255, 255))
        
        # Position the text item
        rect = self.rect()
        self.text_item.setPos(rect.left() + 8, rect.top() + 28)
        self.text_item.setTextWidth(rect.width() - 16)
        
        # Focus the text editor
        self.text_item.setFocus()
        
        # Connect signals
        document = self.text_item.document()
        document.contentsChanged.connect(self.on_text_changed)
        
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
        
        # Process content change
        if hasattr(self, 'process_content_change'):
            self.process_content_change(self.original_content, new_content)
        else:
            # Default behavior: just update content
            self.content = new_content
            
        self._cleanup_editing()
        
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
            
        # Update node size if needed
        text_rect = self.text_item.boundingRect()
        current_rect = self.rect()
        
        min_height = text_rect.height() + 40  # Title + padding
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
                
        super().keyPressEvent(event)
        
    def focusOutEvent(self, event):
        """Handle focus out events."""
        if self.editing:
            # Auto-commit when losing focus
            self.commitEdit()
            
        if hasattr(super(), 'focusOutEvent'):
            super().focusOutEvent(event)
