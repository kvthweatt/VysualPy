from PyQt5.QtWidgets import (
    QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QColorDialog,
    QFileDialog
    )

class ColorButton(QPushButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setColor(color)
        self.clicked.connect(self.choose_color)
        
    def setColor(self, color):
        self.color = color
        self.setStyleSheet(f'background-color: {color.name()}')
        
    def choose_color(self):
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.setColor(color)
            
    def getColor(self):
        return self.color

class PathListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # List widget for paths
        self.path_list = QListWidget()
        layout.addWidget(self.path_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Path")
        remove_btn = QPushButton("Remove Path")
        edit_btn = QPushButton("Edit Path")
        
        add_btn.clicked.connect(self.add_path)
        remove_btn.clicked.connect(self.remove_path)
        edit_btn.clicked.connect(self.edit_path)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(edit_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def add_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_list.addItem(path)
    
    def remove_path(self):
        current_item = self.path_list.currentItem()
        if current_item:
            self.path_list.takeItem(self.path_list.row(current_item))
    
    def edit_path(self):
        current_item = self.path_list.currentItem()
        if current_item:
            path = QFileDialog.getExistingDirectory(self, "Select Directory", current_item.text())
            if path:
                current_item.setText(path)
    
    def get_paths(self):
        return [self.path_list.item(i).text() for i in range(self.path_list.count())]
    
    def set_paths(self, paths):
        self.path_list.clear()
        for path in paths:
            self.path_list.addItem(path)
