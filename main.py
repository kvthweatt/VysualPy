import sys
from PyQt5.QtWidgets import QApplication

from vpy_editor import PythonIDE

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = PythonIDE()
    ide.show()
    sys.exit(app.exec_())
