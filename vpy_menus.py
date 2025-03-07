import json

from os import path, makedirs
from os.path import expanduser, exists, basename
from pathlib import Path

from PyQt5.QtWidgets import (
    QAction, QMenu, QDialog, QVBoxLayout, QWidget, QTabWidget, QGroupBox,
    QHBoxLayout, QLabel, QSlider, QSpinBox, QGridLayout, QColorDialog,
    QComboBox, QLineEdit, QPushButton, QMessageBox, QFileDialog
    )

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from vpy_config import ConfigManager
from vpy_defs import PathListWidget, ColorButton

class PresetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Preset")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_label = QLabel("Preset Name:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(name_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_name(self):
        return self.name_edit.text()

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config = ConfigManager()
        self.load_saved_preferences()
        self.color_buttons = {}
        self.initUI()

    def save_and_close(self):
        # Collect all values into a dictionary immediately
        values = {}
        try:
            values = {
                'grid_size': {
                    'blueprint': self.bp_spinbox.value(),
                    'execution': self.ex_spinbox.value()
                },
                'colors': {name: button.getColor() for name, button in self.color_buttons.items()},
                'env': {
                    'interpreter': str(self.interpreter_path.text()),
                    'python_lib_paths': list(self.lib_paths.get_paths()),
                    'other_lib_paths': list(self.other_lib_paths.get_paths()),
                    'compiler': str(self.compiler_path.text()),
                    'linker': str(self.linker_path.text())
                }
            }
            self.saved_values = values
            self.config.update_config(values)
            self.accept()
        except Exception as e:
            print(f"Error saving preferences: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save preferences: {str(e)}")
    
    def load_saved_preferences(self):
        config = self.config.load_config()
        self.saved_config = config
    
    def accept(self):
        try:
            # Capture all values first
            compiler_path = self.compiler_path.text()
            linker_path = self.linker_path.text()
            interpreter_path = self.interpreter_path.text()
            python_lib_paths = self.lib_paths.get_paths()
            other_lib_paths = self.other_lib_paths.get_paths()
            bp_grid = self.bp_spinbox.value()
            ex_grid = self.ex_spinbox.value()
            colors = {name: button.getColor() for name, button in self.color_buttons.items()}

            # Store in saved_values
            self.saved_values = {
                'grid_size': {
                    'blueprint': bp_grid,
                    'execution': ex_grid
                },
                'colors': colors,
                'env': {
                    'interpreter': interpreter_path,
                    'python_lib_paths': python_lib_paths,
                    'other_lib_paths': other_lib_paths,
                    'compiler': compiler_path,
                    'linker': linker_path
                }
            }
            
            self.config.update_config(self.saved_values)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save preferences: {str(e)}")

    def getValues(self):
        return self.saved_values if hasattr(self, 'saved_values') else None
    
    def initUI(self):
        self.setWindowTitle('Preferences')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        tabs = QTabWidget()

        # Always add Blueprint tab
        blueprint_tab = self.create_blueprint_tab()
        tabs.addTab(blueprint_tab, "Blueprint Graphs")
        
        # Only add Editor tab if we're in the main IDE window
        if hasattr(self.parent, 'textEdit'):
            editor_tab = self.create_editor_tab()
            tabs.addTab(editor_tab, "Editor")
        
        # Environment tabs
        env_tabs = QTabWidget()
        
        # Python environment tab
        python_tab = QTabWidget()
        
        # Python interpreter tab
        interpreter_tab = QWidget()
        interpreter_layout = QVBoxLayout()
        
        interpreter_group = QGroupBox("Python Interpreter")
        interpreter_inner = QGridLayout()
        
        interpreter_label = QLabel("Interpreter Path:")
        self.interpreter_path = QLineEdit()
        interpreter_browse = QPushButton("Browse")
        interpreter_browse.clicked.connect(lambda: self.browse_path(self.interpreter_path))
        
        interpreter_inner.addWidget(interpreter_label, 0, 0)
        interpreter_inner.addWidget(self.interpreter_path, 0, 1)
        interpreter_inner.addWidget(interpreter_browse, 0, 2)
        
        interpreter_group.setLayout(interpreter_inner)
        interpreter_layout.addWidget(interpreter_group)
        interpreter_tab.setLayout(interpreter_layout)
        
        # Python libraries tab
        libraries_tab = QWidget()
        libraries_layout = QVBoxLayout()
        
        lib_group = QGroupBox("Python Library Paths")
        lib_inner = QVBoxLayout()
        
        self.lib_paths = PathListWidget()
        lib_inner.addWidget(self.lib_paths)
        
        lib_group.setLayout(lib_inner)
        libraries_layout.addWidget(lib_group)
        libraries_tab.setLayout(libraries_layout)
        
        python_tab.addTab(interpreter_tab, "Interpreter")
        python_tab.addTab(libraries_tab, "Libraries")
        
        # Other environment tab
        other_tab = QTabWidget()  # Change to QTabWidget

        # Build settings tab
        build_tab = self.create_build_tab()
        other_tab.addTab(build_tab, "Build")

        build_group = QGroupBox("Build Settings")
        build_inner = QGridLayout()

        compiler_label = QLabel("Compiler:")
        self.compiler_path = QLineEdit()
        compiler_browse = QPushButton("Browse")
        compiler_browse.clicked.connect(lambda: self.browse_path(self.compiler_path))

        linker_label = QLabel("Linker:")
        self.linker_path = QLineEdit()
        linker_browse = QPushButton("Browse")
        linker_browse.clicked.connect(lambda: self.browse_path(self.linker_path))

        build_inner.addWidget(compiler_label, 0, 0)
        build_inner.addWidget(self.compiler_path, 0, 1)
        build_inner.addWidget(compiler_browse, 0, 2)
        build_inner.addWidget(linker_label, 1, 0)
        build_inner.addWidget(self.linker_path, 1, 1)
        build_inner.addWidget(linker_browse, 1, 2)

        build_group.setLayout(build_inner)

        # Libraries tab
        lib_tab = QWidget()
        lib_layout = QVBoxLayout()

        lib_group = QGroupBox("Library Paths")
        lib_inner = QVBoxLayout()

        self.other_lib_paths = PathListWidget()
        lib_inner.addWidget(self.other_lib_paths)

        lib_group.setLayout(lib_inner)
        lib_layout.addWidget(lib_group)
        lib_tab.setLayout(lib_layout)

        # Add tabs to other_tab
        other_tab.addTab(build_tab, "Build")
        other_tab.addTab(lib_tab, "Libraries")
        
        env_tabs.addTab(python_tab, "Python")
        env_tabs.addTab(other_tab, "Other")
        
        tabs.addTab(env_tabs, "Environment")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_editor_tab(self):
        # Original editor tab code here
        editor_tab = QWidget()
        editor_layout = QVBoxLayout()
        
        highlight_group = QGroupBox("Syntax Highlighting")
        highlight_layout = QGridLayout()
        
        current_colors = self.parent.textEdit.highlighter.colors
        #self.color_buttons = {}
        row = 0
        for name, color in current_colors.items():
            label = QLabel(name.capitalize())
            button = ColorButton(color)
            self.color_buttons[name] = button
            highlight_layout.addWidget(label, row, 0)
            highlight_layout.addWidget(button, row, 1)
            row += 1
            
        highlight_group.setLayout(highlight_layout)
        editor_layout.addWidget(highlight_group)
        
        theme_group = QGroupBox("Color Themes")
        theme_layout = QVBoxLayout()
        theme_combo = QComboBox()
        theme_combo.addItems(["Default", "Dark", "Light", "Monokai"])
        theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(theme_combo)
        theme_group.setLayout(theme_layout)
        editor_layout.addWidget(theme_group)
        
        editor_tab.setLayout(editor_layout)
        return editor_tab
    
    def create_blueprint_tab(self):
        blueprint_tab = QTabWidget()  # Change to QTabWidget for nested tabs
        
        # Blueprint Graph Tab
        blueprint_graph = QWidget()
        blueprint_layout = QVBoxLayout()
        
        grid_group = QGroupBox("Grid Settings")
        grid_layout = QVBoxLayout()
        
        size_layout = QHBoxLayout()
        size_label = QLabel("Grid Size:")
        self.bp_slider = QSlider(Qt.Horizontal)
        self.bp_slider.setMinimum(10)
        self.bp_slider.setMaximum(100)
        self.bp_slider.setValue(self.parent.grid_size)
        
        self.bp_spinbox = QSpinBox()
        self.bp_spinbox.setMinimum(10)
        self.bp_spinbox.setMaximum(100)
        self.bp_spinbox.setValue(self.parent.grid_size)
        
        self.bp_slider.valueChanged.connect(self.bp_spinbox.setValue)
        self.bp_spinbox.valueChanged.connect(self.bp_slider.setValue)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.bp_slider)
        size_layout.addWidget(self.bp_spinbox)
        grid_layout.addLayout(size_layout)
        grid_group.setLayout(grid_layout)
        blueprint_layout.addWidget(grid_group)
        
        # Additional Blueprint settings can go here
        blueprint_graph.setLayout(blueprint_layout)
        
        # Execution Graph Tab
        execution_graph = QWidget()
        execution_layout = QVBoxLayout()
        
        exec_grid_group = QGroupBox("Grid Settings")
        exec_grid_layout = QVBoxLayout()
        
        exec_size_layout = QHBoxLayout()
        exec_size_label = QLabel("Grid Size:")
        self.ex_slider = QSlider(Qt.Horizontal)
        self.ex_slider.setMinimum(10)
        self.ex_slider.setMaximum(100)
        self.ex_slider.setValue(self.parent.grid_size)
        
        self.ex_spinbox = QSpinBox()
        self.ex_spinbox.setMinimum(10)
        self.ex_spinbox.setMaximum(100)
        self.ex_spinbox.setValue(self.parent.grid_size)
        
        self.ex_slider.valueChanged.connect(self.ex_spinbox.setValue)
        self.ex_spinbox.valueChanged.connect(self.ex_slider.setValue)
        
        exec_size_layout.addWidget(exec_size_label)
        exec_size_layout.addWidget(self.ex_slider)
        exec_size_layout.addWidget(self.ex_spinbox)
        exec_grid_layout.addLayout(exec_size_layout)
        exec_grid_group.setLayout(exec_grid_layout)
        execution_layout.addWidget(exec_grid_group)
        
        execution_graph.setLayout(execution_layout)
        
        # Add both tabs
        blueprint_tab.addTab(blueprint_graph, "Blueprint Graph")
        blueprint_tab.addTab(execution_graph, "Execution Graph")
        
        return blueprint_tab

    def getValues(self):
        return {
            'grid_size': {
                'blueprint': self.bp_spinbox.value(),
                'execution': self.ex_spinbox.value()
            },
            'colors': {name: button.getColor() for name, button in self.color_buttons.items()},
            'env': {
                'interpreter': self.interpreter_path.text(),
                'python_lib_paths': self.lib_paths.get_paths(),
                'other_lib_paths': self.other_lib_paths.get_paths(),
                'compiler': self.compiler_path.text(),
                'linker': self.linker_path.text()
            }
        }
    
    def browse_path(self, line_edit):
        path = QFileDialog.getOpenFileName(self, "Select File")[0]
        if path:
            line_edit.setText(path)
    
    def apply_theme(self, theme_name):
        themes = {
            "Dark": {
                'keyword': QColor("#FF6B6B"),
                'string': QColor("#98C379"),
                'comment': QColor("#5C6370"),
                'function': QColor("#61AFEF"),
                'class': QColor("#E5C07B"),
                'number': QColor("#D19A66"),
                'decorator': QColor("#C678DD"),
            },
            "Light": {
                'keyword': QColor("#D73A49"),
                'string': QColor("#22863A"),
                'comment': QColor("#6A737D"),
                'function': QColor("#005CC5"),
                'class': QColor("#6F42C1"),
                'number': QColor("#E36209"),
                'decorator': QColor("#6F42C1"),
            },
            "Monokai": {
                'keyword': QColor("#F92672"),
                'string': QColor("#E6DB74"),
                'comment': QColor("#75715E"),
                'function': QColor("#66D9EF"),
                'class': QColor("#A6E22E"),
                'number': QColor("#AE81FF"),
                'decorator': QColor("#FD971F"),
            }
        }
        
        if theme_name in themes:
            for name, color in themes[theme_name].items():
                if name in self.color_buttons:
                    self.color_buttons[name].setColor(color)

    def create_build_tab(self):
        build_tab = QWidget()
        build_layout = QVBoxLayout()

        # Presets group
        presets_group = QGroupBox("Build Presets")
        presets_layout = QHBoxLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        
        add_preset = QPushButton("Save As...")
        remove_preset = QPushButton("Remove")
        
        add_preset.clicked.connect(self.save_preset)
        remove_preset.clicked.connect(self.remove_preset)
        
        presets_layout.addWidget(self.preset_combo)
        presets_layout.addWidget(add_preset)
        presets_layout.addWidget(remove_preset)
        
        presets_group.setLayout(presets_layout)
        build_layout.addWidget(presets_group)

        # Build settings group
        build_group = QGroupBox("Build Settings")
        build_inner = QGridLayout()

        compiler_label = QLabel("Compiler:")
        self.compiler_path = QLineEdit()
        compiler_browse = QPushButton("Browse")
        compiler_browse.clicked.connect(lambda: self.browse_path(self.compiler_path))

        linker_label = QLabel("Linker:")
        self.linker_path = QLineEdit()
        linker_browse = QPushButton("Browse")
        linker_browse.clicked.connect(lambda: self.browse_path(self.linker_path))

        build_inner.addWidget(compiler_label, 0, 0)
        build_inner.addWidget(self.compiler_path, 0, 1)
        build_inner.addWidget(compiler_browse, 0, 2)
        build_inner.addWidget(linker_label, 1, 0)
        build_inner.addWidget(self.linker_path, 1, 1)
        build_inner.addWidget(linker_browse, 1, 2)

        build_group.setLayout(build_inner)
        build_layout.addWidget(build_group)
        
        build_tab.setLayout(build_layout)
        return build_tab

    def save_preset(self):
        dialog = PresetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            if name:
                preset = BuildPreset(
                    name=name,
                    compiler_path=self.compiler_path.text(),
                    linker_path=self.linker_path.text(),
                    lib_paths=self.other_lib_paths.get_paths()
                )
                self.save_preset_to_file(preset)
                self.update_preset_list()

    def remove_preset(self):
        current = self.preset_combo.currentText()
        if current:
            self.remove_preset_from_file(current)
            self.update_preset_list()

    def load_preset(self, name):
        if not name:
            return
        preset = self.load_preset_from_file(name)
        if preset:
            self.compiler_path.setText(preset.compiler_path)
            self.linker_path.setText(preset.linker_path)
            self.other_lib_paths.set_paths(preset.lib_paths)

    def save_preset_to_file(self, preset):
        presets_dir = path.join(path.expanduser('~'), '.vysual_ide', 'presets')
        makedirs(presets_dir, exist_ok=True)
        
        preset_path = path.join(presets_dir, f"{preset.name}.json")
        with open(preset_path, 'w') as f:
            json.dump(preset.to_dict(), f)

    def remove_preset_from_file(self, name):
        preset_path = path.join(path.expanduser('~'), '.vysual_ide', 'presets', f"{name}.json")
        if path.exists(preset_path):
            remove(preset_path)

    def load_preset_from_file(self, name):
        preset_path = path.join(path.expanduser('~'), '.vysual_ide', 'presets', f"{name}.json")
        if path.exists(preset_path):
            with open(preset_path) as f:
                data = json.load(f)
                return BuildPreset.from_dict(data)
        return None

    def update_preset_list(self):
        self.preset_combo.clear()
        presets_dir = path.join(path.expanduser('~'), '.vysual_ide', 'presets')
        if path.exists(presets_dir):
            for file in listdir(presets_dir):
                if file.endswith('.json'):
                    self.preset_combo.addItem(file[:-5])

