from PyQt5 import QtWidgets, QtGui, QtCore

import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem
from PyQt5 import QtWidgets, QtGui, QtCore

def numpy_to_qpixmap(array: np.ndarray) -> QtGui.QPixmap:
    try:
        if array.ndim == 3:
            height, width, channels = array.shape
            if channels == 1:  # Grayscale image with extra dimension
                bytes_per_line = width
                img = array 
                img = np.squeeze(array, axis=2)
                img = img.astype(np.uint8)
                image = QtGui.QImage(img, width, height, width, QtGui.QImage.Format_Grayscale8)

            elif channels == 3:  # RGB image
                bytes_per_line = 3 * width
                image = QtGui.QImage(array.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888).rgbSwapped()
            else:
                raise ValueError(f"Unsupported number of channels: {channels}")
        else:
            raise ValueError("Unsupported image format")

        if image.isNull():
            raise ValueError("Error converting numpy array to QImage")

        pixmap = QtGui.QPixmap.fromImage(image)

        if pixmap.isNull():
            raise ValueError("Error converting QImage to QPixmap")

        return pixmap

    except Exception as e:
        raise ValueError(f"Error processing numpy array to QPixmap: {str(e)}")
    

from PyQt5 import QtWidgets, QtGui, QtCore

class MeasurementLine(QtWidgets.QGraphicsLineItem):
    def __init__(self, scene, x1, y1, x2, y2):
        super(MeasurementLine, self).__init__(x1, y1, x2, y2)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self._scene = scene

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = event.scenePos()
            self.setLine(self.start_pos.x(), self.start_pos.y(), self.start_pos.x(), self.start_pos.y())
            self._scene.addItem(self)
        super(MeasurementLine, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            end_pos = event.scenePos()
            self.setLine(self.start_pos.x(), self.start_pos.y(), end_pos.x(), end_pos.y())
        super(MeasurementLine, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            end_pos = event.scenePos()
            self.setLine(self.start_pos.x(), self.start_pos.y(), end_pos.x(), end_pos.y())
            self._scene.parent().line_drawn(self.start_pos, end_pos)
        super(MeasurementLine, self).mouseReleaseEvent(event)



import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem
from PyQt5 import QtWidgets, QtGui, QtCore

class ImageWithLineView(QGraphicsView):
    lineDistanceMeasured = QtCore.pyqtSignal(float)

    def __init__(self, image_source):
        super(ImageWithLineView, self).__init__()

        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.image = None
        self.line = None

        self.set_image(image_source)

    def set_image(self, image):
        self.image = numpy_to_qpixmap(image) if isinstance(image, np.ndarray) else QtGui.QPixmap(image)
        self.update_view()

    def update_view(self):
        self.scene.clear()

        if self.image:
            self.image_item = QtWidgets.QGraphicsPixmapItem(self.image)
            self.image_item.setPos(0, 0)
            image_width = self.image.width()
            image_height = self.image.height()
            self.scene.setSceneRect(0, 0, image_width, image_height)
            self.image_item.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.image_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.scene.addItem(self.image_item)

            self.setFixedSize(image_width, image_height)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = event.pos()
            scene_pos = self.mapToScene(self.start_pos)
            self.line = MeasurementLine(self.scene, scene_pos.x(), scene_pos.y(), scene_pos.x(), scene_pos.y())
        super(ImageWithLineView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.line and event.buttons() & QtCore.Qt.LeftButton:
            end_pos = self.mapToScene(event.pos())
            self.line.setLine(self.start_pos.x(), self.start_pos.y(), end_pos.x(), end_pos.y())
        super(ImageWithLineView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.line and event.button() == QtCore.Qt.LeftButton:
            end_pos = self.mapToScene(event.pos())
            self.line.setLine(self.start_pos.x(), self.start_pos.y(), end_pos.x(), end_pos.y())
            self.line_drawn(self.start_pos, end_pos)
        super(ImageWithLineView, self).mouseReleaseEvent(event)

    def line_drawn(self, start_pos, end_pos):
        start_scene_pos = self.mapToScene(start_pos)
        end_scene_pos = self.mapToScene(end_pos)
        distance = self.calculate_distance(start_scene_pos, end_scene_pos)
        self.lineDistanceMeasured.emit(distance)

    def calculate_distance(self, start_pos, end_pos):
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        return (dx**2 + dy**2)**0.5

    def update_scene(self, new_image):
        self.set_image(new_image)
        self.update_view()

import sys
from PyQt5 import QtWidgets, QtCore
class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Replace with the path to your image
        self.image_view = ImageWithLineView("D:\MA\App\Data\April_2024\April_2024\\3_4\\3_4_100mm.jpg")
        self.image_view.lineDistanceMeasured.connect(self.display_distance)
        
        layout.addWidget(self.image_view)
        self.setLayout(layout)

        self.setWindowTitle('Distance Measurement Tool')
        self.resize(800, 600)  # Set a normal size for the main window

    def display_distance(self, distance):
        print(f"Measured distance: {distance:.2f} pixels")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWidget()
    mainWin.show()
    sys.exit(app.exec_())


