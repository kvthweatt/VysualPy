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
- **Analyze Project Structure**: `python analyze_project.py --output PROJECT_STRUCTURE.md --json project_structure.json`

### Project Structure Analyzer
A utility script to scan the repository and produce an up-to-date index of classes and functions per file.

- Script: `analyze_project.py`
- Purpose: Generate a concise reference of the codebase layout to aid refactors and reviews
- Outputs:
  - `PROJECT_STRUCTURE.md` — human-readable report (timestamped)
  - `project_structure.json` — machine-readable data for tooling
- Scope: Currently scans Python files in the repository root (non-recursive)
- Suggested workflow: Run after notable refactors to refresh the index

Examples:
```bash
# Markdown only
python analyze_project.py --output PROJECT_STRUCTURE.md

# Markdown + JSON
python analyze_project.py --output PROJECT_STRUCTURE.md --json project_structure.json
```

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

## Recent Bug Fixes (2025)

### Font Scaling Issues ✅ FIXED
- **Problem**: `QFont::setPointSize: Point size <= 0 (-2)` errors causing application spam
- **Root Cause**: Font scaling calculations in `CommentBox.paint()` and `CodeEditor.lineNumberAreaPaintEvent()` could result in negative font sizes
- **Solution**: Added bounds checking to ensure font sizes are always >= 8pt with fallback values
- **Files Fixed**: `vpy_graph.py` (lines 73-82), `vpy_editor.py` (lines 254-257)

### Terminal Cleanup Issues ✅ FIXED
- **Problem**: "wrapped C/C++ object of type Terminal has been deleted" error on application exit
- **Root Cause**: `sys.stdout` redirection to Terminal widget without proper cleanup
- **Solution**: Added proper stdout restoration in Terminal class and IDE closeEvent handler
- **Files Fixed**: `vpy_layout.py` (Terminal class), `vpy_editor.py` (closeEvent method)

### Missing Import Errors ✅ FIXED
- **Problem**: Missing `QTimer` and `QTextFormat` imports causing runtime errors
- **Solution**: Added missing imports to `vpy_editor.py`

### BuildGraph Editor Integration ✅ FIXED (Aug 29, 2025)
- **Problem**: BuildGraph system failing with "IDE object has no attribute 'textEdit'" errors
- **Root Cause**: BuildGraph classes accessing non-existent `textEdit` attribute instead of tab-based editor system
- **Solution**: Updated all BuildGraph editor access to use `current_editor()` method and check for valid editor instance
- **Files Fixed**: `vpy_blueprints.py` (BuildGraphScene, BuildGraphView classes)

### Missing Function Implementation ✅ FIXED (Aug 29, 2025)
- **Problem**: `detect_function_calls` function referenced but not implemented, breaking BuildGraph auto-function creation
- **Solution**: Implemented complete AST-based function call detection with built-in exclusions and local function filtering
- **Files Fixed**: `vpy_blueprints.py` (added FunctionCallCollector class and detect_function_calls function)

### Custom Window Dragging ✅ FIXED (Aug 29, 2025)
- **Problem**: TypeError "unsupported operand type(s) for -: 'QPoint' and 'NoneType'" when dragging custom windows
- **Root Cause**: `dragPos` variable not properly initialized or checked for None before arithmetic operations
- **Solution**: Added proper null checks and initialization in CustomWindowMixin mouse event handlers
- **Files Fixed**: `vpy_winmix.py` (titleBarMouseMoveEvent method)

### Multiple Inheritance Issues ✅ FIXED (Aug 29, 2025)
- **Problem**: Duplicate `super().__init__()` calls causing initialization conflicts in Blueprint windows
- **Solution**: Cleaned up constructor calls to use single proper inheritance chain
- **Files Fixed**: `vpy_blueprints.py` (BlueprintGraphWindow constructor)

## Ongoing Refactoring (August 2025)

### Code Architecture Improvements
The graph and node system is undergoing refactoring to improve maintainability and extensibility:

#### Issues Being Addressed
- **Code Duplication**: Three similar node classes (`DraggableRect`, `ExecutionDraggableRect`, `BuildableNode`) share overlapping functionality
- **Missing Dependencies**: `detect_function_calls` function referenced but not implemented, breaking BuildGraph auto-function creation
- **Large Monolithic Files**: `vpy_blueprints.py` (1422 lines) handles multiple responsibilities
- **Inconsistent Patterns**: Different approaches for similar functionality across node types
- **Mixed Concerns**: Classes handling both rendering and business logic

