from PyQt5 import QtWidgets, QtGui, QtCore

class MovableHorizontalLine(QtWidgets.QGraphicsLineItem):
    def __init__(self, scene, x1, y1, x2, y2):
        super(MovableHorizontalLine, self).__init__(x1, y1, x2, y2)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges) 
        self.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
        self._line_y_position = y1
        self._scene = scene 


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setSelected(True)
        super(MovableHorizontalLine, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            if event.buttons() & QtCore.Qt.LeftButton:
                new_pos_relative_to_line = event.scenePos()
                new_pos_relative_to_main_scene = self.mapToScene(new_pos_relative_to_line)
                #print(new_pos_relative_to_line, new_pos_relative_to_main_scene)
                new_y = max(0, min(new_pos_relative_to_main_scene.y(), self._scene.sceneRect().height()))
                set_new_y_relative_to_line = self.mapFromScene(new_pos_relative_to_main_scene)
                self.setLine(self.line().x1(), set_new_y_relative_to_line.y(), self.line().x2(), set_new_y_relative_to_line.y())
                ## have t oalways emit the mapToScene(pos) correct for the image 
                self._line_y_position = new_y
        super(MovableHorizontalLine, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setSelected(False)
        super(MovableHorizontalLine, self).mouseReleaseEvent(event)

    def get_line_y_position(self):
        return self._line_y_position


from PyQt5.QtCore import QObject, pyqtSignal
    
class LineController(QObject):
    positionChanged = pyqtSignal(float)

    def __init__(self, line_item):
        super().__init__()
        self.line_item = line_item

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.GraphicsSceneMouseRelease:
            new_y = self.line_item.get_line_y_position()
            print(f"Emitting positionChanged signal with new_y: {new_y}")
            self.positionChanged.emit(new_y)
        return super().eventFilter(watched, event)
    
