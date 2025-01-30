from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsPathItem
)

from PyQt5.QtCore import Qt, QPointF

from PyQt5.QtGui import (
    QPen, QColor, QPainterPath
    )

import re

class ConnectionPoint(QGraphicsEllipseItem):
    def __init__(self, scene, parent, is_output):
        super().__init__(-5, -5, 10, 10, parent)
        self.is_output = is_output
        self.connections = []
        self.setAcceptHoverEvents(True)
        self.setBrush(Qt.white)  # White dot for connection points
        self.setPen(QPen(Qt.gray))  # Gray border for connection points
        self.setZValue(1)
        self.blueprint_scene = scene  # Renamed to be more specific
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Use the stored scene instance directly
            if hasattr(self.blueprint_scene, 'connection_in_progress') and not self.blueprint_scene.connection_in_progress:
                self.blueprint_scene.connection_in_progress = Connection(self, self.mapToScene(event.pos()), self.blueprint_scene)
                self.blueprint_scene.addItem(self.blueprint_scene.connection_in_progress)
                self.blueprint_scene.active_connection_point = self
            super().mousePressEvent(event)
        elif event.button() == Qt.RightButton:
            self.showContextMenu(event)

    def addConnection(self, connection):
        if connection not in self.connections:
            self.connections.append(connection)

    def removeConnection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def showContextMenu(self, event):
        menu = QMenu()
        if self.is_output:
            action = menu.addAction("Break All Connections")
            action.triggered.connect(self.breakAllConnections)
        else:
            if self.connections:  # Only show if there's a connection
                action = menu.addAction("Break Connection")
                action.triggered.connect(self.breakConnection)
        
        menu.exec_(event.screenPos())

    def breakAllConnections(self):
        # Create a copy of the list since we'll be modifying it during iteration
        connections_to_remove = self.connections.copy()
        for connection in connections_to_remove:
            connection.cleanup()
            if connection.scene():
                connection.scene().removeItem(connection)

    def breakConnection(self):
        if self.connections:  # Input points should only have one connection
            connection = self.connections[0]
            connection.cleanup()
            if connection.scene():
                connection.scene().removeItem(connection)

class Connection(QGraphicsPathItem):
    def __init__(self, start_point, end_pos, scene=None):
        super().__init__()
        self.start_point = start_point
        self.end_pos = end_pos
        self.end_point = None
        self.scene = scene

        # Set default color
        color = QColor(144, 238, 144)  # Light green default

        # Set color based on parent node type if available
        if isinstance(start_point, ConnectionPoint) and hasattr(start_point, 'parentItem'):
            parent_rect = start_point.parentItem()
            if hasattr(parent_rect, 'name') and hasattr(parent_rect, 'full_content'):
                content = re.sub(r'^\s+', '', parent_rect.full_content)
                if parent_rect.name is None or parent_rect.name == "Global":
                    color = QColor(144, 238, 144)  # Light green for global blocks
                elif content.startswith("class"):
                    color = QColor(255, 165, 0)  # Orange for classes
                elif content.startswith("async def") or content.startswith("def"):
                    color = QColor(173, 216, 230)  # Light blue for functions

        self.setPen(QPen(color, 2))
        self.setZValue(0)

        if isinstance(start_point, ConnectionPoint):
            self.start_point.addConnection(self)

        self.updatePath()

    def updatePath(self):
        # Get start position
        if isinstance(self.start_point, ConnectionPoint):
            start_pos = self.start_point.scenePos()
            start_rect = self.start_point.parentItem()
            if is_return := (self.pen().color().name() == '#ff00ff'):
                start_pos = start_rect.mapToScene(0, start_rect.boundingRect().height())
            else:
                start_pos = start_rect.mapToScene(start_rect.boundingRect().width(), 
                                                start_rect.boundingRect().height() / 2)
        else:
            start_pos = self.start_point

        # Get end position
        if isinstance(self.end_point, ConnectionPoint):
            end_rect = self.end_point.parentItem()
            if is_return:
                end_pos = end_rect.mapToScene(end_rect.boundingRect().width(), 
                                            end_rect.boundingRect().height())
            else:
                end_pos = end_rect.mapToScene(0, end_rect.boundingRect().height() / 2)
        else:
            end_pos = self.end_pos

        # Create path
        path = QPainterPath()
        path.moveTo(start_pos)
        
        # Calculate control points
        dx = end_pos.x() - start_pos.x()
        ctrl1 = QPointF(start_pos.x() + dx * 0.5, start_pos.y())
        ctrl2 = QPointF(end_pos.x() - dx * 0.5, end_pos.y())
        
        # Create curve
        path.cubicTo(ctrl1, ctrl2, QPointF(end_pos.x(), end_pos.y()))
        self.setPath(path)

    def setEndPoint(self, end_point):
        # Remove from old end point if it exists
        if self.end_point and isinstance(self.end_point, ConnectionPoint):
            self.end_point.removeConnection(self)
            
        self.end_point = end_point
        if isinstance(end_point, ConnectionPoint):
            self.end_point.addConnection(self)
        self.updatePath()

    def cleanup(self):
        # Remove references from both connection points
        if isinstance(self.start_point, ConnectionPoint):
            self.start_point.removeConnection(self)
        if isinstance(self.end_point, ConnectionPoint):
            self.end_point.removeConnection(self)