class RecentFiles:
    def __init__(self, max_files=10):
        self.max_files = max_files
        self.recent_files = []
        self.config_file = expanduser('~/.vysual_ide_recent.json')
        self.load_recent_files()

    def add_file(self, filepath):
        """Add a file to recent files list."""
        if not filepath:
            return
            
        # Convert to absolute path
        filepath = str(Path(filepath).resolve())
        
        # Remove if already exists (to move it to top)
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
            
        # Add to beginning of list
        self.recent_files.insert(0, filepath)
        
        # Trim list to max size
        self.recent_files = self.recent_files[:self.max_files]
        
        # Save to disk
        self.save_recent_files()

    def remove_file(self, filepath):
        """Remove a file from recent files list."""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
            self.save_recent_files()

    def get_files(self):
        """Get list of recent files, removing any that no longer exist."""
        existing_files = []
        for filepath in self.recent_files:
            if exists(filepath):
                existing_files.append(filepath)
            
        self.recent_files = existing_files
        self.save_recent_files()
        return existing_files

    def clear(self):
        """Clear the recent files list."""
        self.recent_files = []
        self.save_recent_files()

    def load_recent_files(self):
        """Load recent files list from config file."""
        try:
            if exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.recent_files = json.load(f)
        except Exception as e:
            print(f"Error loading recent files: {e}")
            self.recent_files = []

    def save_recent_files(self):
        """Save recent files list to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.recent_files, f)
        except Exception as e:
            print(f"Error saving recent files: {e}")

class RecentFilesMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__("Recent Files", parent)
        self.parent = parent
        self.recent_files = RecentFiles()
        self.update_menu()

    def update_menu(self):
        """Update the menu with current recent files."""
        self.clear()
        
        files = self.recent_files.get_files()
        
        if not files:
            no_files_action = QAction("No Recent Files", self)
            no_files_action.setEnabled(False)
            self.addAction(no_files_action)
            return

        # Add recent files
        for filepath in files:
            action = QAction(basename(filepath), self)
            action.setStatusTip(filepath)
            action.setData(filepath)
            action.triggered.connect(lambda checked, path=filepath: self.open_recent_file(path))
            self.addAction(action)

        # Add separator and clear option
        self.addSeparator()
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self.clear_recent_files)
        self.addAction(clear_action)

    def add_recent_file(self, filepath):
        """Add a file to recent files and update menu."""
        self.recent_files.add_file(filepath)
        self.update_menu()

    def open_recent_file(self, filepath):
        """Open a recent file."""
        if exists(filepath):
            try:
                with open(filepath, 'r') as file:
                    self.parent.textEdit.setText(file.read())
                self.parent.currentFile = filepath
                self.parent.setWindowTitle(f"Vysual Python IDE - {filepath}")
            except Exception as e:
                self.parent.show_error_message(f"Error opening file: {e}")
                self.recent_files.remove_file(filepath)
                self.update_menu()
        else:
            self.parent.show_error_message(f"File not found: {filepath}")
            self.recent_files.remove_file(filepath)
            self.update_menu()

    def clear_recent_files(self):
        """Clear all recent files."""
        self.recent_files.clear()
        self.update_menu()
