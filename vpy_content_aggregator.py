#!/usr/bin/env python3
"""
Node Content Aggregator - Loosely coupled architecture for aggregating BuildableNode content.

This module provides a NodeContentAggregator class that can collect and organize content
from BuildableNodes in a scene or from a list of nodes, then notify subscribers through
signals and callback mechanisms when content changes.

The aggregator is designed to be independent from UI components, allowing multiple editors
or views to subscribe to its updates.
"""

import re
import ast
from typing import List, Dict, Set, Optional, Callable, Any, Tuple
from collections import defaultdict, deque
from PyQt5.QtCore import QObject, pyqtSignal


class CodeElement:
    """Represents a code element (function, class, import, variable) from a BuildableNode."""
    
    def __init__(self, name: str, element_type: str, content: str, 
                 node_id: str, line_start: int, dependencies: Set[str] = None):
        self.name = name
        self.element_type = element_type  # 'import', 'class', 'function', 'variable', 'other'
        self.content = content
        self.node_id = node_id
        self.line_start = line_start
        self.dependencies = dependencies or set()
        self.line_end = line_start + len(content.split('\n')) - 1
        
    def __repr__(self):
        return f"CodeElement({self.name}, {self.element_type}, node={self.node_id})"


class NodeContentAggregator(QObject):
    """
    Aggregates content from BuildableNodes and notifies subscribers of changes.
    
    This class is designed to be independent from UI components and can work with
    either a scene containing BuildableNodes or a direct list of nodes.
    
    Signals:
        contentUpdated: Emitted when aggregated content changes
        nodeAdded: Emitted when a node is added to tracking
        nodeRemoved: Emitted when a node is removed from tracking
    """
    
    # Signals for content changes
    contentUpdated = pyqtSignal(str, dict)  # (aggregated_content, line_mapping)
    nodeAdded = pyqtSignal(object)  # (node)
    nodeRemoved = pyqtSignal(object)  # (node)
    
    def __init__(self, scene=None, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.nodes = []  # List of BuildableNodes
        self.code_elements = []  # List of CodeElement objects
        self.aggregated_content = ""
        self.line_to_node_mapping = {}  # Maps line numbers to (node_id, original_line)
        self.node_to_elements = defaultdict(list)  # Maps node_id to CodeElements
        self._last_refresh_hash = None
        self.callbacks = []  # List of callback functions
        self.include_comments = True
        self.last_content = ""
    
    def add_callback(self, callback: Callable[[str, Dict], None]):
        """
        Add a callback function that will be called when content updates.
        
        Args:
            callback: Function that takes (content: str, line_mapping: Dict) as parameters
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str, Dict], None]):
        """Remove a callback function from the update notifications."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def set_include_comments(self, include_comments: bool):
        """Set whether to include comment nodes in the aggregation."""
        if self.include_comments != include_comments:
            self.include_comments = include_comments
            self.refresh_content()
    
    def add_node(self, node):
        """Add a BuildableNode to be tracked by this aggregator."""
        if node not in self.nodes:
            self.nodes.append(node)
            self.nodeAdded.emit(node)
            self.refresh_content()
    
    def remove_node(self, node):
        """Remove a BuildableNode from tracking."""
        if node in self.nodes:
            self.nodes.remove(node)
            self.nodeRemoved.emit(node)
            self.refresh_content()
    
    def set_nodes_from_scene(self, scene):
        """
        Set tracked nodes by scanning a scene for BuildableNodes.
        
        Args:
            scene: Qt scene object containing BuildableNode items
        """
        # Clear current tracking
        self.nodes.clear()
        
        # Find all BuildableNodes in the scene
        if hasattr(scene, 'items'):
            for item in scene.items():
                if self._is_buildable_node(item):
                    self.nodes.append(item)
        
        self.refresh_content()
    
    def set_nodes_from_list(self, nodes: List):
        """
        Set tracked nodes from a direct list.
        
        Args:
            nodes: List of BuildableNode objects
        """
        self.nodes = list(nodes)  # Create a copy
        self.refresh_content()
    
    def _is_buildable_node(self, item) -> bool:
        """Check if an item is a BuildableNode."""
        return (hasattr(item, 'node_type') and 
                hasattr(item.node_type, 'value') and 
                item.node_type.value == 'buildable')
    
    def refresh_content(self):
        """Refresh the aggregated content and notify all subscribers."""
        old_content = self.aggregated_content
        
        # Generate new content
        self.refresh(force=True)
        
        # Check if content actually changed
        if self.aggregated_content != old_content:
            self.last_content = self.aggregated_content
            
            # Emit signal
            self.contentUpdated.emit(self.aggregated_content, self.line_to_node_mapping)
            
            # Call all registered callbacks
            for callback in self.callbacks:
                try:
                    callback(self.aggregated_content, self.line_to_node_mapping)
                except Exception as e:
                    print(f"Error in content update callback: {e}")
        
    def set_scene(self, scene):
        """Set the scene to aggregate content from."""
        self.scene = scene
        
    def find_buildable_nodes(self) -> List:
        """Find all BuildableNodes in the current scene."""
        if not self.scene:
            return []
            
        nodes = []
        for item in self.scene.items():
            if (hasattr(item, 'node_type') and 
                hasattr(item.node_type, 'value') and 
                item.node_type.value == 'buildable'):
                nodes.append(item)
                
        return nodes
        
    def refresh(self, force: bool = False) -> bool:
        """
        Refresh the aggregated content from all buildable nodes.
        
        Args:
            force: Force refresh even if content hasn't changed
            
        Returns:
            True if content was updated, False if no changes
        """
        current_nodes = self.find_buildable_nodes()
        
        # Create a hash of current content to detect changes
        content_hash = self._calculate_content_hash(current_nodes)
        
        if not force and content_hash == self._last_refresh_hash:
            return False  # No changes detected
            
        self.nodes = current_nodes
        self.code_elements = []
        self.node_to_elements.clear()
        self._last_refresh_hash = content_hash
        
        # Parse content from each node
        for node in self.nodes:
            self._parse_node_content(node)
            
        # Generate organized content
        self._generate_aggregated_content()
        
        return True
        
    def _calculate_content_hash(self, nodes: List) -> str:
        """Calculate a hash representing the current state of all nodes."""
        import hashlib
        
        content_parts = []
        for node in sorted(nodes, key=lambda n: getattr(n, 'name', '')):
            content = getattr(node, 'content', '') or getattr(node, 'full_content', '')
            node_id = str(id(node))
            content_parts.append(f"{node_id}:{content}")
            
        combined = "|".join(content_parts)
        return hashlib.md5(combined.encode()).hexdigest()
        
    def _parse_node_content(self, node):
        """Parse content from a single BuildableNode into CodeElements."""
        content = getattr(node, 'content', '') or getattr(node, 'full_content', '')
        if not content.strip():
            return
            
        node_id = str(id(node))
        
        try:
            # Parse the content as Python AST
            tree = ast.parse(content)
            
            for node_ast in ast.walk(tree):
                element = self._create_code_element_from_ast(node_ast, content, node_id)
                if element:
                    self.code_elements.append(element)
                    self.node_to_elements[node_id].append(element)
                    
        except SyntaxError:
            # Handle invalid Python - treat as a single "other" element
            element = CodeElement(
                name=f"code_block_{len(self.code_elements)}",
                element_type="other",
                content=content,
                node_id=node_id,
                line_start=1
            )
            self.code_elements.append(element)
            self.node_to_elements[node_id].append(element)
            
    def _create_code_element_from_ast(self, node_ast, full_content: str, node_id: str) -> Optional[CodeElement]:
        """Create a CodeElement from an AST node."""
        if isinstance(node_ast, ast.Import):
            # Handle import statements
            import_names = [alias.name for alias in node_ast.names]
            line_start = node_ast.lineno
            line_end = getattr(node_ast, 'end_lineno', line_start)
            content_lines = full_content.split('\n')
            content = '\n'.join(content_lines[line_start-1:line_end])
            
            return CodeElement(
                name=f"import_{import_names[0]}",
                element_type="import",
                content=content,
                node_id=node_id,
                line_start=line_start
            )
            
        elif isinstance(node_ast, ast.ImportFrom):
            # Handle from ... import statements
            module = node_ast.module or ""
            line_start = node_ast.lineno
            line_end = getattr(node_ast, 'end_lineno', line_start)
            content_lines = full_content.split('\n')
            content = '\n'.join(content_lines[line_start-1:line_end])
            
            return CodeElement(
                name=f"from_{module}",
                element_type="import",
                content=content,
                node_id=node_id,
                line_start=line_start
            )
            
        elif isinstance(node_ast, ast.FunctionDef):
            # Handle function definitions
            dependencies = self._extract_dependencies_from_function(node_ast)
            line_start = node_ast.lineno
            line_end = getattr(node_ast, 'end_lineno', line_start)
            content_lines = full_content.split('\n')
            content = '\n'.join(content_lines[line_start-1:line_end])
            
            return CodeElement(
                name=node_ast.name,
                element_type="function",
                content=content,
                node_id=node_id,
                line_start=line_start,
                dependencies=dependencies
            )
            
        elif isinstance(node_ast, ast.AsyncFunctionDef):
            # Handle async function definitions
            dependencies = self._extract_dependencies_from_function(node_ast)
            line_start = node_ast.lineno
            line_end = getattr(node_ast, 'end_lineno', line_start)
            content_lines = full_content.split('\n')
            content = '\n'.join(content_lines[line_start-1:line_end])
            
            return CodeElement(
                name=node_ast.name,
                element_type="function",
                content=content,
                node_id=node_id,
                line_start=line_start,
                dependencies=dependencies
            )
            
        elif isinstance(node_ast, ast.ClassDef):
            # Handle class definitions
            dependencies = self._extract_dependencies_from_class(node_ast)
            line_start = node_ast.lineno
            line_end = getattr(node_ast, 'end_lineno', line_start)
            content_lines = full_content.split('\n')
            content = '\n'.join(content_lines[line_start-1:line_end])
            
            return CodeElement(
                name=node_ast.name,
                element_type="class",
                content=content,
                node_id=node_id,
                line_start=line_start,
                dependencies=dependencies
            )
            
        elif isinstance(node_ast, ast.Assign):
            # Handle variable assignments at module level
            if hasattr(node_ast, 'lineno') and len(node_ast.targets) == 1:
                target = node_ast.targets[0]
                if isinstance(target, ast.Name):
                    dependencies = self._extract_dependencies_from_expr(node_ast.value)
                    line_start = node_ast.lineno
                    line_end = getattr(node_ast, 'end_lineno', line_start)
                    content_lines = full_content.split('\n')
                    content = '\n'.join(content_lines[line_start-1:line_end])
                    
                    return CodeElement(
                        name=target.id,
                        element_type="variable",
                        content=content,
                        node_id=node_id,
                        line_start=line_start,
                        dependencies=dependencies
                    )
                    
        return None
        
    def _extract_dependencies_from_function(self, func_node) -> Set[str]:
        """Extract function/class names that this function depends on."""
        dependencies = set()
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # This is a name being read/called
                dependencies.add(node.id)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    dependencies.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        dependencies.add(node.func.value.id)
                        
        # Remove built-in names and keywords
        builtin_names = {
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed',
            'min', 'max', 'sum', 'abs', 'round', 'isinstance', 'hasattr', 'getattr',
            'setattr', 'None', 'True', 'False', 'self', 'cls'
        }
        
        return dependencies - builtin_names
        
    def _extract_dependencies_from_class(self, class_node) -> Set[str]:
        """Extract dependencies for a class definition."""
        dependencies = set()
        
        # Check base classes
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                dependencies.add(base.id)
                
        # Check decorators
        for decorator in class_node.decorator_list:
            if isinstance(decorator, ast.Name):
                dependencies.add(decorator.id)
                
        return dependencies
        
    def _extract_dependencies_from_expr(self, expr_node) -> Set[str]:
        """Extract dependencies from an expression."""
        dependencies = set()
        
        for node in ast.walk(expr_node):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                dependencies.add(node.id)
                
        builtin_names = {
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed',
            'min', 'max', 'sum', 'abs', 'round', 'isinstance', 'hasattr', 'getattr',
            'setattr', 'None', 'True', 'False'
        }
        
        return dependencies - builtin_names
        
    def _generate_aggregated_content(self):
        """Generate the final aggregated content with proper ordering."""
        # Separate elements by type
        imports = [e for e in self.code_elements if e.element_type == 'import']
        classes = [e for e in self.code_elements if e.element_type == 'class']
        functions = [e for e in self.code_elements if e.element_type == 'function']
        variables = [e for e in self.code_elements if e.element_type == 'variable']
        others = [e for e in self.code_elements if e.element_type == 'other']
        
        # Sort each category
        ordered_imports = self._deduplicate_imports(imports)
        ordered_classes = self._topological_sort_elements(classes)
        ordered_functions = self._topological_sort_elements(functions)
        ordered_variables = self._dependency_sort_variables(variables)
        
        # Build the final content
        content_parts = []
        current_line = 1
        self.line_to_node_mapping.clear()
        
        # Add imports first
        if ordered_imports:
            for element in ordered_imports:
                self._add_element_to_content(element, content_parts, current_line)
                current_line += len(element.content.split('\n'))
            content_parts.append("")  # Empty line after imports
            current_line += 1
            
        # Add variables
        if ordered_variables:
            for element in ordered_variables:
                self._add_element_to_content(element, content_parts, current_line)
                current_line += len(element.content.split('\n'))
            content_parts.append("")  # Empty line after variables
            current_line += 1
            
        # Add classes
        if ordered_classes:
            for element in ordered_classes:
                self._add_element_to_content(element, content_parts, current_line)
                current_line += len(element.content.split('\n'))
                content_parts.append("")  # Empty line after each class
                current_line += 1
                
        # Add functions
        if ordered_functions:
            for element in ordered_functions:
                self._add_element_to_content(element, content_parts, current_line)
                current_line += len(element.content.split('\n'))
                content_parts.append("")  # Empty line after each function
                current_line += 1
                
        # Add other code blocks
        if others:
            content_parts.append("# Other code blocks")
            current_line += 1
            for element in others:
                self._add_element_to_content(element, content_parts, current_line)
                current_line += len(element.content.split('\n'))
                content_parts.append("")  # Empty line after each block
                current_line += 1
                
        self.aggregated_content = '\n'.join(content_parts).rstrip() + '\n'
        
    def _add_element_to_content(self, element: CodeElement, content_parts: List[str], current_line: int):
        """Add a code element to the content and update line mappings."""
        # Add a comment indicating which node this came from
        if hasattr(self, '_show_node_comments') and self._show_node_comments:
            node_name = self._get_node_name_by_id(element.node_id)
            content_parts.append(f"# From node: {node_name}")
            current_line += 1
            
        # Add the actual content
        content_parts.append(element.content)
        
        # Update line mappings
        lines_in_element = element.content.split('\n')
        for i, _ in enumerate(lines_in_element):
            self.line_to_node_mapping[current_line + i] = (element.node_id, element.line_start + i)
            
    def _get_node_name_by_id(self, node_id: str) -> str:
        """Get the display name of a node by its ID."""
        for node in self.nodes:
            if str(id(node)) == node_id:
                return getattr(node, 'name', 'Unknown')
        return 'Unknown'
        
    def _deduplicate_imports(self, imports: List[CodeElement]) -> List[CodeElement]:
        """Remove duplicate import statements."""
        seen_imports = set()
        unique_imports = []
        
        for import_elem in imports:
            # Normalize the import statement for comparison
            normalized = import_elem.content.strip()
            if normalized not in seen_imports:
                seen_imports.add(normalized)
                unique_imports.append(import_elem)
                
        return unique_imports
        
    def _topological_sort_elements(self, elements: List[CodeElement]) -> List[CodeElement]:
        """Topologically sort elements based on their dependencies."""
        # Create a dependency graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        element_by_name = {elem.name: elem for elem in elements}
        
        # Initialize in-degree for all elements
        for elem in elements:
            in_degree[elem.name] = 0
            
        # Build the graph
        for elem in elements:
            for dep in elem.dependencies:
                if dep in element_by_name:
                    graph[dep].append(elem.name)
                    in_degree[elem.name] += 1
                    
        # Perform topological sort using Kahn's algorithm
        queue = deque([name for name in in_degree if in_degree[name] == 0])
        sorted_names = []
        
        while queue:
            current = queue.popleft()
            sorted_names.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        # If we couldn't sort everything, there's a circular dependency
        if len(sorted_names) != len(elements):
            print(f"Warning: Circular dependency detected in {len(elements) - len(sorted_names)} elements")
            # Add remaining elements at the end
            for elem in elements:
                if elem.name not in sorted_names:
                    sorted_names.append(elem.name)
                    
        return [element_by_name[name] for name in sorted_names if name in element_by_name]
        
    def _dependency_sort_variables(self, variables: List[CodeElement]) -> List[CodeElement]:
        """Sort variables so that dependencies come first."""
        return self._topological_sort_elements(variables)
        
    def get_aggregated_content(self) -> str:
        """Get the current aggregated content."""
        return self.aggregated_content
        
    def get_node_by_line(self, line_number: int) -> Tuple[Optional[str], Optional[int]]:
        """
        Get the original node and line number for a line in the aggregated content.
        
        Returns:
            Tuple of (node_id, original_line_number) or (None, None) if not found
        """
        return self.line_to_node_mapping.get(line_number, (None, None))
        
    def get_elements_for_node(self, node_id: str) -> List[CodeElement]:
        """Get all code elements that belong to a specific node."""
        return self.node_to_elements.get(node_id, [])
        
    def enable_node_comments(self, enabled: bool = True):
        """Enable or disable node origin comments in the aggregated content."""
        self._show_node_comments = enabled
    
    def get_current_content(self) -> str:
        """Get the current aggregated content."""
        return self.aggregated_content
    
    def get_line_mapping(self) -> Dict:
        """Get the current line mapping."""
        return self.line_to_node_mapping.copy()
    
    def get_tracked_nodes(self) -> List:
        """Get a copy of the currently tracked nodes."""
        return self.nodes.copy()
    
    def get_node_at_line(self, line_number: int) -> Optional[object]:
        """Get the node that corresponds to a specific line in the aggregated content."""
        mapping = self.line_to_node_mapping.get(line_number, {})
        if isinstance(mapping, tuple):
            # Old format: (node_id, original_line)
            node_id = mapping[0]
        else:
            # New format: dict with node_id key
            node_id = mapping.get('node_id')
        
        if node_id and node_id != 'aggregator':
            # Find the actual node object
            for node in self.nodes:
                if str(id(node)) == node_id:
                    return node
        
        return None
    
    def sync_changes_to_node(self, line_number: int, new_content: str) -> bool:
        """
        Sync changes from the aggregated content back to the original node.
        
        Args:
            line_number: Line number in the aggregated content
            new_content: New content for that line
            
        Returns:
            bool: True if sync was successful, False otherwise
        """
        node = self.get_node_at_line(line_number)
        if not node:
            return False
        
        mapping = self.line_to_node_mapping.get(line_number, {})
        if isinstance(mapping, tuple):
            # Old format: (node_id, original_line)
            original_line = mapping[1]
        else:
            # New format: dict
            original_line = mapping.get('original_line', 0)
        
        if original_line > 0:
            # Update the specific line in the node's content
            node_content = getattr(node, 'content', '') or getattr(node, 'full_content', '')
            lines = node_content.split('\n')
            
            if 1 <= original_line <= len(lines):
                lines[original_line - 1] = new_content
                updated_content = '\n'.join(lines)
                
                # Update node content
                if hasattr(node, 'content'):
                    node.content = updated_content
                if hasattr(node, 'full_content'):
                    node.full_content = updated_content
                
                # Process content change if supported
                if hasattr(node, 'process_content_change'):
                    node.process_content_change(node_content, updated_content)
                
                # Update visual representation
                if hasattr(node, 'update'):
                    node.update()
                
                return True
        
        return False


class GlobalNodeTextEditor(QObject):
    """
    Lightweight text editor controller that subscribes to NodeContentAggregator updates.
    
    This class acts as a bridge between the aggregator and actual UI editors,
    providing a clean separation of concerns.
    """
    
    def __init__(self, aggregator: NodeContentAggregator, title="Global Nodes"):
        super().__init__()
        self.aggregator = aggregator
        self.title = title
        self.editors = []  # List of UI editor instances
        
        # Connect to aggregator signals
        self.aggregator.contentUpdated.connect(self._on_content_updated)
        self.aggregator.nodeAdded.connect(self._on_node_added)
        self.aggregator.nodeRemoved.connect(self._on_node_removed)
    
    def add_editor(self, editor):
        """Add a UI editor to receive updates."""
        if editor not in self.editors:
            self.editors.append(editor)
            # Initialize with current content
            content = self.aggregator.get_current_content()
            if content and hasattr(editor, 'set_content'):
                editor.set_content(content)
    
    def remove_editor(self, editor):
        """Remove a UI editor from updates."""
        if editor in self.editors:
            self.editors.remove(editor)
    
    def request_refresh(self):
        """Request a content refresh from the aggregator."""
        self.aggregator.refresh_content()
    
    def _on_content_updated(self, content: str, line_mapping: Dict):
        """Handle content updates from the aggregator."""
        # Update all registered editors
        for editor in self.editors[:]:  # Create copy to avoid modification during iteration
            try:
                if hasattr(editor, 'set_content'):
                    editor.set_content(content)
                elif hasattr(editor, 'setPlainText'):
                    editor.setPlainText(content)
            except Exception as e:
                print(f"Error updating editor: {e}")
                # Remove problematic editor
                self.editors.remove(editor)
    
    def _on_node_added(self, node):
        """Handle node addition notifications."""
        # Could be used for UI updates, status notifications, etc.
        pass
    
    def _on_node_removed(self, node):
        """Handle node removal notifications."""
        # Could be used for UI updates, status notifications, etc.
        pass
    
    def sync_editor_changes(self, editor, line_number: int, new_content: str):
        """
        Sync changes from an editor back to the source nodes.
        
        Args:
            editor: The UI editor that made the change
            line_number: Line number in the aggregated content
            new_content: New content for that line
        """
        return self.aggregator.sync_changes_to_node(line_number, new_content)
