# VysualPy Project Structure Report

Generated on: 2025-08-29 14:21:51
Total files analyzed: 16

## Overview

- Total Classes: 69
- Total Functions: 10
- Total Lines of Code: 7659

## File Details

### analyze_project.py

**Lines:** 380 | **Classes:** 5 | **Functions:** 1

**Description:**
> VysualPy Project Analyzer

This tool scans the VysualPy source files and generates a structural overview
of classes, functions, and their relationships. It helps track the codebase
during refactoring and provides quick reference information.

Usage:
    python analyze_project.py [--output PROJECT_STRUCTURE.md] [--json project_structure.json]

**Key Imports:**

- `ast`
- `os`
- `json`
- `argparse`
- `from pathlib import Path`
- `from typing import Dict`
- `from typing import List`
- `from typing import Tuple`
- `from typing import Any`
- `from typing import Optional`
- ... and 2 more

**Classes:**

- `FunctionInfo` (line 23)
- `ClassInfo` (line 36)
- `FileInfo` (line 47)
- `ProjectAnalyzer` (line 57)
  - `__init__()` (method)
  - `analyze_file()` (method)
  - `analyze_project()` (method)
  - `generate_markdown_report()` (method)
  - `_format_file_info()` (method)
  - ... and 2 more methods
- `FileVisitor(NodeVisitor)` (line 212)
  - `__init__()` (method)
  - `visit_Module()` (method)
  - `visit_Import()` (method)
  - `visit_ImportFrom()` (method)
  - `visit_ClassDef()` (method)
  - ... and 5 more methods

**Functions:**

- `main()` (function, line 343)

---

### main.py

**Lines:** 10 | **Classes:** 0 | **Functions:** 0

**Key Imports:**

- `sys`
- `from PyQt5.QtWidgets import QApplication`
- `from vpy_editor import PythonIDE`

---

### vpy_blueprints.py

**Lines:** 1584 | **Classes:** 11 | **Functions:** 1

**Key Imports:**

- `ast`
- `builtins`
- `json`
- `from PyQt5.QtWidgets import QGraphicsScene`
- `from PyQt5.QtWidgets import QGraphicsView`
- `from PyQt5.QtWidgets import QMainWindow`
- `from PyQt5.QtWidgets import QWidget`
- `from PyQt5.QtWidgets import QVBoxLayout`
- `from PyQt5.QtWidgets import QMenuBar`
- `from PyQt5.QtWidgets import QAction`
- ... and 19 more

**Classes:**

- `FunctionCallCollector(NodeVisitor)` (line 62)
  - `__init__()` (method)
  - `visit_FunctionDef()` (method)
  - `visit_AsyncFunctionDef()` (method)
  - `visit_Call()` (method)
  - `_get_callable_name()` (method)
  - ... and 1 more methods
- `BlueprintScene(QGraphicsScene)` (line 116)
  - `__init__()` (method)
  - `mouseMoveEvent()` (method)
  - `mouseReleaseEvent()` (method)
  - `mousePressEvent()` (method)
  - `showContextMenu()` (method)
- `BlueprintView(QGraphicsView)` (line 180)
  - `__init__()` (method)
  - `keyPressEvent()` (method)
  - `mousePressEvent()` (method)
  - `mouseMoveEvent()` (method)
  - `mouseReleaseEvent()` (method)
  - ... and 2 more methods
- `BlueprintGraphWindow(QMainWindow, CustomWindowMixin)` (line 281)
  - `__init__()` (method)
  - `showPreferences()` (method)
  - `updateGridSize()` (method)
  - `saveBlueprintWorkspace()` (method)
  - `loadBlueprintWorkspace()` (method)
  - ... and 6 more methods
- `FunctionCallVisitor(NodeVisitor)` (line 642)
  - `__init__()` (method)
  - `should_include_call()` (method)
  - `visit_Module()` (method)
  - `visit_If()` (method)
  - `visit_While()` (method)
  - ... and 9 more methods
- `ExecutionScene(BlueprintScene)` (line 826)
  - `__init__()` (method)