#### Refactoring Strategy
1. **Create unified Node base class** with clear interface for ports, connections, and state
2. **Extract mixins** for rendering, interaction, and business logic to promote code reuse
3. **Implement missing utilities** like `detect_function_calls` in new `utils/` module
4. **Split large files** into focused modules with clear responsibilities
5. **Maintain backward compatibility** with existing APIs during transition

#### Progress Tracking
- ✅ **Project Structure Analysis**: Created `analyze_project.py` tool for tracking changes
- ✅ **Baseline Documentation**: Generated `PROJECT_STRUCTURE.md` with current architecture
- 🔄 **Utility Functions**: Working on `utils/ast_tools.py` for AST parsing functions
- ⏳ **Node Hierarchy**: Planning unified base classes and mixins
- ⏳ **Connection System**: Redesigning for extensibility and validation

### New Development Tools

#### Project Structure Analyzer (`analyze_project.py`)
- **Purpose**: Track codebase structure changes during refactoring
- **Output**: Timestamped reports showing classes, functions, and relationships
- **Usage**: Run after major changes to update documentation
- **Integration**: Generates both human-readable Markdown and machine-readable JSON

## Current Status (Updated 2025-08-29)

### ✅ Working Features
- **IDE Startup**: Application launches cleanly without font scaling errors
- **Code Editor**: Basic text editing with syntax highlighting for Python
- **Line Numbers**: Proper line numbering with fixed font scaling
- **File Operations**: Open, save, and manage Python files
- **Terminal Integration**: Output redirection with proper cleanup
- **Menu System**: All main menus and actions are functional
- **Dark Theme**: Consistent dark UI theme across components
- **Window Dragging**: Fixed custom title bar dragging functionality with proper null checks
- **BuildGraph Integration**: Fixed editor access to work with tab-based architecture

### 🔄 Recently Fixed Features (Aug 29, 2025)
- **BuildGraph Editor Access**: Fixed `textEdit` attribute errors by updating to use `current_editor()` method
- **Function Call Detection**: Implemented missing `detect_function_calls` function with AST parsing
- **Window Dragging Bug**: Resolved TypeError in custom window dragging with proper dragPos initialization
- **Multiple Inheritance Issues**: Fixed duplicate `super().__init__()` calls in Blueprint classes

### 🔄 Partially Working Features
- **Graph Systems**: Blueprint, Execution, and Build Graph windows can be opened and function correctly
- **File Browser**: Basic file system navigation (needs testing)
- **Workspace Management**: Save/load functionality exists but needs validation
- **Build Graph Live Editing**: Core functionality restored, auto-function creation working

### ⚠️ Features Needing Testing/Validation
- **Node Connections**: Graph node connection system needs validation
- **AST Parsing**: Execution graph generation from code
- **Workspace Persistence**: Save/load of graph workspaces (.vpb, .veg files)
- **Program Execution**: Running Python files from within the IDE

### 🚧 Known Areas for Improvement
- **Error Handling**: More robust error handling throughout the application
- **Performance**: Graph rendering optimization for large codebases
- **Testing**: No unit tests currently exist
- **Documentation**: User documentation and help system

## Troubleshooting

### Common Issues
- **File display problems**: The code editor has specific scroll handling for large files
- **Graph connection issues**: Ensure connection points are properly initialized in node constructors
- **Build Graph sync problems**: Check that `parent_ide` reference is maintained in `BuildableNode` instances
- **Font scaling errors**: If you see font size warnings, check that all font.setPointSize() calls use max() to ensure positive values
- **Terminal output issues**: Ensure Terminal class properly stores and restores original stdout

### Performance Notes
- Large files may require viewport optimization in the code editor
- Graph rendering uses full viewport updates for smooth connection drawing
- AST parsing performance scales with code complexity in execution graphs
- Font scaling calculations are now bounded to prevent negative sizes

### Debugging Tips
- Use `python main.py` to run the IDE directly and see any console output
- Check for Qt font warnings - these indicate scaling calculation issues
- Terminal output redirection can mask print statements - use original stdout if needed
- Graph view scaling issues often manifest as font size problems
