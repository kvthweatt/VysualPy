from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton
    )

from PyQt5.QtCore import Qt

from PyQt5.QtGui import (
    QIcon
    )

class CustomWindowMixin:
    BORDER_WIDTH = 5
    
    def setupCustomTitleBar(self, title):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
            }
        """)
        
        containerLayout = QVBoxLayout(container)
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.setSpacing(0)
        
        titleBar = QFrame()
        titleBar.setFixedHeight(32)
        titleBar.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """)
        
        # Store dragPos at class level
        self.dragPos = None
        titleBar.mousePressEvent = self._titleBarMousePressEvent
        titleBar.mouseMoveEvent = self._titleBarMouseMoveEvent
        
        titleLayout = QHBoxLayout(titleBar)
        titleLayout.setContentsMargins(8, 0, 0, 0)
        titleLayout.setSpacing(4)
        
        iconLabel = QLabel()
        icon = QIcon("icon.svg")
        pixmap = icon.pixmap(24, 24)
        iconLabel.setPixmap(pixmap)
        titleLayout.addWidget(iconLabel)
        
        titleLabel = QLabel(title)
        titleLabel.setObjectName("title_label")
        titleLabel.setStyleSheet("color: white; font-weight: bold;")
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch()
        
        btnWidget = QWidget()
        btnLayout = QHBoxLayout(btnWidget)
        btnLayout.setContentsMargins(0, 0, 0, 0)
        btnLayout.setSpacing(0)
        
        for btnText, btnAction, hoverColor in [
            ("−", self.showMinimized, "#404040"),
            ("□", self.toggleMaximized, "#404040"),
            ("×", self.close, "#c10000")
        ]:
            btn = QPushButton(btnText)
            btn.setFixedSize(46, 32)
            btn.clicked.connect(btnAction)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: white;
                    border: none;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background: {hoverColor};
                }}
            """)
            btnLayout.addWidget(btn)
        
        titleLayout.addWidget(btnWidget)
        containerLayout.addWidget(titleBar)
        
        # Enable resizing
        self._resizeStart = None
        container.mousePressEvent = self._containerMousePressEvent
        container.mouseMoveEvent = self._containerMouseMoveEvent
        container.mouseReleaseEvent = self._containerMouseReleaseEvent
        container.mouseMoveEvent = self._containerMouseMoveEvent
        
        return container, containerLayout, titleBar

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            width = self.width()
            height = self.height()
            edge = self.BORDER_WIDTH

            self.resizing = False
            
            # Check edges for resizing
            if x <= edge:  # Left
                self.resizing = 'left'
            elif x >= width - edge:  # Right
                self.resizing = 'right'
            if y <= edge:  # Top
                self.resizing = 'top'
            elif y >= height - edge:  # Bottom
                self.resizing = 'bottom'

            if not self.resizing:
                self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            else:
                self.dragPosition = event.pos()
                self.oldPos = self.pos()
                self.oldSize = self.size()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'resizing') and self.resizing:
            delta = event.pos() - self.dragPosition
            if self.resizing == 'right':
                self.resize(max(self.minimumWidth(), self.oldSize.width() + delta.x()), self.height())
            elif self.resizing == 'bottom':
                self.resize(self.width(), max(self.minimumHeight(), self.oldSize.height() + delta.y()))
            elif self.resizing == 'left':
                newWidth = max(self.minimumWidth(), self.oldSize.width() - delta.x())
                self.resize(newWidth, self.height())
                if newWidth != self.minimumWidth():
                    self.move(self.oldPos.x() + delta.x(), self.oldPos.y())
            elif self.resizing == 'top':
                newHeight = max(self.minimumHeight(), self.oldSize.height() - delta.y())
                self.resize(self.width(), newHeight)
                if newHeight != self.minimumHeight():
                    self.move(self.oldPos.x(), self.oldPos.y() + delta.y())
        elif hasattr(self, 'dragPosition') and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        
    def changeCursor(self, event):
        x = event.pos().x()
        y = event.pos().y()
        width = self.width()
        height = self.height()
        edge = self.BORDER_WIDTH

        if x <= edge or x >= width - edge:
            self.setCursor(Qt.SizeHorCursor)
        elif y <= edge or y >= height - edge:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def _titleBarMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def _titleBarMouseMoveEvent(self, event):
        if self.dragPos is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _containerMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._resizeStart = event.globalPos()

    def _containerMouseMoveEvent(self, event):
        if self._resizeStart:
            delta = event.globalPos() - self._resizeStart
            self.resize(self.width() + delta.x(), self.height() + delta.y())
            self._resizeStart = event.globalPos()

    def _containerMouseReleaseEvent(self, event):
        self._resizeStart = None

    def titleBarMousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def titleBarMouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'dragPos') and self.dragPos is not None:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def toggleMaximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