- `ExecutionView(BlueprintView)` (line 831)
  - `__init__()` (method)
- `ExecutionGraphWindow(QMainWindow, CustomWindowMixin)` (line 836)
  - `__init__()` (method)
  - `addCommentBoxToScene()` (method)
  - `create_menus()` (method)
  - `showPreferences()` (method)
  - `updateGridSize()` (method)
  - ... and 8 more methods
- `BuildGraphScene(BlueprintScene)` (line 1209)
  - `__init__()` (method)
  - `should_initialize()` (method)
  - `initialize_default_structure()` (method)
  - `keyPressEvent()` (method)
  - `mousePressEvent()` (method)
  - ... and 3 more methods
- `BuildGraphView(BlueprintView)` (line 1391)
  - `__init__()` (method)
  - `keyPressEvent()` (method)
  - `deleteSelectedNodes()` (method)
  - `mousePressEvent()` (method)
- `BuildGraphWindow(QMainWindow)` (line 1484)
  - `__init__()` (method)
  - `addCommentBoxToScene()` (method)
  - `confirm_code_replacement()` (method)
  - `create_initial_nodes()` (method)
  - `setup_menus()` (method)

**Functions:**

- `detect_function_calls(source_code)` (function, line 20)

---

### vpy_config.py

**Lines:** 139 | **Classes:** 2 | **Functions:** 0

**Key Imports:**

- `from os import path`
- `from os import makedirs`
- `from os import listdir`
- `json`

**Classes:**

- `LanguageConfig` (line 5)
  - `__init__()` (method)
  - `load_configs()` (method)
  - `create_default_config()` (method)
  - `get_language_config()` (method)
  - `get_language_by_name()` (method)
- `ConfigManager` (line 59)
  - `__init__()` (method)
  - `ensure_config_exists()` (method)
  - `get_default_config()` (method)
  - `load_config()` (method)
  - `save_config()` (method)
  - ... and 1 more methods

---

### vpy_connection.py

**Lines:** 153 | **Classes:** 2 | **Functions:** 0

**Key Imports:**

- `from PyQt5.QtWidgets import QGraphicsEllipseItem`
- `from PyQt5.QtWidgets import QGraphicsPathItem`
- `from PyQt5.QtCore import Qt`
- `from PyQt5.QtCore import QPointF`
- `from PyQt5.QtGui import QPen`
- `from PyQt5.QtGui import QColor`
- `from PyQt5.QtGui import QPainterPath`
- `re`

**Classes:**

- `ConnectionPoint(QGraphicsEllipseItem)` (line 13)
  - `__init__()` (method)
  - `mousePressEvent()` (method)
  - `addConnection()` (method)
  - `removeConnection()` (method)
  - `showContextMenu()` (method)
  - ... and 2 more methods
- `Connection(QGraphicsPathItem)` (line 70)
  - `__init__()` (method)
  - `updatePath()` (method)
  - `setEndPoint()` (method)
  - `cleanup()` (method)

---

### vpy_connection_core.py

**Lines:** 498 | **Classes:** 4 | **Functions:** 0

**Description:**
> Enhanced connection system for VysualPy.

Provides improved connection management, validation, and visual feedback
while maintaining backward compatibility with the existing system.

**Key Imports:**

- `from typing import Dict`
- `from typing import List`
- `from typing import Any`
- `from typing import Optional`
- `from typing import Callable`
- `from typing import Set`
- `from enum import Enum`
- `uuid`
- `from PyQt5.QtWidgets import QGraphicsPathItem`
- `from PyQt5.QtWidgets import QGraphicsScene`
- ... and 11 more

**Classes:**

- `ConnectionStyle(Enum)` (line 19)
- `ConnectionState(Enum)` (line 27)
- `Connection(QGraphicsPathItem, BaseConnection)` (line 36)
  - `__init__()` (method)
  - `setEndPoint()` (method)
  - `updatePath()` (method)
  - `updatePen()` (method)
  - `validate()` (method)
  - ... and 9 more methods
