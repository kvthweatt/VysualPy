#!/usr/bin/env python3
"""
Debug script to test multi-selection functionality with new node system.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor

# Import the new node classes and blueprint system
from vpy_node_types import BlueprintNode, ExecutionNode
from vpy_blueprints import BlueprintScene, BlueprintView

class MultiSelectDebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Selection Debug Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add instructions
        instructions = QLabel(
            "Instructions:\n" +
            "• Drag in empty space to rubber band select multiple nodes\n" +
            "• Ctrl+Click to add/remove nodes from selection\n" +
            "• Try dragging multiple selected nodes together\n" +
            "• Alt+Drag to pan view, Ctrl+Wheel to zoom"
        )
        instructions.setStyleSheet(
            "color: white; background-color: #34495e; padding: 12px; " +
            "font-size: 11px; border: 1px solid #5a6c7d; margin: 5px;"
        )
        layout.addWidget(instructions)
        
        # Create scene and view using the blueprint classes
        self.scene = BlueprintScene()
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        
        self.view = BlueprintView(self.scene)
        layout.addWidget(self.view)
        
        # Create test nodes
        self.create_test_nodes()
        
    def create_test_nodes(self):
        print("Creating test nodes for multi-selection testing...")
        
        nodes = []
        
        # Row 1 - Blueprint nodes
        for i in range(4):
            node = BlueprintNode(
                name=f"Blueprint {i+1}",
                content=f"def function_{i+1}():\n    print('Function {i+1}')\n    return {i+1}"
            )
            node.setPos(i*220, 0)
            nodes.append(node)
            self.scene.addItem(node)
            
        # Row 2 - Execution nodes  
        for i in range(4):
            node = ExecutionNode(
                name=f"function_{i+1}", 
                original_name=f"Execution {i+1}"
            )
            node.setPos(i*220, 180)
            nodes.append(node)
            self.scene.addItem(node)
            
        # Row 3 - Mixed smaller nodes
        for i in range(3):
            if i % 2 == 0:
                node = BlueprintNode(
                    name=f"Small Blueprint {i+1}",
                    content=f"x = {i+1}"
                )
            else:
                node = ExecutionNode(
                    name=f"print_{i+1}",
                    original_name=f"Small Execution {i+1}"
                )
            node.setPos(i*220 + 110, 360)
            nodes.append(node)
            self.scene.addItem(node)
            
        print(f"Created {len(nodes)} test nodes")
        
        # Debug info about selection capabilities
        print(f"Scene items: {len(self.scene.items())}")
        for i, item in enumerate(self.scene.items()):
            print(f"  {i+1}. {type(item).__name__}")
            print(f"     boundingRect: {item.boundingRect()}")
            print(f"     isVisible: {item.isVisible()}")
            print(f"     isSelectable: {bool(item.flags() & item.ItemIsSelectable)}")
            print(f"     isMovable: {bool(item.flags() & item.ItemIsMovable)}")
            
def main():
    app = QApplication(sys.argv)
    window = MultiSelectDebugWindow()
    window.show()
    
    print("\nMulti-selection debug window shown. Test the following:")
    print("  1. Drag in empty space to rubber band select multiple nodes")
    print("  2. Ctrl+Click to add/remove individual nodes from selection")
    print("  3. Try dragging multiple selected nodes together")
    print("  4. Check if all selected nodes move together when dragging")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
