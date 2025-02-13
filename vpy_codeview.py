from PyQt5.QtWidgets import QMainWindow, QTextEdit, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from vpy_winmix import CustomWindowMixin

class CodeViewerWindow(QMainWindow, CustomWindowMixin):
    def __init__(self, title, content):
        super().__init__()
        self.setStyleSheet("QMainWindow { background: #2c3e50; color: white; }")
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        container, containerLayout, titleBar = self.setupCustomTitleBar(title)
        main_layout.addWidget(titleBar)
        
        self.textEdit = QTextEdit()
        self.textEdit.setFont(QFont("Courier", 10))
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(content)
        self.textEdit.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ecf0f1;
                border: none;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        
        main_layout.addWidget(self.textEdit)
        
        titleBar.mousePressEvent = self.titleBarMousePressEvent
        titleBar.mouseMoveEvent = self.titleBarMouseMoveEvent
        
        self.setCentralWidget(central_widget)
        self.resize(600, 400)