- `ConnectionManager(QObject)` (line 340)
  - `__init__()` (method)
  - `add_validation_rule()` (method)
  - `start_connection()` (method)
  - `update_connection()` (method)
  - `complete_connection()` (method)
  - ... and 9 more methods

---

### vpy_defs.py

**Lines:** 76 | **Classes:** 2 | **Functions:** 0

**Key Imports:**

- `from PyQt5.QtWidgets import QPushButton`
- `from PyQt5.QtWidgets import QWidget`
- `from PyQt5.QtWidgets import QHBoxLayout`
- `from PyQt5.QtWidgets import QVBoxLayout`
- `from PyQt5.QtWidgets import QListWidget`
- `from PyQt5.QtWidgets import QColorDialog`
- `from PyQt5.QtWidgets import QFileDialog`

**Classes:**

- `ColorButton(QPushButton)` (line 6)
  - `__init__()` (method)
  - `setColor()` (method)
  - `choose_color()` (method)
  - `getColor()` (method)
- `PathListWidget(QWidget)` (line 24)
  - `__init__()` (method)
  - `initUI()` (method)
  - `add_path()` (method)
  - `remove_path()` (method)
  - `edit_path()` (method)
  - ... and 2 more methods

---

### vpy_editor.py

**Lines:** 1312 | **Classes:** 6 | **Functions:** 0

**Key Imports:**

- `re`
- `os`
- `subprocess`
- `from PyQt5.QtWidgets import QMainWindow`
- `from PyQt5.QtWidgets import QMenuBar`
- `from PyQt5.QtWidgets import QAction`
- `from PyQt5.QtWidgets import QTextEdit`
- `from PyQt5.QtWidgets import QMessageBox`
- `from PyQt5.QtWidgets import QGraphicsView`
- `from PyQt5.QtWidgets import QFileDialog`
- ... and 37 more

**Classes:**

- `CodeViewerWindow(QMainWindow, CustomWindowMixin)` (line 30)
  - `__init__()` (method)
- `SyntaxHighlighter(QSyntaxHighlighter)` (line 66)
  - `__init__()` (method)
  - `setup_default_format()` (method)
  - `load_language()` (method)
  - `setup_formats()` (method)
  - `highlightBlock()` (method)
- `LineNumberArea(QWidget)` (line 139)
  - `__init__()` (method)
  - `sizeHint()` (method)
  - `paintEvent()` (method)
- `CodeEditor(QTextEdit)` (line 150)
  - `__init__()` (method)
  - `handleScrollRangeChange()` (method)
  - `handleTextChanged()` (method)
  - `lineNumberAreaPaintEvent()` (method)
  - `line_number_area_width()` (method)
  - ... and 7 more methods
- `EditorTabs(QTabWidget)` (line 465)
  - `__init__()` (method)
  - `add_new_tab()` (method)
  - `_create_code_editor()` (method)
  - `_mark_dirty()` (method)
  - `_mark_clean()` (method)
  - ... and 6 more methods
- `PythonIDE(QMainWindow)` (line 692)
  - `__init__()` (method)
  - `initUI()` (method)
  - `createMenuBar()` (method)
  - `createMenus()` (method)
  - `toggleMaximized()` (method)
  - ... and 26 more methods

---

### vpy_graph.py

**Lines:** 531 | **Classes:** 4 | **Functions:** 0

**Key Imports:**

- `re`
- `from PyQt5.QtWidgets import QGraphicsRectItem`
- `from PyQt5.QtWidgets import QGraphicsTextItem`
- `from PyQt5.QtWidgets import QInputDialog`
- `from PyQt5.QtWidgets import QGraphicsItem`
- `from PyQt5.QtCore import QRectF`
- `from PyQt5.QtCore import Qt`
- `from PyQt5.QtGui import QColor`
- `from PyQt5.QtGui import QBrush`
- `from PyQt5.QtGui import QPen`
- ... and 3 more

**Classes:**

