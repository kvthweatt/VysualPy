#!/usr/bin/env python3
"""
Tree operations and group alignment for VysualPy.

This module provides advanced node organization capabilities extracted from
debug_node_system.py, including tree alignment, group operations, and 
intelligent node positioning.
"""

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication
from typing import List, Set, Dict, Any, Optional


class TreeAlignmentEngine:
    """Engine for intelligent tree-based node alignment."""
    
    def __init__(self, scene):
        self.scene = scene
        self.processed_nodes = set()
        
    def align_child_nodes_vertically(self, selected_nodes: List) -> int:
        """Align direct children of selected nodes vertically to the right.
        
        Args:
            selected_nodes: List of nodes to process
            
        Returns:
            Number of nodes that were aligned
        """
        if not selected_nodes:
            print("❌ No nodes selected for child alignment")
            return 0
            
        aligned_count = 0
        
        for parent_node in selected_nodes:
            # Find direct children (nodes connected via output ports)
            children = self._get_direct_children(parent_node)
            
            if not children:
                print(f"ℹ️  Node '{parent_node.name}' has no direct children to align")
                continue
                
            # Sort children by current Y position for consistent ordering
            children.sort(key=lambda child: child.pos().y())
            
            # Calculate alignment position (to the right of parent)
            parent_pos = parent_node.pos()
            parent_width = parent_node.boundingRect().width()
            align_x = parent_pos.x() + parent_width + 100  # 100px spacing
            
            # Calculate vertical spacing
            if len(children) > 1:
                total_height = sum(child.boundingRect().height() for child in children)
                spacing = max(50, total_height / len(children) * 0.3)  # Minimum 50px spacing
            else:
                spacing = 0
            
            # Start Y position (center children around parent's center)
            parent_center_y = parent_pos.y() + parent_node.boundingRect().height() / 2
            total_children_height = (len(children) - 1) * spacing
            start_y = parent_center_y - total_children_height / 2
            
            # Align children vertically
            for i, child in enumerate(children):
                new_y = start_y + (i * spacing)
                child.setPos(align_x, new_y)
                aligned_count += 1
                
            print(f"✅ Aligned {len(children)} children of '{parent_node.name}' vertically")
        
        # Update all connections after moving nodes
        self._update_connections()
        
        if aligned_count > 0:
            print(f"🎯 Child Alignment: Aligned {aligned_count} child nodes vertically")
        else:
            print("ℹ️  No child nodes found to align")
            
        return aligned_count
            
    def align_full_tree(self, selected_nodes: List) -> int:
        """Recursively align entire node tree with intelligent spacing.
        
        Args:
            selected_nodes: Root nodes to start alignment from
            
        Returns:
            Number of nodes that were aligned
        """
        if not selected_nodes:
            print("❌ No nodes selected for tree alignment")
            return 0
            
        aligned_count = 0
        self.processed_nodes = set()
        
        for root_node in selected_nodes:
            if root_node in self.processed_nodes:
                continue
                
            # Perform recursive tree alignment
            aligned_in_tree = self._align_node_tree_recursive(root_node, 0)
            aligned_count += aligned_in_tree
            
        # Update all connections after moving nodes
        self._update_connections()
        
        if aligned_count > 0:
            print(f"🌳 Tree Alignment: Aligned {aligned_count} nodes in full tree structure")
        else:
            print("ℹ️  No tree structure found to align")
            
        return aligned_count
            
    def _align_node_tree_recursive(self, node, depth: int, start_y: Optional[float] = None) -> int:
        """Recursively align a node and all its descendants.
        
        Args:
            node: Node to align
            depth: Current depth in the tree
            start_y: Optional starting Y position
            
        Returns:
            Number of nodes aligned in this subtree
        """
        if node in self.processed_nodes:
            return 0
            
        self.processed_nodes.add(node)
        aligned_count = 0
        
        # Get direct children
        children = self._get_direct_children(node)
        
        if not children:
            return aligned_count  # Leaf node
            
        # Sort children by current Y position for consistent ordering
        children.sort(key=lambda child: child.pos().y())
        
        # Calculate horizontal position based on depth
        node_pos = node.pos()
        node_width = node.boundingRect().width()
        child_x = node_pos.x() + node_width + (120 + depth * 20)  # Increasing spacing per depth
        
        # Calculate vertical positioning
        if start_y is None:
            # For root level, center around the parent
            node_center_y = node_pos.y() + node.boundingRect().height() / 2
        else:
            node_center_y = start_y + node.boundingRect().height() / 2
            
        # Calculate total space needed for all children and their subtrees
        child_heights = []
        for child in children:
            subtree_height = self._calculate_subtree_height(child)
            child_heights.append(max(child.boundingRect().height(), subtree_height))
            
        total_height = sum(child_heights) + (len(children) - 1) * 60  # 60px between child groups
        start_y = node_center_y - total_height / 2
        
        # Position and recursively align children
        current_y = start_y
        for i, child in enumerate(children):
            child.setPos(child_x, current_y)
            aligned_count += 1
            
            # Recursively align the child's subtree
            subtree_aligned = self._align_node_tree_recursive(
                child, depth + 1, current_y
            )
            aligned_count += subtree_aligned
            
            # Move to next child position
            current_y += child_heights[i] + 60
            
        print(f"🌿 Aligned node '{node.name}' with {len(children)} children at depth {depth}")
        return aligned_count
        
    def _calculate_subtree_height(self, node) -> float:
        """Calculate the total height needed for a node's subtree.
        
        Args:
            node: Root node of subtree
            
        Returns:
            Total height required for the subtree
        """
        # Use a temporary set to avoid infinite recursion
        temp_processed = set(self.processed_nodes)
        
        if node in temp_processed:
            return node.boundingRect().height()
            
        temp_processed.add(node)
        children = self._get_direct_children(node)
        
        if not children:
            return node.boundingRect().height()
            
        child_heights = []
        for child in children:
            if child not in temp_processed:
                temp_processed.add(child)
                height = self._calculate_subtree_height_recursive(child, temp_processed)
                child_heights.append(height)
                
        if not child_heights:
            return node.boundingRect().height()
            
        total_children_height = sum(child_heights) + (len(child_heights) - 1) * 60
        return max(node.boundingRect().height(), total_children_height)
        
    def _calculate_subtree_height_recursive(self, node, processed: Set) -> float:
        """Recursive helper for subtree height calculation."""
        if node in processed:
            return node.boundingRect().height()
            
        processed.add(node)
        children = self._get_direct_children(node)
        
        if not children:
            return node.boundingRect().height()
            
        child_heights = []
        for child in children:
            if child not in processed:
                height = self._calculate_subtree_height_recursive(child, processed)
                child_heights.append(height)
                
        if not child_heights:
            return node.boundingRect().height()
            
        total_children_height = sum(child_heights) + (len(child_heights) - 1) * 60
        return max(node.boundingRect().height(), total_children_height)
        
    def _get_direct_children(self, parent_node) -> List:
        """Get all nodes directly connected as children from this node's output ports.
        
        Args:
            parent_node: Parent node to find children for
            
        Returns:
            List of child nodes
        """
        children = []
        
        if not hasattr(self.scene, 'connections'):
            return children
            
        for connection in self.scene.connections:
            if (hasattr(connection, 'start_port') and hasattr(connection, 'end_port') and
                connection.start_port and connection.end_port and
                connection.start_port.node == parent_node):
                # This connection starts from the parent node
                child_node = connection.end_port.node
                if child_node not in children:
                    children.append(child_node)
                    
        return children
        
    def _update_connections(self):
        """Update all connections after node movement."""
        if hasattr(self.scene, 'update_all_connections'):
            self.scene.update_all_connections()


