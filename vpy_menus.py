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
    """VysualPy Preferences Dialog.
    
    IMPORTANT: After dialog closes, all widgets are destroyed. Any data needed
    must be retrieved via getValues() method which returns cached values.
    Do not attempt to access widgets directly after dialog closes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config = ConfigManager()
        self.load_saved_preferences()
        self.color_buttons = {}
        self.saved_values = None  # Initialize to prevent hasattr checks
        self.initUI()

    def _collect_values(self):
        """Collect all widget values before dialog closes to prevent widget deletion issues."""
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
            return values
        except Exception as e:
            print(f"Error collecting preference values: {e}")
            return {}
    
    def save_and_close(self):
        """Save preferences and close dialog safely."""
        try:
            values = self._collect_values()
            if values:
                self.config.update_config(values)
                self.accept()
        except Exception as e:
            print(f"Error saving preferences: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save preferences: {str(e)}")
    
    def load_saved_preferences(self):
        config = self.config.load_config()
        self.saved_config = config
        
    def populate_fields_from_config(self):
        """Load saved configuration values into the dialog fields"""
        if not hasattr(self, 'saved_config'):
            return
            
        try:
            # Load interpreter path
            if hasattr(self, 'interpreter_path'):
                interpreter = self.saved_config.get('environment', {}).get('python', {}).get('interpreter', '')
                self.interpreter_path.setText(interpreter)
            
            # Load compiler and linker paths  
            if hasattr(self, 'compiler_path'):
                compiler = self.saved_config.get('environment', {}).get('build', {}).get('compiler', '')
                self.compiler_path.setText(compiler)
            
            if hasattr(self, 'linker_path'):
                linker = self.saved_config.get('environment', {}).get('build', {}).get('linker', '')
                self.linker_path.setText(linker)
                
            # Load library paths
            if hasattr(self, 'lib_paths'):
                python_libs = self.saved_config.get('environment', {}).get('python', {}).get('lib_paths', [])
                self.lib_paths.set_paths(python_libs)
            
            if hasattr(self, 'other_lib_paths'):
                build_libs = self.saved_config.get('environment', {}).get('build', {}).get('lib_paths', [])
                self.other_lib_paths.set_paths(build_libs)
                
            # Load grid sizes
            if hasattr(self, 'bp_spinbox'):
                bp_grid = self.saved_config.get('blueprint', {}).get('grid_size', 50)
                self.bp_spinbox.setValue(bp_grid)
                self.bp_slider.setValue(bp_grid)
            
            if hasattr(self, 'ex_spinbox'):
                ex_grid = self.saved_config.get('execution', {}).get('grid_size', 50)
                self.ex_spinbox.setValue(ex_grid)
                self.ex_slider.setValue(ex_grid)
            
            # Load editor colors
            saved_colors = self.saved_config.get('editor', {}).get('colors', {})
            if saved_colors and self.color_buttons:
                from PyQt5.QtGui import QColor
                for name, color_str in saved_colors.items():
                    if name in self.color_buttons:
                        color = QColor(color_str)
                        if color.isValid():
                            self.color_buttons[name].setColor(color)
                
        except Exception as e:
            print(f"Error loading preferences into fields: {e}")
    
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
            
            # Update language config files with current color settings
            if colors:
                # Group colors by language
                language_colors = {}
                for button_name, color in colors.items():
                    if '_' in button_name:
                        language_name, color_name = button_name.split('_', 1)
                        if language_name not in language_colors:
                            language_colors[language_name] = {}
                        language_colors[language_name][color_name] = color.name()
                
                # Update each language config file
                for language_name, lang_colors in language_colors.items():
                    self.update_language_config_colors(language_name, lang_colors)
            
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
        
        # Only add Editor tab if we're in the main IDE window and have current editor
        if hasattr(self.parent, 'current_editor') and self.parent.current_editor():
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
        
        # Load saved preferences into the fields
        self.populate_fields_from_config()
    
    def create_editor_tab(self):
        editor_tab = QWidget()
        editor_layout = QVBoxLayout()
        
        # Language selection group
        language_group = QGroupBox("Language")
        language_layout = QHBoxLayout()
        
        language_label = QLabel("Select Language:")
        self.language_combo = QComboBox()
        
        # Get available languages from config
        from vpy_config import LanguageConfig
        self.lang_config = LanguageConfig()
        available_languages = list(self.lang_config.languages.keys())
        
        if available_languages:
            self.language_combo.addItems(available_languages)
        else:
            self.language_combo.addItem("Python")  # Fallback
            
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()
        
        language_group.setLayout(language_layout)
        editor_layout.addWidget(language_group)
        
        # Syntax highlighting colors group
        self.highlight_group = QGroupBox("Syntax Highlighting Colors")
        self.highlight_layout = QGridLayout()
        
        # Load initial language colors
        self.load_language_colors(self.language_combo.currentText())
        
        self.highlight_group.setLayout(self.highlight_layout)
        editor_layout.addWidget(self.highlight_group)
        
        editor_tab.setLayout(editor_layout)
        return editor_tab
    
    def on_language_changed(self, language_name):
        """Handle language selection change."""
        self.load_language_colors(language_name)
    
    def load_language_colors(self, language_name):
        """Load syntax highlighting colors for the specified language."""
        # Clear existing color buttons
        for i in reversed(range(self.highlight_layout.count())):
            self.highlight_layout.itemAt(i).widget().setParent(None)
        
        # Clear color buttons dictionary but keep the old ones for saving
        current_colors = {}
        
        # Get language config
        language_config = self.lang_config.get_language_by_name(language_name)
        
        if language_config and "colors" in language_config:
            language_colors = language_config["colors"]
        else:
            # Fallback colors
            language_colors = {
                "keyword": "#ff7b72",
                "string": "#a5d6ff", 
                "comment": "#8b949e",
                "function": "#d2a8ff",
                "class": "#ffa657",
                "number": "#79c0ff",
                "decorator": "#f85149"
            }
        
        # Create new color buttons
        row = 0
        for name, color_str in language_colors.items():
            label = QLabel(name.capitalize())
            color = QColor(color_str)
            button = ColorButton(color)
            
            # Store button with language prefix to avoid conflicts
            button_key = f"{language_name}_{name}"
            current_colors[button_key] = button
            
            self.highlight_layout.addWidget(label, row, 0)
            self.highlight_layout.addWidget(button, row, 1)
            row += 1
        
        # Update the main color_buttons dictionary
        # Remove old entries for this language
        keys_to_remove = [k for k in self.color_buttons.keys() if k.startswith(f"{language_name}_")]
        for key in keys_to_remove:
            del self.color_buttons[key]
        
        # Add new entries
        self.color_buttons.update(current_colors)
    
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

    
    def browse_path(self, line_edit):
        path = QFileDialog.getOpenFileName(self, "Select File")[0]
        if path:
            line_edit.setText(path)
    
    def update_language_config_colors(self, language_name, new_colors):
        """Update the language configuration file with new syntax highlighting colors."""
        try:
            import os
            config_path = os.path.join("config", f"{language_name.lower()}.json")
            
            # Load current config
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Update colors section
                config["colors"] = new_colors
                
                # Save updated config
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                
                print(f"Updated {language_name.lower()}.json with new colors")
            else:
                print(f"Warning: {config_path} not found")
                
        except Exception as e:
            print(f"Error updating {language_name} config: {e}")

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
                # Use the tab-based file opening method
                self.parent.open_file_in_tab(filepath)
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