- `CommentBox(QGraphicsRectItem)` (line 17)
  - `__init__()` (method)
  - `mousePressEvent()` (method)
  - `mouseMoveEvent()` (method)
  - `mouseReleaseEvent()` (method)
  - `paint()` (method)
  - ... and 1 more methods
- `DraggableRect(QGraphicsRectItem)` (line 103)
  - `__init__()` (method)
  - `snapToGrid()` (method)
  - `updateConnectionPoints()` (method)
  - `updateConnectedLines()` (method)
  - `mousePressEvent()` (method)
  - ... and 3 more methods
- `ExecutionDraggableRect(DraggableRect)` (line 228)
  - `__init__()` (method)
  - `itemChange()` (method)
  - `updateConnectedLines()` (method)
  - `mousePressEvent()` (method)
  - `mouseMoveEvent()` (method)
- `BuildableNode(QGraphicsRectItem)` (line 332)
  - `__init__()` (method)
  - `updateConnectionPoints()` (method)
  - `updateTitle()` (method)
  - `startEditing()` (method)
  - `stopEditing()` (method)
  - ... and 6 more methods

---

### vpy_layout.py

**Lines:** 297 | **Classes:** 5 | **Functions:** 0

**Key Imports:**

- `from PyQt5.QtWidgets import QTreeView`
- `from PyQt5.QtWidgets import QFileSystemModel`
- `from PyQt5.QtWidgets import QDockWidget`
- `from PyQt5.QtWidgets import QPlainTextEdit`
- `from PyQt5.QtWidgets import QSplitter`
- `from PyQt5.QtWidgets import QVBoxLayout`
- `from PyQt5.QtWidgets import QHBoxLayout`
- `from PyQt5.QtWidgets import QWidget`
- `from PyQt5.QtWidgets import QPushButton`
- `from PyQt5.QtWidgets import QStyle`
- ... and 7 more

**Classes:**

- `ProjectBrowser(QWidget)` (line 10)
  - `__init__()` (method)
  - `load_project()` (method)
  - `close_project()` (method)
  - `on_file_clicked()` (method)
- `FileBrowser(QWidget)` (line 99)
  - `__init__()` (method)
  - `set_current_directory()` (method)
  - `on_file_clicked()` (method)
- `BrowserTabs(QDockWidget)` (line 154)
  - `__init__()` (method)
- `Terminal(QDockWidget)` (line 191)
  - `__init__()` (method)
  - `write()` (method)
  - `flush()` (method)
  - `clear_output()` (method)
  - `restore_stdout()` (method)
- `IDELayout` (line 259)
  - `setup()` (method)

---

### vpy_legacy_compat.py

**Lines:** 351 | **Classes:** 7 | **Functions:** 5

**Description:**
> Backward compatibility layer for VysualPy refactored architecture.

This module provides compatibility wrappers and import paths for existing code
that relies on the old node and connection classes.

**Key Imports:**

- `warnings`
- `from typing import Any`
- `from typing import Dict`
- `from typing import Optional`
- `from PyQt5.QtCore import QPointF`
- `from PyQt5.QtCore import QRectF`
- `from PyQt5.QtWidgets import QGraphicsScene`
- `from vpy_node_base import BaseNode`
- `from vpy_node_base import NodeType`
- `from vpy_node_base import NodeState`
- ... and 7 more

**Classes:**

- `DraggableRect(BlueprintNode)` (line 30)
  - `__init__()` (method)
  - `full_content()` (method)
  - `full_content()` (method)
  - `snapToGrid()` (method)
- `ExecutionDraggableRect(ExecutionNode)` (line 74)
  - `__init__()` (method)
  - `full_content()` (method)
  - `full_content()` (method)
- `LegacyConnection` (line 109)
  - `__init__()` (method)
  - `setEndPoint()` (method)
  - `updatePath()` (method)
  - `__getattr__()` (method)
- `CommentBox(CommentNode)` (line 157)
  - `__init__()` (method)
- `ConnectionPoint` (line 177)
  - `__init__()` (method)
  - `parentItem()` (method)
  - `connections()` (method)
- `LegacyGraphModule` (line 240)
  - `__getattr__()` (method)