class GroupOperations:
    """Class for group operations on selected nodes."""
    
    def __init__(self, scene):
        self.scene = scene
        
    def align_selected_nodes(self, selected_nodes: List, alignment: str) -> int:
        """Align selected nodes based on alignment type.
        
        Args:
            selected_nodes: List of nodes to align
            alignment: One of 'left', 'right', 'top', 'bottom'
            
        Returns:
            Number of nodes that were aligned
        """
        if len(selected_nodes) < 2:
            print(f"ℹ️  Need at least 2 nodes to align, got {len(selected_nodes)}")
            return 0
            
        # Get reference position (first selected node)
        ref_item = selected_nodes[0]
        ref_pos = ref_item.pos()
        aligned_count = 0
        
        for item in selected_nodes[1:]:
            current_pos = item.pos()
            
            if alignment == "left":
                item.setPos(ref_pos.x(), current_pos.y())
            elif alignment == "right":
                ref_width = ref_item.boundingRect().width()
                item_width = item.boundingRect().width()
                item.setPos(ref_pos.x() + ref_width - item_width, current_pos.y())
            elif alignment == "top":
                item.setPos(current_pos.x(), ref_pos.y())
            elif alignment == "bottom":
                ref_height = ref_item.boundingRect().height()
                item_height = item.boundingRect().height()
                item.setPos(current_pos.x(), ref_pos.y() + ref_height - item_height)
                
            aligned_count += 1
                
        print(f"📐 Aligned {len(selected_nodes)} nodes to {alignment}")
        self._update_connections()
        return aligned_count
        
    def distribute_selected_nodes(self, selected_nodes: List, direction: str) -> int:
        """Distribute selected nodes evenly.
        
        Args:
            selected_nodes: List of nodes to distribute
            direction: Either 'horizontal' or 'vertical'
            
        Returns:
            Number of nodes that were distributed
        """
        if len(selected_nodes) < 3:
            print(f"ℹ️  Need at least 3 nodes to distribute, got {len(selected_nodes)}")
            return 0
            
        # Sort by position
        if direction == "horizontal":
            selected_nodes.sort(key=lambda item: item.pos().x())
        else:
            selected_nodes.sort(key=lambda item: item.pos().y())
            
        # Calculate spacing
        first_item = selected_nodes[0]
        last_item = selected_nodes[-1]
        
        if direction == "horizontal":
            total_distance = last_item.pos().x() - first_item.pos().x()
            spacing = total_distance / (len(selected_nodes) - 1)
            
            for i, item in enumerate(selected_nodes[1:-1], 1):
                new_x = first_item.pos().x() + (spacing * i)
                item.setPos(new_x, item.pos().y())
        else:
            total_distance = last_item.pos().y() - first_item.pos().y()
            spacing = total_distance / (len(selected_nodes) - 1)
            
            for i, item in enumerate(selected_nodes[1:-1], 1):
                new_y = first_item.pos().y() + (spacing * i)
                item.setPos(item.pos().x(), new_y)
                
        print(f"📏 Distributed {len(selected_nodes)} nodes {direction}ly")
        self._update_connections()
        return len(selected_nodes) - 2  # Don't count first and last nodes
        
    def arrange_in_grid(self, selected_nodes: List, columns: int = None) -> int:
        """Arrange selected nodes in a grid layout.
        
        Args:
            selected_nodes: List of nodes to arrange
            columns: Number of columns (auto-calculated if None)
            
        Returns:
            Number of nodes that were arranged
        """
        if not selected_nodes:
            return 0
            
        # Auto-calculate columns if not specified
        if columns is None:
            columns = max(1, int(len(selected_nodes) ** 0.5))
            
        # Calculate grid spacing
        max_width = max(node.boundingRect().width() for node in selected_nodes)
        max_height = max(node.boundingRect().height() for node in selected_nodes)
        
        spacing_x = max_width + 50  # 50px padding
        spacing_y = max_height + 50  # 50px padding
        
        # Find top-left corner based on current selection
        min_x = min(node.pos().x() for node in selected_nodes)
        min_y = min(node.pos().y() for node in selected_nodes)
        
        # Arrange nodes in grid
        for i, node in enumerate(selected_nodes):
            row = i // columns
            col = i % columns
            
            new_x = min_x + (col * spacing_x)
            new_y = min_y + (row * spacing_y)
            
            node.setPos(new_x, new_y)
            
        print(f"🗂️  Arranged {len(selected_nodes)} nodes in {columns}-column grid")
        self._update_connections()
        return len(selected_nodes)
        
    def create_circular_layout(self, selected_nodes: List, radius: float = None) -> int:
        """Arrange selected nodes in a circular pattern.
        
        Args:
            selected_nodes: List of nodes to arrange
            radius: Radius of the circle (auto-calculated if None)
            
        Returns:
            Number of nodes that were arranged
        """
        if not selected_nodes:
            return 0
            
        import math
        
        # Auto-calculate radius if not specified
        if radius is None:
            # Base radius on number of nodes and average node size
            avg_width = sum(node.boundingRect().width() for node in selected_nodes) / len(selected_nodes)
            radius = max(100, (len(selected_nodes) * avg_width) / (2 * math.pi))
            
        # Find center point based on current selection
        center_x = sum(node.pos().x() for node in selected_nodes) / len(selected_nodes)
        center_y = sum(node.pos().y() for node in selected_nodes) / len(selected_nodes)
        
        # Arrange nodes in circle
        for i, node in enumerate(selected_nodes):
            angle = (2 * math.pi * i) / len(selected_nodes)
            
            new_x = center_x + radius * math.cos(angle)
            new_y = center_y + radius * math.sin(angle)
            
            node.setPos(new_x, new_y)
            
        print(f"⭕ Arranged {len(selected_nodes)} nodes in circular layout (radius: {radius:.1f})")
        self._update_connections()
        return len(selected_nodes)
        
    def _update_connections(self):
        """Update all connections after node movement."""
        if hasattr(self.scene, 'update_all_connections'):
            self.scene.update_all_connections()


