import json
import os
import shutil
from typing import List, Dict, Optional
from dataclasses import dataclass
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QTreeWidget,
    QTreeWidgetItem, QMenu, QSpinBox, QWidget
)
from PyQt5.QtCore import Qt

@dataclass
class ProjectConfig:
    name: str
    version: str
    venv_path: str
    files: List[str]
    working_dir: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectConfig':
        return cls(
            name=data['name'],
            version=data['version'],
            venv_path=data.get('venv_path', ''),
            files=data.get('files', []),
            working_dir=data.get('working_dir', '')
        )

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'venv_path': self.venv_path,
            'files': self.files,
            'working_dir': self.working_dir
        }

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setModal(True)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Project Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Project Name:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Version Number
        version_layout = QHBoxLayout()
        version_label = QLabel("Version:")
        self.version_major = QSpinBox()
        self.version_minor = QSpinBox()
        self.version_patch = QSpinBox()
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_major)
        version_layout.addWidget(QLabel("."))
        version_layout.addWidget(self.version_minor)
        version_layout.addWidget(QLabel("."))
        version_layout.addWidget(self.version_patch)
        layout.addLayout(version_layout)

        # Python Virtual Environment
        venv_layout = QHBoxLayout()
        venv_label = QLabel("Python venv:")
        self.venv_edit = QLineEdit()
        venv_browse = QPushButton("Browse...")
        venv_browse.clicked.connect(self.browse_venv)
        venv_layout.addWidget(venv_label)
        venv_layout.addWidget(self.venv_edit)
        venv_layout.addWidget(venv_browse)
        layout.addLayout(venv_layout)

        # Project Location
        location_layout = QHBoxLayout()
        location_label = QLabel("Location:")
        self.location_edit = QLineEdit()
        location_browse = QPushButton("Browse...")
        location_browse.clicked.connect(self.browse_location)
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_edit)
        location_layout.addWidget(location_browse)
        layout.addLayout(location_layout)

        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton("Create")
        cancel_button = QPushButton("Cancel")
        create_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_venv(self):
        path = QFileDialog.getExistingDirectory(self, "Select Python Virtual Environment")
        if path:
            self.venv_edit.setText(path)

    def browse_location(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Location")
        if path:
            self.location_edit.setText(path)

    def get_project_data(self) -> Optional[ProjectConfig]:
        if not self.validate():
            return None

        version = f"{self.version_major.value()}.{self.version_minor.value()}.{self.version_patch.value()}"
        working_dir = os.path.join(self.location_edit.text(), self.name_edit.text())

        return ProjectConfig(
            name=self.name_edit.text(),
            version=version,
            venv_path=self.venv_edit.text(),
            files=[],
            working_dir=working_dir
        )

    def validate(self) -> bool:
        if not self.name_edit.text():
            QMessageBox.warning(self, "Validation Error", "Project name is required")
            return False
        if not self.location_edit.text():
            QMessageBox.warning(self, "Validation Error", "Project location is required")
            return False
        return True

class ProjectManager:
    def __init__(self):
        self.current_project: Optional[ProjectConfig] = None

    def create_project(self, config: ProjectConfig) -> bool:
        try:
            # Create project directory
            os.makedirs(config.working_dir, exist_ok=True)

            # Create project file
            project_file = os.path.join(config.working_dir, f"{config.name}.vpy")
            with open(project_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=4)

            self.current_project = config
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to create project: {str(e)}")
            return False

    def open_project(self, filepath: str) -> Optional[ProjectConfig]:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.current_project = ProjectConfig.from_dict(data)
                return self.current_project
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to open project: {str(e)}")
            return None

    def add_file_to_project(self, filepath: str) -> bool:
        if not self.current_project:
            return False

        try:
            # Copy file to project directory
            filename = os.path.basename(filepath)
            destination = os.path.join(self.current_project.working_dir, filename)
            shutil.copy2(filepath, destination)

            # Update project file list
            if destination not in self.current_project.files:
                self.current_project.files.append(destination)

            # Save project file
            self.save_project()
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to add file: {str(e)}")
            return False

    def remove_file_from_project(self, filepath: str) -> bool:
        if not self.current_project:
            return False

        try:
            if filepath in self.current_project.files:
                self.current_project.files.remove(filepath)
                os.remove(filepath)  # Remove the file from disk
                self.save_project()
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to remove file: {str(e)}")
            return False

    def save_project(self) -> bool:
        if not self.current_project:
            return False

        try:
            project_file = os.path.join(
                self.current_project.working_dir,
                f"{self.current_project.name}.vpy"
            )
            with open(project_file, 'w') as f:
                json.dump(self.current_project.to_dict(), f, indent=4)
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to save project: {str(e)}")
            return False

class ProjectTreeWidget(QTreeWidget):
    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.setColumnCount(1)
        self.setHeaderLabels(["Project Files"])
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect double-click event
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
    def on_item_double_clicked(self, item, column):
        """Handle double-click on tree items"""
        if item.parent():  # Only handle file items (items with a parent)
            filepath = item.data(0, Qt.UserRole)
            if filepath and os.path.exists(filepath):
                # Find the main IDE window
                ide_window = self.get_ide_window()
                if ide_window:
                    try:
                        with open(filepath, 'r') as file:
                            ide_window.textEdit.setText(file.read())
                        ide_window.currentFile = filepath
                        ide_window.setWindowTitle(f"Vysual Python IDE - {filepath}")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
                        
    def get_ide_window(self):
        """Find the main IDE window by traversing up the parent hierarchy"""
        parent = self.parent()
        while parent:
            if hasattr(parent, 'textEdit'):  # This identifies the main IDE window
                return parent
            parent = parent.parent()
        return None

    def update_tree(self):
        self.clear()
        if not self.project_manager.current_project:
            return

        # Create root item
        root = QTreeWidgetItem(self)
        root.setText(0, self.project_manager.current_project.name)
        
        # Add files
        for filepath in self.project_manager.current_project.files:
            item = QTreeWidgetItem(root)
            item.setText(0, os.path.basename(filepath))
            item.setData(0, Qt.UserRole, filepath)

        root.setExpanded(True)

    def show_context_menu(self, position):
        menu = QMenu()
        add_action = menu.addAction("Add File")
        remove_action = None

        item = self.itemAt(position)
        if item and item.parent():  # If it's a file item
            remove_action = menu.addAction("Remove File")

        action = menu.exec_(self.mapToGlobal(position))
        
        if action == add_action:
            self.add_file()
        elif action == remove_action and item:
            self.remove_file(item)

    def add_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Add File to Project")
        if filepath and self.project_manager.add_file_to_project(filepath):
            self.update_tree()

    def remove_file(self, item):
        filepath = item.data(0, Qt.UserRole)
        if filepath and self.project_manager.remove_file_from_project(filepath):
            self.update_tree()

class ProjectBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_manager = ProjectManager()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create message widget for when no project is loaded
        self.message_widget = QWidget()
        message_layout = QVBoxLayout(self.message_widget)
        message_label = QLabel("No Project Open")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 14px;
            }
        """)
        message_layout.addWidget(message_label)
        
        # Create project tree widget
        self.tree_widget = ProjectTreeWidget(self.project_manager)
        self.tree_widget.setVisible(False)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: #323232;
            }
            QTreeWidget::item:selected {
                background-color: #2d5177;
            }
        """)
        
        # Add widgets to layout
        self.layout.addWidget(self.message_widget)
        self.layout.addWidget(self.tree_widget)
    
    def create_new_project(self):
        """Create a new project"""
        dialog = NewProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            project_config = dialog.get_project_data()
            if project_config and self.project_manager.create_project(project_config):
                self.message_widget.setVisible(False)
                self.tree_widget.setVisible(True)
                self.tree_widget.update_tree()
    
    def open_project(self):
        """Open an existing project"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Visual Python Project (*.vpy)"
        )
        if filepath and self.project_manager.open_project(filepath):
            self.message_widget.setVisible(False)
            self.tree_widget.setVisible(True)
            self.tree_widget.update_tree()
    
    def close_project(self):
        """Close the current project"""
        self.project_manager.current_project = None
        self.message_widget.setVisible(True)
        self.tree_widget.setVisible(False)
        self.tree_widget.clear()