- `LegacyConnectionModule` (line 257)
  - `__getattr__()` (method)

**Functions:**

- `_deprecated_warning(old_name, new_name, version)` (function, line 20)
- `create_legacy_node(node_type)` (function, line 214)
- `setup_legacy_imports()` (function, line 231)
- `migrate_workspace_data(old_data)` (function, line 270)
- `check_compatibility()` (function, line 309)

---

### vpy_menus.py

**Lines:** 682 | **Classes:** 4 | **Functions:** 0

**Key Imports:**

- `json`
- `from os import path`
- `from os import makedirs`
- `from os.path import expanduser`
- `from os.path import exists`
- `from os.path import basename`
- `from pathlib import Path`
- `from PyQt5.QtWidgets import QAction`
- `from PyQt5.QtWidgets import QMenu`
- `from PyQt5.QtWidgets import QDialog`
- ... and 20 more

**Classes:**

- `PresetDialog(QDialog)` (line 19)
  - `__init__()` (method)
  - `get_name()` (method)
- `PreferencesDialog(QDialog)` (line 48)
  - `__init__()` (method)
  - `_collect_values()` (method)
  - `save_and_close()` (method)
  - `load_saved_preferences()` (method)
  - `populate_fields_from_config()` (method)
  - ... and 15 more methods
- `RecentFiles` (line 558)
  - `__init__()` (method)
  - `add_file()` (method)
  - `remove_file()` (method)
  - `get_files()` (method)
  - `clear()` (method)
  - ... and 2 more methods
- `RecentFilesMenu(QMenu)` (line 626)
  - `__init__()` (method)
  - `update_menu()` (method)
  - `add_recent_file()` (method)
  - `open_recent_file()` (method)
  - `clear_recent_files()` (method)

---

### vpy_node_base.py

**Lines:** 470 | **Classes:** 8 | **Functions:** 0

**Description:**
> Base node system for VysualPy graph architecture.

This module provides the foundation for a unified node system that eliminates
code duplication and provides clear interfaces for different node types.

**Key Imports:**

- `from abc import ABCMeta`
- `from abc import abstractmethod`
- `from typing import Dict`
- `from typing import List`
- `from typing import Any`
- `from typing import Optional`
- `from typing import Set`
- `from typing import Union`
- `from typing import Callable`
- `from enum import Enum`
- ... and 8 more

**Classes:**

- `QGraphicsABCMeta(ABCMeta)` (line 19)
- `NodeType(Enum)` (line 24)
- `PortType(Enum)` (line 32)
- `ConnectionPort` (line 39)
  - `__init__()` (method)
  - `can_connect_to()` (method)
  - `add_connection()` (method)
  - `remove_connection()` (method)
- `BaseConnection` (line 81)
  - `__init__()` (method)
  - `disconnect()` (method)
  - `serialize()` (method)
- `NodeState(Enum)` (line 114)
- `BaseNode(QGraphicsRectItem)` (line 124)
  - `__init__()` (method)
  - `add_input_port()` (method)
  - `add_output_port()` (method)
  - `remove_port()` (method)
  - `_update_port_positions()` (method)
  - ... and 17 more methods
- `NodeRegistry` (line 440)
  - `__init__()` (method)
  - `register_node_class()` (method)
  - `register_factory_function()` (method)
  - `create_node()` (method)
  - `get_available_types()` (method)

---

### vpy_node_mixins.py

**Lines:** 532 | **Classes:** 3 | **Functions:** 0

**Description:**
> Mixin classes for VysualPy node system.

These mixins provide shared functionality that can be composed into different
node types, promoting code reuse and separation of concerns.

**Key Imports:**

- `from typing import Optional`
- `from typing import Dict`
- `from typing import Any`
- `from abc import ABC`
- `from abc import abstractmethod`
- `from PyQt5.QtWidgets import QGraphicsTextItem`
- `from PyQt5.QtWidgets import QGraphicsRectItem`
- `from PyQt5.QtWidgets import QMenu`
- `from PyQt5.QtWidgets import QAction`
- `from PyQt5.QtWidgets import QInputDialog`
- ... and 17 more