class KeyboardShortcutHandler:
    """Handler for keyboard shortcuts related to tree operations."""
    
    def __init__(self, scene):
        self.scene = scene
        self.tree_engine = TreeAlignmentEngine(scene)
        self.group_ops = GroupOperations(scene)
        
    def handle_key_event(self, event) -> bool:
        """Handle keyboard events for tree operations.
        
        Args:
            event: QKeyEvent
            
        Returns:
            True if event was handled, False otherwise
        """
        from PyQt5.QtCore import Qt
        
        # Get keyboard modifiers
        modifiers = QApplication.keyboardModifiers()
        
        # CTRL+S - Child Vertical Align
        if (event.key() == Qt.Key_S and 
            modifiers == Qt.ControlModifier):
            selected_nodes = self._get_selected_nodes()
            self.tree_engine.align_child_nodes_vertically(selected_nodes)
            return True
            
        # CTRL+SHIFT+S - Full Tree Align
        if (event.key() == Qt.Key_S and 
            modifiers == (Qt.ControlModifier | Qt.ShiftModifier)):
            selected_nodes = self._get_selected_nodes()
            self.tree_engine.align_full_tree(selected_nodes)
            return True
            
        # CTRL+SHIFT+G - Grid Layout
        if (event.key() == Qt.Key_G and 
            modifiers == (Qt.ControlModifier | Qt.ShiftModifier)):
            selected_nodes = self._get_selected_nodes()
            self.group_ops.arrange_in_grid(selected_nodes)
            return True
            
        # CTRL+SHIFT+C - Circular Layout
        if (event.key() == Qt.Key_C and 
            modifiers == (Qt.ControlModifier | Qt.ShiftModifier)):
            selected_nodes = self._get_selected_nodes()
            self.group_ops.create_circular_layout(selected_nodes)
            return True
            
        return False
        
    def _get_selected_nodes(self) -> List:
        """Get list of currently selected nodes that have node_type attribute."""
        return [item for item in self.scene.selectedItems() 
                if hasattr(item, 'node_type')]


