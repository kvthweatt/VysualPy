#!/usr/bin/env python3
"""
Debug script to test node rendering in isolation.
"""

import sys
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QColor

# Import our new node classes
from vpy_node_types import BlueprintNode, ExecutionNode

class DebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Debug Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create graphics scene and view
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-400, -300, 800, 600)
        
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        
        self.setCentralWidget(central_widget)
        
        # Test node creation
        self.create_test_nodes()
        
    def create_test_nodes(self):
        print("Creating test nodes...")
        
        try:
            # Create BlueprintNode
            blueprint_node = BlueprintNode(
                name="Test Blueprint",
                content="def test_function():\n    return 'Hello World'"
            )
            blueprint_node.setPos(0, 0)
            self.scene.addItem(blueprint_node)
            print(f"Created BlueprintNode: {blueprint_node}")
            print(f"BlueprintNode rect: {blueprint_node.rect()}")
            print(f"BlueprintNode pos: {blueprint_node.pos()}")
            
            # Create ExecutionNode
            execution_node = ExecutionNode(name="Test Execution")
            execution_node.setPos(250, 0)
            self.scene.addItem(execution_node)
            print(f"Created ExecutionNode: {execution_node}")
            print(f"ExecutionNode rect: {execution_node.rect()}")
            print(f"ExecutionNode pos: {execution_node.pos()}")
            
            # Test if nodes are in scene
            scene_items = self.scene.items()
            print(f"Scene items: {len(scene_items)}")
            for item in scene_items:
                print(f"  - {type(item).__name__}: {item}")
                print(f"    boundingRect: {item.boundingRect()}")
                print(f"    isVisible: {item.isVisible()}")
                
        except Exception as e:
            print(f"Error creating nodes: {e}")
            import traceback
            traceback.print_exc()

def main():
    app = QApplication(sys.argv)
    window = DebugWindow()
    window.show()
    
    print("Debug window shown. Check if nodes are visible.")
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
