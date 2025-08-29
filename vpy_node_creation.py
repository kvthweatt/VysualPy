#!/usr/bin/env python3
"""
Enhanced node creation system for VysualPy.

This module provides the NodeCreationDialog and related functionality
extracted from debug_node_system.py for production use.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, 
    QLineEdit, QTextEdit, QPushButton, QLabel, QComboBox, QGroupBox,
    QCheckBox, QSpinBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor

class NodeCreationDialog(QDialog):
    """Enhanced dialog for creating new nodes with rich configuration options."""
    
    def __init__(self, node_type=None, parent=None):
        super().__init__(parent)
        self.node_type = node_type
        self.setWindowTitle(f"Create {node_type} Node" if node_type else "Create Node")
        self.setModal(True)
        self.resize(500, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create scroll area for the form (in case it gets long)
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Node type selection (if not specified)
        if not node_type:
            self.setup_node_type_selection(scroll_layout)
        else:
            self.current_node_type = node_type
            
        # Basic properties group
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setText(f"New {self.current_node_type}" if hasattr(self, 'current_node_type') else "New Node")
        self.name_edit.selectAll()  # Auto-select for easy editing
        basic_layout.addRow("Name:", self.name_edit)
        
        scroll_layout.addWidget(basic_group)
        
        # Content group (for nodes that support content)
        if not node_type or node_type in ["Blueprint", "Buildable"]:
            self.setup_content_section(scroll_layout)
        
        # Node-specific options
        if node_type == "Execution":
            self.setup_execution_options(scroll_layout)
        elif node_type == "Blueprint":
            self.setup_blueprint_options(scroll_layout)
        elif node_type == "Buildable":
            self.setup_buildable_options(scroll_layout)
            
        # Advanced options group
        self.setup_advanced_options(scroll_layout)
        
        # Set up scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Buttons
        self.setup_buttons(layout)
        
        # Set initial focus
        self.name_edit.setFocus()
        
        # Connect signals for dynamic updates
        self.connect_signals()
        
    def setup_node_type_selection(self, layout):
        """Setup node type selection dropdown."""
        type_group = QGroupBox("Node Type")
        type_layout = QFormLayout(type_group)
        
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems(["Blueprint", "Execution", "Buildable"])
        self.current_node_type = "Blueprint"  # Default
        
        self.node_type_combo.currentTextChanged.connect(self.on_node_type_changed)
        type_layout.addRow("Type:", self.node_type_combo)
        
        layout.addWidget(type_group)
        
    def setup_content_section(self, layout):
        """Setup content editing section."""
        content_group = QGroupBox("Content")
        content_layout = QVBoxLayout(content_group)
        
        # Template selection
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))
        
        self.template_combo = QComboBox()
        self.update_template_options()
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        template_layout.addWidget(self.template_combo)
        template_layout.addStretch()
        
        content_layout.addLayout(template_layout)
        
        # Content editor
        self.content_edit = QTextEdit()
        self.content_edit.setFont(QFont("Courier New", 10))
        self.content_edit.setPlainText(self.get_default_content())
        content_layout.addWidget(self.content_edit)
        
        # Live preview checkbox
        self.live_preview_check = QCheckBox("Live syntax highlighting")
        self.live_preview_check.setChecked(True)
        content_layout.addWidget(self.live_preview_check)
        
        layout.addWidget(content_group)
        
    def setup_execution_options(self, layout):
        """Setup options specific to execution nodes."""
        exec_group = QGroupBox("Execution Properties")
        exec_layout = QFormLayout(exec_group)
        
        # Original name field
        self.original_name_edit = QLineEdit()
        self.original_name_edit.setText(self.name_edit.text())
        exec_layout.addRow("Original Name:", self.original_name_edit)
        
        # Conditional execution checkbox
        self.conditional_check = QCheckBox("Conditional execution")
        exec_layout.addRow("Options:", self.conditional_check)
        
        # Return value checkbox
        self.has_return_check = QCheckBox("Has return value")
        exec_layout.addRow("", self.has_return_check)
        
        layout.addWidget(exec_group)
        
    def setup_blueprint_options(self, layout):
        """Setup options specific to blueprint nodes."""
        blueprint_group = QGroupBox("Blueprint Properties")
        blueprint_layout = QFormLayout(blueprint_group)
        
        # Auto-resize checkbox
        self.auto_resize_check = QCheckBox("Auto-resize to content")
        self.auto_resize_check.setChecked(True)
        blueprint_layout.addRow("Layout:", self.auto_resize_check)
        
        # Class/Function detection
        self.auto_detect_type_check = QCheckBox("Auto-detect class/function")
        self.auto_detect_type_check.setChecked(True)
        blueprint_layout.addRow("Detection:", self.auto_detect_type_check)
        
        layout.addWidget(blueprint_group)
        
    def setup_buildable_options(self, layout):
        """Setup options specific to buildable nodes."""
        buildable_group = QGroupBox("Buildable Properties")
        buildable_layout = QFormLayout(buildable_group)
        
        # Auto-connect checkbox
        self.auto_connect_check = QCheckBox("Auto-create connections from code analysis")
        self.auto_connect_check.setChecked(True)
        buildable_layout.addRow("Connections:", self.auto_connect_check)
        
        # Sync with editor checkbox
        self.sync_editor_check = QCheckBox("Sync with global text editor")
        self.sync_editor_check.setChecked(True)
        buildable_layout.addRow("Editor:", self.sync_editor_check)
        
        layout.addWidget(buildable_group)
        
    def setup_advanced_options(self, layout):
        """Setup advanced configuration options."""
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        # Position settings
        self.auto_position_check = QCheckBox("Auto-position relative to selection")
        self.auto_position_check.setChecked(True)
        advanced_layout.addRow("Positioning:", self.auto_position_check)
        
        # Size settings
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 800)
        self.width_spin.setValue(300)
        self.width_spin.setSuffix(" px")
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(60, 600)
        self.height_spin.setValue(150)
        self.height_spin.setSuffix(" px")
        
        size_layout.addWidget(QLabel("Width:"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("Height:"))
        size_layout.addWidget(self.height_spin)
        size_layout.addStretch()
        
        advanced_layout.addRow("Size:", size_layout)
        
        # Grid snap
        self.grid_snap_check = QCheckBox("Snap to grid")
        self.grid_snap_check.setChecked(True)
        advanced_layout.addRow("Grid:", self.grid_snap_check)
        
        layout.addWidget(advanced_group)
        
    def setup_buttons(self, layout):
        """Setup dialog buttons."""
        button_layout = QHBoxLayout()
        
        # Preview button
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.show_preview)
        button_layout.addWidget(self.preview_button)
        
        button_layout.addStretch()
        
        # Standard buttons
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.accept)
        self.create_button.setDefault(True)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
        
    def connect_signals(self):
        """Connect signals for dynamic behavior."""
        # Update original name when name changes (for execution nodes)
        if hasattr(self, 'original_name_edit'):
            self.name_edit.textChanged.connect(
                lambda text: self.original_name_edit.setText(text)
            )
            
        # Auto-detect content type when content changes
        if hasattr(self, 'content_edit') and hasattr(self, 'auto_detect_type_check'):
            self.content_edit.textChanged.connect(self.on_content_changed)
            
        # Update templates when node type changes
        if hasattr(self, 'node_type_combo'):
            self.node_type_combo.currentTextChanged.connect(self.update_template_options)
            
    def on_node_type_changed(self, node_type):
        """Handle node type selection change."""
        self.current_node_type = node_type
        self.update_template_options()
        
        # Update content with appropriate template
        if hasattr(self, 'content_edit'):
            self.content_edit.setPlainText(self.get_default_content())
            
        # Update window title
        self.setWindowTitle(f"Create {node_type} Node")
        
    def on_template_changed(self, template_name):
        """Handle template selection change."""
        if hasattr(self, 'content_edit'):
            content = self.get_template_content(template_name)
            if content:
                self.content_edit.setPlainText(content)
                
    def on_content_changed(self):
        """Handle content changes for auto-detection."""
        if (hasattr(self, 'auto_detect_type_check') and 
            self.auto_detect_type_check.isChecked()):
            
            content = self.content_edit.toPlainText().strip()
            if content.startswith('class '):
                # Extract class name
                try:
                    first_line = content.split('\\n')[0]
                    class_name = first_line.split()[1].split('(')[0].split(':')[0]
                    self.name_edit.setText(class_name)
                except (IndexError, AttributeError):
                    pass
            elif content.startswith(('def ', 'async def ')):
                # Extract function name
                try:
                    first_line = content.split('\\n')[0]
                    if content.startswith('async def '):
                        func_name = first_line.split()[2].split('(')[0]
                    else:
                        func_name = first_line.split()[1].split('(')[0]
                    self.name_edit.setText(func_name)
                except (IndexError, AttributeError):
                    pass
                    
    def update_template_options(self):
        """Update available templates based on node type."""
        if not hasattr(self, 'template_combo'):
            return
            
        self.template_combo.clear()
        
        node_type = getattr(self, 'current_node_type', self.node_type or 'Blueprint')
        
        if node_type == "Blueprint":
            self.template_combo.addItems([
                "Empty Function", "Class Template", "Method Template", 
                "Property Template", "Custom"
            ])
        elif node_type == "Buildable":
            self.template_combo.addItems([
                "Simple Code", "Function Call", "Variable Assignment",
                "Import Statement", "Custom"
            ])
        elif node_type == "Execution":
            self.template_combo.addItems([
                "Function Execution", "Method Call", "Conditional Block", "Custom"
            ])
            
    def get_default_content(self):
        """Get default content for the current node type."""
        node_type = getattr(self, 'current_node_type', self.node_type or 'Blueprint')
        
        if node_type == "Blueprint":
            return "def new_function():\\n    \\\"\\\"\\\"A new function.\\\"\\\"\\\"\\n    pass"
        elif node_type == "Buildable":
            return "# Buildable code block\\nprint('Hello from buildable node')"
        elif node_type == "Execution":
            return "# Execution flow node\\n# This represents a function call in the execution graph"
        else:
            return ""
            
    def get_template_content(self, template_name):
        """Get content for a specific template."""
        templates = {
            # Blueprint templates
            "Empty Function": "def new_function():\\n    pass",
            "Class Template": "class NewClass:\\n    def __init__(self):\\n        pass",
            "Method Template": "def method_name(self, param):\\n    \\\"\\\"\\\"Method description.\\\"\\\"\\\"\\n    return param",
            "Property Template": "@property\\ndef property_name(self):\\n    return self._property_name",
            
            # Buildable templates
            "Simple Code": "# Simple code block\\nresult = 42\\nprint(result)",
            "Function Call": "result = some_function(arg1, arg2)\\nprint(f'Result: {result}')",
            "Variable Assignment": "variable_name = 'value'\\nprint(variable_name)",
            "Import Statement": "import module_name\\nfrom package import specific_item",
            
            # Execution templates
            "Function Execution": "function_name(arguments)",
            "Method Call": "object.method_name(arguments)",
            "Conditional Block": "if condition:\\n    execute_code()"
        }
        
        return templates.get(template_name, "")
        
    def show_preview(self):
        """Show a preview of the node that would be created."""
        # This could open a small preview window showing how the node would look
        # For now, we'll just update the main dialog with current settings
        data = self.get_node_data()
        
        # Show preview info in a simple dialog
        from PyQt5.QtWidgets import QMessageBox
        preview_text = f"Node Preview:\\n\\n"
        preview_text += f"Type: {data.get('type', 'Unknown')}\\n"
        preview_text += f"Name: {data['name']}\\n"
        
        if data.get('content'):
            preview_text += f"Content Length: {len(data['content'])} characters\\n"
            preview_text += f"Content Preview:\\n{data['content'][:100]}{'...' if len(data['content']) > 100 else ''}"
            
        QMessageBox.information(self, "Node Preview", preview_text)
        
    def get_node_data(self):
        """Get all the data needed to create the node."""
        node_type = getattr(self, 'current_node_type', self.node_type)
        
        data = {
            'type': node_type,
            'name': self.name_edit.text().strip() or f"New {node_type}",
            'auto_position': getattr(self, 'auto_position_check', type('obj', (object,), {'isChecked': lambda: True})()).isChecked(),
            'width': getattr(self, 'width_spin', type('obj', (object,), {'value': lambda: 300})()).value(),
            'height': getattr(self, 'height_spin', type('obj', (object,), {'value': lambda: 150})()).value(),
            'snap_to_grid': getattr(self, 'grid_snap_check', type('obj', (object,), {'isChecked': lambda: True})()).isChecked()
        }
        
        # Add content if available
        if hasattr(self, 'content_edit'):
            data['content'] = self.content_edit.toPlainText()
            data['auto_resize'] = getattr(self, 'auto_resize_check', type('obj', (object,), {'isChecked': lambda: True})()).isChecked()
            
        # Add execution-specific properties
        if node_type == "Execution":
            if hasattr(self, 'original_name_edit'):
                data['original_name'] = self.original_name_edit.text().strip()
            if hasattr(self, 'conditional_check'):
                data['is_conditional'] = self.conditional_check.isChecked()
            if hasattr(self, 'has_return_check'):
                data['has_return'] = self.has_return_check.isChecked()
                
        # Add blueprint-specific properties  
        elif node_type == "Blueprint":
            if hasattr(self, 'auto_detect_type_check'):
                data['auto_detect_type'] = self.auto_detect_type_check.isChecked()
                
        # Add buildable-specific properties
        elif node_type == "Buildable":
            if hasattr(self, 'auto_connect_check'):
                data['auto_connect'] = self.auto_connect_check.isChecked()
            if hasattr(self, 'sync_editor_check'):
                data['sync_editor'] = self.sync_editor_check.isChecked()
        
        return data


class QuickNodeCreator:
    """Helper class for quick node creation without dialog."""
    
    @staticmethod
    def create_function_node(name, parameters=None):
        """Quickly create a function node."""
        params = parameters or []
        param_str = ", ".join(params) if params else ""
        
        return {
            'type': 'Blueprint',
            'name': name,
            'content': f"def {name}({param_str}):\\n    pass",
            'auto_resize': True,
            'auto_detect_type': True
        }
        
    @staticmethod
    def create_class_node(name, base_classes=None):
        """Quickly create a class node."""
        bases = base_classes or []
        base_str = f"({', '.join(bases)})" if bases else ""
        
        return {
            'type': 'Blueprint', 
            'name': name,
            'content': f"class {name}{base_str}:\\n    def __init__(self):\\n        pass",
            'auto_resize': True,
            'auto_detect_type': True
        }
        
    @staticmethod
    def create_code_block(name, code):
        """Quickly create a buildable code block."""
        return {
            'type': 'Buildable',
            'name': name,
            'content': code,
            'auto_connect': True,
            'sync_editor': True
        }
        
    @staticmethod
    def create_execution_node(name, original_name=None):
        """Quickly create an execution node."""
        return {
            'type': 'Execution',
            'name': name,
            'original_name': original_name or name,
            'is_conditional': False,
            'has_return': False
        }
