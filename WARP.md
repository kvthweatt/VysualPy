# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

VysualPy is a node graph-based IDE for Python development, inspired by Unreal Engine blueprints and disassembler execution flow graphs. It features three main graph workspace types:

1. **Blueprint Graph** - Visual representation of code structure and function relationships
2. **Execution Graph** - Runtime execution flow visualization 
3. **Code Build Graph** - Live code editing workspace where typing creates executable nodes

The IDE transforms traditional coding into a visual building-block system, making refactoring easier and application development faster.

## Quick Start

### Dependencies
- Python 3.12+ (tested with 3.13.5)
- PyQt5 5.15.11+

### Installation
```bash
pip install PyQt5
```

### Running the IDE
```bash
python main.py
```

## Development Commands

### Core Development Tasks
- **Run IDE**: `python main.py`
- **Run Python files from IDE**: Use "Run Program" menu item or run code directly from the IDE
- **Save/Load Workspaces**: 
  - Blueprint workspaces: `*.vpb` files
  - Execution workspaces: `*.veg` files

### Key Shortcuts
- **Ctrl+G**: Go to line (in code editor)
- **Alt + Left-Click**: Pan graph views
- **Ctrl + Mouse Wheel**: Zoom in/out on graphs
- **Delete**: Remove selected comment boxes or nodes
- **Ctrl+Enter**: Complete editing in Build Graph nodes
- **Escape**: Cancel editing in Build Graph nodes

## Architecture

### Core Module Structure

```
vpy_editor.py       - Main IDE window, text editor with syntax highlighting
vpy_blueprints.py   - Three graph workspace implementations
vpy_graph.py        - Node classes (DraggableRect, ExecutionDraggableRect, BuildableNode)
vpy_connection.py   - Node connection system for graph relationships  
vpy_layout.py       - IDE layout with file browser and project management
vpy_menus.py        - Menu system and preferences dialog
vpy_config.py       - Configuration management and language settings
vpy_winmix.py       - Custom window styling and behavior
vpy_defs.py         - Common definitions and constants
main.py             - Application entry point
```

### Graph System Architecture

**Blueprint Graph (`BlueprintScene`, `BlueprintView`, `BlueprintGraphWindow`)**:
- Visualizes code structure as connected nodes
- Each function/class becomes a draggable node with input/output connection points
- Supports comment boxes for grouping related functionality
- Saves/loads workspace state as JSON

**Execution Graph (`ExecutionScene`, `ExecutionView`, `ExecutionGraphWindow`)**:
- Shows runtime execution flow and call paths
- Highlights execution branches (if statements in orange)
- Dims unconnected paths when nodes are selected for clarity
- Uses AST parsing to trace function calls

**Build Graph (`BuildGraphScene`, `BuildGraphView`, `BuildGraphWindow`)**:
- Live editing workspace where typing creates code nodes
- Automatically creates function stubs when undefined functions are called
- Real-time synchronization with main IDE text editor
- Nodes auto-detect type (function, class, assignment) and adjust appearance

### Key Design Patterns

**Node System**: All graph elements inherit from `QGraphicsRectItem` with custom connection points. The `BuildableNode` class supports in-place editing and automatic content analysis.

**AST Integration**: Uses Python's `ast` module to parse code structure, detect function calls, and build execution graphs.

**Live Synchronization**: Build Graph maintains bidirectional sync between visual nodes and source code text.

**Configurable Syntax Highlighting**: Language-agnostic syntax highlighting system with JSON-based language definitions.

## Development Guidelines

### Code Organization
- Each major feature area has its own module (editor, blueprints, graphs, etc.)
- Graph types share common base classes but have specialized behaviors
- Configuration system supports multiple languages via JSON definitions

### Graph Development
- New graph types should inherit from base scene/view classes in `vpy_blueprints.py`
- Connection system in `vpy_connection.py` handles all node relationships
- Graph state persistence uses JSON format with validation

### UI Consistency
- Dark theme styling defined in individual modules
- Custom window styling handled by `CustomWindowMixin`
- PyQt5-based interface with consistent color schemes

### Code Editor Features
- Line numbers with proper viewport handling
- Syntax highlighting for Python (extensible to other languages)
- Go-to-line functionality
- Proper scroll handling for large files

## Configuration

### Language Support
Language definitions stored in `config/python.json` with structure:
```json
{
    "lang": {"name": "Python", "extensions": ["py", "pyc", "pyw"]},
    "keywords": [...],
    "colors": {"keyword": "#FF6B6B", "string": "#98C379", ...}
}
```

### User Settings
- IDE preferences stored in `~/.vysual_ide/config.json`
- Includes editor colors, grid sizes, and environment settings
- Configurable Python interpreter and library paths

## File Browser System
- Dual-tab system: File Browser and Project Browser  
- Project Browser shows "No Project Open" when no project is loaded
- File clicking automatically opens files in main editor
- Tree view with proper styling matching IDE theme

## Build Graph Live Editing
The Build Graph is the most sophisticated feature:

- **Type-and-Create**: Typing in empty space creates new code nodes
- **Function Detection**: Automatically detects when undefined functions are called and creates empty function nodes
- **Scope Detection**: Identifies indentation levels and marks nested vs global scope
- **Real-time Updates**: Changes in nodes immediately update the main source file
- **Connection Tracking**: Visual connections between function calls and definitions

### Build Graph Workflow
1. Type code directly in graph empty space
2. IDE creates a `BuildableNode` automatically  
3. Node analyzes content to detect function/class definitions
4. If code calls undefined functions, new stub nodes are created
5. All changes sync back to main text editor in real-time

## Known Development Notes
- Uses `subprocess.run(["python3", filepath])` for program execution
- Grid snapping set to 50-unit grid for all graph types  
- Comment boxes support resizing with green resize handles
- Rubber band selection enabled in all graph views
- Connection dimming system for visual clarity when nodes are selected

## Troubleshooting

### Common Issues
- **File display problems**: The code editor has specific scroll handling for large files
- **Graph connection issues**: Ensure connection points are properly initialized in node constructors
- **Build Graph sync problems**: Check that `parent_ide` reference is maintained in `BuildableNode` instances

### Performance Notes
- Large files may require viewport optimization in the code editor
- Graph rendering uses full viewport updates for smooth connection drawing
- AST parsing performance scales with code complexity in execution graphs
