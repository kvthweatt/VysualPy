# VysualPy Refactoring Architecture

## Overview

This document outlines the refactored architecture for VysualPy's node graph system, designed to eliminate code duplication, improve maintainability, and enable extensible functionality.

## Current Issues

### Code Duplication
- `DraggableRect`, `ExecutionDraggableRect`, `BuildableNode` share 60-70% similar functionality
- Connection handling logic replicated across node types
- Scene management code duplicated in multiple graph classes

### Tight Coupling
- Nodes directly manage their rendering, interaction, and business logic
- Scene classes handle both UI and business logic concerns
- Direct dependencies between unrelated components

### Missing Abstractions
- No common interface for node types
- Connection system lacks validation and extensibility
- Utility functions scattered throughout codebase

## Proposed Architecture

### Core Principles
1. **Separation of Concerns**: Separate rendering, interaction, and business logic
2. **Composition over Inheritance**: Use mixins for shared functionality
3. **Dependency Injection**: Reduce hard-coded dependencies
4. **Backward Compatibility**: Maintain existing APIs during transition

### Node Hierarchy

```
BaseNode (abstract)
├── properties: id, position, size, ports, connections
├── methods: serialize(), deserialize(), validate()
└── hooks: on_connect(), on_disconnect(), on_update()

ExecutionNode (BaseNode + RenderMixin + InteractionMixin)
├── specialized for execution flow visualization
├── connection dimming logic
└── execution path highlighting

BuildableNode (BaseNode + RenderMixin + InteractionMixin + EditableMixin)
├── specialized for live code editing
├── content analysis and AST integration
└── real-time sync with editor

BlueprintNode (BaseNode + RenderMixin + InteractionMixin)
├── specialized for structural representation
├── class/function metadata display
└── code structure visualization
```

### Mixin System

#### RenderMixin
```python
class RenderMixin:
    """Handles QGraphicsItem rendering concerns"""
    def paint(self, painter, option, widget)
    def boundingRect(self)
    def shape(self)
    def update_visual_style(self)
```

#### InteractionMixin
```python
class InteractionMixin:
    """Handles user interaction events"""
    def mousePressEvent(self, event)
    def mouseMoveEvent(self, event)
    def contextMenuEvent(self, event)
    def keyPressEvent(self, event)
```

#### EditableMixin
```python
class EditableMixin:
    """Handles in-place editing functionality"""
    def startEditing(self)
    def stopEditing(self)
    def commitEdit(self)
    def cancelEdit(self)
```

### Connection System

```
Connection (base)
├── validation logic
├── style management
└── event callbacks

ConnectionManager
├── creates/destroys connections
├── validates connection compatibility
├── manages connection persistence
└── broadcasts connection events

ConnectionPoint
├── input/output port abstraction
├── type checking
└── visual feedback
```

### Scene Architecture

```
BaseScene (QGraphicsScene)
├── common scene management
├── node factory methods
└── connection management

BlueprintScene (BaseScene)
├── blueprint-specific behavior
└── code structure parsing

ExecutionScene (BaseScene)
├── execution-specific behavior
└── flow analysis

BuildGraphScene (BaseScene)
├── live editing behavior
└── AST integration
```

### File Structure (Flat Organization)

```
# Core node system
vpy_node_base.py         # BaseNode abstract class and core interfaces
vpy_node_mixins.py       # RenderMixin, InteractionMixin, EditableMixin
vpy_node_types.py        # ExecutionNode, BuildableNode, BlueprintNode implementations
vpy_node_registry.py     # Node type registry and factory

# Connection system
vpy_connection_core.py   # Enhanced Connection and ConnectionPoint classes
vpy_connection_manager.py # ConnectionManager and validation logic

# Scene system
vpy_scene_base.py        # BaseScene with common functionality
vpy_scenes_refactored.py # Refactored Blueprint/Execution/BuildGraph scenes

# Utilities
vpy_ast_tools.py         # AST parsing utilities (extracted from blueprints)
vpy_serialization.py     # Save/load helpers
vpy_validation.py        # General validation utilities

# Legacy compatibility
vpy_legacy_compat.py     # Backward compatibility wrappers with deprecation warnings

# Existing files (to be gradually refactored)
vpy_graph.py             # Current node classes (will become thin wrappers)
vpy_blueprints.py        # Current scene classes (will be split and refactored)
vpy_connection.py        # Current connection system (will be enhanced)
```

## Migration Strategy

### Phase 1: Create Foundation
1. Implement BaseNode abstract class
2. Create mixin interfaces
3. Implement new Connection system
4. Add utility modules

### Phase 2: Migrate Node Types
1. Implement ExecutionNode using new architecture
2. Implement BuildableNode using new architecture
3. Implement BlueprintNode using new architecture
4. Create compatibility wrappers for old classes

### Phase 3: Update Scene Classes
1. Refactor scene classes to use new nodes
2. Remove duplicated logic
3. Update scene-specific behaviors

### Phase 4: File Reorganization
1. Move code to new folder structure
2. Add backward compatibility imports
3. Update all internal references

### Phase 5: Testing & Documentation
1. Comprehensive test coverage
2. Update documentation
3. Migration guide for external users

## API Compatibility

### Deprecated APIs (with warnings)
```python
# Old way (deprecated)
from vpy_graph import DraggableRect

# New way (recommended)
from nodes import BlueprintNode
```

### Compatibility Layer
Provide thin wrappers that maintain old interfaces while using new implementations internally.

## Benefits

1. **Reduced Code Duplication**: Common functionality shared through mixins
2. **Better Testability**: Separated concerns enable isolated unit testing
3. **Extensibility**: New node types can be created by composing mixins
4. **Maintainability**: Clear separation of responsibilities
5. **Performance**: More efficient rendering and interaction handling

## Implementation Notes

- Use Abstract Base Classes to enforce interfaces
- Employ type hints throughout for better IDE support
- Implement comprehensive logging for debugging
- Add configuration system for customizable behavior
- Consider plugin architecture for future extensions

## Testing Strategy

- Unit tests for each mixin and base class
- Integration tests for node interactions
- Performance tests for large graphs
- Backward compatibility tests
- GUI tests using PyQt5's QTest framework
