import dis
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QVBoxLayout, QWidget, 
    QPushButton, QHBoxLayout, QLabel, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from vpy_winmix import CustomWindowMixin

class AssemblyViewer(QMainWindow, CustomWindowMixin):
    def __init__(self, parent=None, code_text=""):
        super().__init__(parent)
        # Set window and widget styles
        self.setStyleSheet("""
            QMainWindow { 
                background: #2c3e50; 
                color: white;
            }
            QWidget {
                background: #2c3e50;
            }
        """)
        # Explicitly disable transparency
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup title bar
        container, containerLayout, titleBar = self.setupCustomTitleBar("Assembly View")
        main_layout.addWidget(titleBar)
        
        # Create toolbar with solid background
        toolbar = QWidget()
        toolbar.setStyleSheet("""
            QWidget {
                background: #2c3e50;
                border: none;
            }
            QComboBox {
                background: #34495e;
                color: white;
                border: 1px solid #445566;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox:hover {
                background: #3d566e;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add assembly type selector
        type_label = QLabel("Assembly Type:")
        type_label.setStyleSheet("color: white; font-weight: bold;")
        self.type_selector = QComboBox()
        self.type_selector.addItems(["Python Bytecode", "Native Assembly"])
        self.type_selector.currentTextChanged.connect(self.update_assembly)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.update_assembly)
        refresh_button.setStyleSheet("""
            QPushButton {
                background: #34495e;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #446380;
            }
        """)
        
        toolbar_layout.addWidget(type_label)
        toolbar_layout.addWidget(self.type_selector)
        toolbar_layout.addWidget(refresh_button)
        toolbar_layout.addStretch()
        
        main_layout.addWidget(toolbar)
        
        # Create text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Courier New", 10))
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ecf0f1;
                border: none;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        main_layout.addWidget(self.text_display)
        
        self.setCentralWidget(central_widget)
        self.resize(800, 600)
        
        # Store the code and update display
        self.code_text = code_text
        self.update_assembly()
        
    def get_python_bytecode(self, code_text):
        """Get Python bytecode for the given code."""
        try:
            # Compile the code
            code_obj = compile(code_text, '<string>', 'exec')
            
            # Use Python's dis module to get bytecode
            import io
            bytecode_output = io.StringIO()
            dis.dis(code_obj, file=bytecode_output)
            return bytecode_output.getvalue()
        except Exception as e:
            return f"Error generating bytecode: {str(e)}"
            
    def get_native_assembly(self, code_text):
        """Get native assembly code using GCC."""
        try:
            # Write Python code to temporary file
            with open('temp.py', 'w') as f:
                f.write(code_text)
            
            # Use gcc to compile to assembly
            import subprocess
            result = subprocess.run(
                ['gcc', '-S', '-o', 'temp.s', 'temp.py'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return f"Error generating assembly:\n{result.stderr}"
            
            # Read the generated assembly
            with open('temp.s', 'r') as f:
                assembly = f.read()
            
            # Clean up temporary files
            import os
            os.remove('temp.py')
            os.remove('temp.s')
            
            return assembly
        except Exception as e:
            return f"Error generating assembly: {str(e)}"
    
    def update_assembly(self):
        """Update the assembly display based on selected type."""
        assembly_type = self.type_selector.currentText()
        
        if assembly_type == "Python Bytecode":
            output = self.get_python_bytecode(self.code_text)
        else:  # Native Assembly
            output = self.get_native_assembly(self.code_text)
            
        self.text_display.setText(output)
