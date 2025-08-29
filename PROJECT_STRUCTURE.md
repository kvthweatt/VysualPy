# VysualPy Project Structure Report

Generated on: 2025-08-29 12:58:44
Total files analyzed: 11

## Overview

- Total Classes: 42
- Total Functions: 2
- Total Lines of Code: 5268

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

**Lines:** 1526 | **Classes:** 11 | **Functions:** 1

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

- `FunctionCallCollector(NodeVisitor)` (line 60)
  - `__init__()` (method)
  - `visit_FunctionDef()` (method)
  - `visit_AsyncFunctionDef()` (method)
  - `visit_Call()` (method)
  - `_get_callable_name()` (method)
  - ... and 1 more methods
- `BlueprintScene(QGraphicsScene)` (line 114)
  - `__init__()` (method)
  - `mouseMoveEvent()` (method)
  - `mouseReleaseEvent()` (method)
  - `mousePressEvent()` (method)
  - `showContextMenu()` (method)
- `BlueprintView(QGraphicsView)` (line 178)
  - `__init__()` (method)
  - `keyPressEvent()` (method)
  - `mousePressEvent()` (method)
  - `mouseMoveEvent()` (method)
  - `mouseReleaseEvent()` (method)
  - ... and 2 more methods
- `BlueprintGraphWindow(QMainWindow, CustomWindowMixin)` (line 279)
  - `__init__()` (method)
  - `showPreferences()` (method)
  - `updateGridSize()` (method)
  - `saveBlueprintWorkspace()` (method)
  - `loadBlueprintWorkspace()` (method)
  - ... and 6 more methods
- `FunctionCallVisitor(NodeVisitor)` (line 635)
  - `__init__()` (method)
  - `should_include_call()` (method)
  - `visit_Module()` (method)
  - `visit_If()` (method)
  - `visit_While()` (method)
  - ... and 9 more methods
- `ExecutionScene(BlueprintScene)` (line 819)
  - `__init__()` (method)
- `ExecutionView(BlueprintView)` (line 824)
  - `__init__()` (method)
- `ExecutionGraphWindow(QMainWindow, CustomWindowMixin)` (line 829)
  - `__init__()` (method)
  - `addCommentBoxToScene()` (method)
  - `create_menus()` (method)
  - `showPreferences()` (method)
  - `updateGridSize()` (method)
  - ... and 8 more methods
- `BuildGraphScene(BlueprintScene)` (line 1197)
  - `__init__()` (method)
  - `should_initialize()` (method)
  - `initialize_default_structure()` (method)
  - `keyPressEvent()` (method)
  - `mousePressEvent()` (method)
  - ... and 3 more methods
- `BuildGraphView(BlueprintView)` (line 1341)
  - `__init__()` (method)
  - `keyPressEvent()` (method)
  - `deleteSelectedNodes()` (method)
  - `mousePressEvent()` (method)
- `BuildGraphWindow(QMainWindow)` (line 1434)
  - `__init__()` (method)
  - `confirm_code_replacement()` (method)
  - `create_initial_nodes()` (method)
  - `setup_menus()` (method)

**Functions:**

- `detect_function_calls(source_code)` (function, line 18)

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

**Lines:** 1305 | **Classes:** 6 | **Functions:** 0

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
  - ... and 6 more methods
- `EditorTabs(QTabWidget)` (line 494)
  - `__init__()` (method)
  - `add_new_tab()` (method)
  - `_create_code_editor()` (method)
  - `_mark_dirty()` (method)
  - `_mark_clean()` (method)
  - ... and 6 more methods
- `PythonIDE(QMainWindow)` (line 721)
  - `__init__()` (method)
  - `initUI()` (method)
  - `createMenuBar()` (method)
  - `createMenus()` (method)
  - `toggleMaximized()` (method)
  - ... and 24 more methods

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

### vpy_menus.py

**Lines:** 648 | **Classes:** 4 | **Functions:** 0

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
  - `save_and_close()` (method)
  - `load_saved_preferences()` (method)
  - `accept()` (method)
  - `getValues()` (method)
  - ... and 14 more methods
- `RecentFiles` (line 522)
  - `__init__()` (method)
  - `add_file()` (method)
  - `remove_file()` (method)
  - `get_files()` (method)
  - `clear()` (method)
  - ... and 2 more methods
- `RecentFilesMenu(QMenu)` (line 590)
  - `__init__()` (method)
  - `update_menu()` (method)
  - `add_recent_file()` (method)
  - `open_recent_file()` (method)
  - `clear_recent_files()` (method)

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