class SmartPositioning:
    """Intelligent node positioning utilities."""
    
    def __init__(self, scene):
        self.scene = scene
        
    def find_optimal_position(self, node_width: float, node_height: float, 
                            reference_node=None, direction: str = "right") -> QPointF:
        """Find optimal position for a new node.
        
        Args:
            node_width: Width of the node to position
            node_height: Height of the node to position
            reference_node: Node to position relative to (if any)
            direction: Direction relative to reference ('right', 'left', 'below', 'above')
            
        Returns:
            Optimal position as QPointF
        """
        if reference_node:
            return self._position_relative_to_node(
                reference_node, node_width, node_height, direction
            )
        else:
            return self._find_empty_space(node_width, node_height)
            
    def _position_relative_to_node(self, reference_node, width: float, height: float, 
                                 direction: str) -> QPointF:
        """Position node relative to reference node."""
        ref_pos = reference_node.pos()
        ref_rect = reference_node.boundingRect()
        margin = 50  # Margin between nodes
        
        if direction == "right":
            x = ref_pos.x() + ref_rect.width() + margin
            y = ref_pos.y()
        elif direction == "left":
            x = ref_pos.x() - width - margin
            y = ref_pos.y()
        elif direction == "below":
            x = ref_pos.x()
            y = ref_pos.y() + ref_rect.height() + margin
        elif direction == "above":
            x = ref_pos.x()
            y = ref_pos.y() - height - margin
        else:
            # Default to right
            x = ref_pos.x() + ref_rect.width() + margin
            y = ref_pos.y()
            
        return QPointF(x, y)
        
    def _find_empty_space(self, width: float, height: float) -> QPointF:
        """Find empty space in the scene for a new node."""
        # Get all existing nodes
        existing_nodes = [item for item in self.scene.items() 
                         if hasattr(item, 'node_type')]
        
        if not existing_nodes:
            # No existing nodes, place at origin with some offset
            return QPointF(100, 100)
            
        # Find bounding box of all existing nodes
        min_x = min(node.pos().x() for node in existing_nodes)
        max_x = max(node.pos().x() + node.boundingRect().width() for node in existing_nodes)
        min_y = min(node.pos().y() for node in existing_nodes)
        max_y = max(node.pos().y() + node.boundingRect().height() for node in existing_nodes)
        
        # Try to place to the right of existing nodes
        candidate_x = max_x + 100
        candidate_y = min_y
        
        # Check if this position is clear
        candidate_pos = QPointF(candidate_x, candidate_y)
        if self._is_position_clear(candidate_pos, width, height, existing_nodes):
            return candidate_pos
            
        # If not clear, try below existing nodes
        candidate_x = min_x
        candidate_y = max_y + 100
        candidate_pos = QPointF(candidate_x, candidate_y)
        
        return candidate_pos
        
    def _is_position_clear(self, pos: QPointF, width: float, height: float, 
                          existing_nodes: List) -> bool:
        """Check if a position is clear of existing nodes."""
        from PyQt5.QtCore import QRectF
        
        # Create rectangle for the proposed position
        proposed_rect = QRectF(pos.x(), pos.y(), width, height)
        margin = 20  # Minimum margin between nodes
        
        for node in existing_nodes:
            node_rect = QRectF(
                node.pos().x() - margin,
                node.pos().y() - margin,
                node.boundingRect().width() + 2 * margin,
                node.boundingRect().height() + 2 * margin
            )
            
            if proposed_rect.intersects(node_rect):
                return False
                
        return True