**Classes:**

- `RenderMixin` (line 24)
  - `__init__()` (method)
  - `get_node_color()` (method)
  - `paint()` (method)
  - `get_border_color()` (method)
  - `paint_title()` (method)
  - ... and 5 more methods
- `InteractionMixin` (line 216)
  - `__init__()` (method)
  - `mousePressEvent()` (method)
  - `mouseMoveEvent()` (method)
  - `mouseReleaseEvent()` (method)
  - `hoverEnterEvent()` (method)
  - ... and 8 more methods
- `EditableMixin` (line 396)
  - `__init__()` (method)
  - `startEditing()` (method)
  - `stopEditing()` (method)
  - `cancelEdit()` (method)
  - `commitEdit()` (method)
  - ... and 4 more methods

---

### vpy_node_types.py

**Lines:** 441 | **Classes:** 5 | **Functions:** 3

**Description:**
> Concrete implementations of different node types for VysualPy.

These classes combine the BaseNode with appropriate mixins to create
specialized node types for different use cases.

**Key Imports:**

- `ast`
- `re`
- `from typing import Dict`
- `from typing import List`
- `from typing import Any`
- `from typing import Optional`
- `from PyQt5.QtCore import QPointF`
- `from PyQt5.QtCore import QRectF`
- `from PyQt5.QtGui import QColor`
- `from vpy_node_base import BaseNode`
- ... and 8 more

**Classes:**

- `BlueprintNode(BaseNode, RenderMixin, InteractionMixin)` (line 19)
  - `__init__()` (method)
  - `analyze_content()` (method)
  - `get_display_name()` (method)
  - `get_tooltip_text()` (method)
  - `can_accept_content()` (method)
  - ... and 1 more methods
- `ExecutionNode(BaseNode, RenderMixin, InteractionMixin)` (line 100)
  - `__init__()` (method)
  - `set_conditional()` (method)
  - `set_has_return()` (method)
  - `get_display_name()` (method)
  - `get_tooltip_text()` (method)
  - ... and 2 more methods
- `BuildableNode(BaseNode, RenderMixin, InteractionMixin, EditableMixin)` (line 169)
  - `__init__()` (method)
  - `analyze_and_update()` (method)
  - `analyze_content()` (method)
  - `detect_function_calls()` (method)
  - `get_display_name()` (method)
  - ... and 4 more methods
- `LegacyConnectionPoint` (line 314)
  - `__init__()` (method)
  - `setPos()` (method)
  - `pos()` (method)
  - `scenePos()` (method)
  - `parentItem()` (method)
  - ... and 2 more methods
- `CommentNode(BaseNode, RenderMixin, InteractionMixin, EditableMixin)` (line 353)
  - `__init__()` (method)
  - `get_display_name()` (method)
  - `get_tooltip_text()` (method)
  - `can_accept_content()` (method)
  - `process_content_change()` (method)

**Functions:**

- `register_node_types()` (function, line 409)
- `create_draggable_rect()` (function, line 417)
- `create_execution_draggable_rect()` (function, line 426)

---

### vpy_winmix.py

**Lines:** 203 | **Classes:** 1 | **Functions:** 0

**Key Imports:**

- `from PyQt5.QtWidgets import QWidget`
- `from PyQt5.QtWidgets import QVBoxLayout`
- `from PyQt5.QtWidgets import QHBoxLayout`
- `from PyQt5.QtWidgets import QFrame`
- `from PyQt5.QtWidgets import QLabel`
- `from PyQt5.QtWidgets import QPushButton`
- `from PyQt5.QtCore import Qt`
- `from PyQt5.QtGui import QIcon`

**Classes:**

- `CustomWindowMixin` (line 11)
  - `setupCustomTitleBar()` (method)
  - `mousePressEvent()` (method)
  - `mouseMoveEvent()` (method)
  - `mouseReleaseEvent()` (method)
  - `changeCursor()` (method)
  - ... and 8 more methods

---
