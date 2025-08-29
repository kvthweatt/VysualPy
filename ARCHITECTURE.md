# VysualPy Refactoring Architecture

## Overview

This document outlines the refactored architecture for VysualPy's node graph system, designed to eliminate code duplication, improve maintainability, and enable extensible functionality.

## Implementation Progress

### ✅ Completed Components

#### Foundation Layer (Phase 1)
- ✅ **BaseNode**: Abstract base class implemented in `vpy_node_base.py`
- ✅ **Mixin System**: RenderMixin, InteractionMixin, EditableMixin in `vpy_node_mixins.py`
- ✅ **Connection System**: Enhanced Connection and ConnectionManager in `vpy_connection_core.py`
- ✅ **Node Types**: BlueprintNode, ExecutionNode, BuildableNode in `vpy_node_types.py`

#### Blueprint System Migration (Phase 2)
- ✅ **BlueprintNode Integration**: Fully migrated from DraggableRect
- ✅ **ExecutionNode Integration**: Fully migrated from ExecutionDraggableRect
- ✅ **Scene Updates**: BlueprintScene and ExecutionScene updated for new architecture
- ✅ **Serialization**: Save/load methods updated for new node types
- ✅ **Grid System**: Updated to work with unified node architecture

### 🚧 In Progress

#### Visual System Integration
- ⚠️ **Node Rendering**: Nodes not yet visible (comment boxes working indicates partial success)
- 🔄 **Connection Ports**: May need updates for proper visual connection handling
- 🔄 **Event Handling**: Some interaction events may need refinement

### 📋 Remaining Issues

#### Legacy Code Duplication (Reduced)
- ⚠️ Some connection handling logic still replicated
- ⚠️ Scene management could be further consolidated

#### Integration Points
- 🔄 **Port System**: Connection ports may need alignment with new architecture
- 🔄 **Visual Feedback**: Node selection and highlighting systems
- 🔄 **Performance**: Large graph rendering optimization needed

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

## Current Refactoring Status

### ✅ Phase 1: Foundation Layer - COMPLETED
- ✅ BaseNode abstract class with port management
- ✅ RenderMixin, InteractionMixin, EditableMixin implemented
- ✅ Enhanced Connection and ConnectionManager system
- ✅ ConnectionPort with proper type validation

### ✅ Phase 2: Node Type Migration - COMPLETED
- ✅ **BlueprintNode**: Complete migration from DraggableRect
  - Updated `add_code_block` method to instantiate BlueprintNode
  - Fixed save/load serialization for new node format
  - Grid positioning updated for new architecture
- ✅ **ExecutionNode**: Complete migration from ExecutionDraggableRect
  - Updated `create_execution_nodes` method
  - Fixed save/load with proper node attributes (name, content, original_name)
  - Connection creation updated for new port system
- ✅ **BuildableNode**: Already using new architecture

### ✅ Phase 3: Scene Integration - COMPLETED
- ✅ **BlueprintScene**: Updated for new node types
- ✅ **ExecutionScene**: Updated for new node types  
- ✅ **BuildGraphScene**: Already using new architecture
- ✅ **Visual Integration**: Node rendering working properly
- ✅ **Connection Management**: Enhanced connection system integrated

### 📋 Next Steps

#### Phase 4: Integration and Polish
1. **Main IDE Integration**: 
   - Integrate debug environment features into main blueprint windows
   - Ensure debug_node_system.py enhancements work in production scenes
   - Test save/load functionality with new node types

2. **Configuration System Implementation**:
   - Move editor styling into `config/editor_style.css`
   - Support for user-customizable Qt CSS themes
   - Runtime theme switching capability
   - Theme presets (dark, light, high contrast)

3. **Editor Enhancements**:
   - Text resizing with CTRL+Scroll in CodeEditor
   - Font size adjustment with mouse wheel + Ctrl
   - Maintain zoom level per document/session

#### Phase 5: Advanced Features
4. **Connection Line Improvements**: 
   - Hover effects: 1px → 4px thickness on hover (from debug environment)
   - Color highlighting on hover for better visibility
   - Smooth thickness transitions with animations

5. **Node Control Features**:
   - Child Vertical Align (CTRL+S) integration in main IDE
   - Full Tree Align (CTRL+SHIFT+S) integration
   - Multi-selection enhancements from debug environment

### ⚠️ Known Issues
1. **GraphLayoutOptimizer**: Currently using stub implementation
2. **Save/Load**: May need testing with complex node graphs in production IDE
3. **Performance**: Large graphs not yet optimized
4. **Debug Environment Integration**: Need to port advanced features to main IDE

### 🧪 Testing Status
- ✅ **Compilation**: All files compile without syntax errors
- ✅ **Visual Testing**: Node rendering working properly, debug environment fully functional
- ✅ **Debug Environment**: Comprehensive testing system in place
- 📋 **Integration Testing**: Needed for save/load workflows with main IDE
- 📋 **Performance Testing**: Needed for large graphs

## Migration Strategy

### Phase 4: Scene System Completion
1. Debug and fix node rendering issues
2. Complete connection system unification  
3. Optimize visual performance
4. Add comprehensive error handling

### Phase 5: File Reorganization
1. Move code to new folder structure
2. Add backward compatibility imports
3. Update all internal references

### Phase 6: Testing & Documentation
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
