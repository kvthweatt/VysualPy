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

class EnhancedBlueprintScene(BlueprintScene):
    """Enhanced scene with comprehensive node creation capabilities."""
    
    def __init__(self):
        super().__init__()
        self.node_counter = {'Blueprint': 0, 'Execution': 0, 'Buildable': 0}
        
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
            "• Drag to select multiple nodes (rubber band selection)\n" +
            "• Ctrl+Click to add/remove nodes from selection\n" +
            "• Drag selected nodes to move them together\n" +
            "• Right-click on selected nodes for group operations\n" +
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
