import numpy as np
from PyQt5.QtWidgets import QGraphicsView,  QGraphicsItem
from PyQt5 import QtWidgets, QtGui, QtCore
from utils.numpy_to_qpixmap import numpy_to_qpixmap
from ui.home.prediction.interactiveimage.moveable_horizontal_line import LineController, MovableHorizontalLine

import numpy as np
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem
from PyQt5 import QtWidgets, QtGui, QtCore
from utils.numpy_to_qpixmap import numpy_to_qpixmap
from ui.home.prediction.interactiveimage.moveable_horizontal_line import LineController, MovableHorizontalLine

class ImageWithLineView(QGraphicsView):
    def __init__(self, image_source, most_horizontal_line):
        super(ImageWithLineView, self).__init__()

        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        self.image = None
        self.horizontal_line = None
        self.line_controller = None
        self.most_horizontal_line = most_horizontal_line

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

            # Set the fixed size of the QGraphicsView to the image size
            self.setFixedSize(image_width, image_height)

        # Update the line position based on the initial most_horizontal_line
        self.update_line_position(self.most_horizontal_line[1])

    def update_line_position(self, new_y):
        new_y = np.abs(new_y)
        if self.horizontal_line:
            try:
                self.scene.removeItem(self.horizontal_line)
            except RuntimeError as e:
                print(f"Error removing horizontal line: {e}")
            self.horizontal_line = None

        if self.image is None:
            return

        self.horizontal_line = MovableHorizontalLine(self.scene, 0, new_y, self.image.width(), new_y)
        self.line_controller = LineController(self.horizontal_line)
        self.scene.installEventFilter(self.line_controller)
        
        self.line_controller.positionChanged.connect(self.on_horizontal_line_position_changed)
        self.scene.addItem(self.horizontal_line)

    def on_horizontal_line_position_changed(self, new_y):
        if self.parent():
            self.parent().on_horizontal_line_position_changed(new_y)

    def update_scene(self, new_image, new_horizontal_line):
        self.set_image(new_image)
        self.update_line_position(new_horizontal_line[1])

    def get_horizontal_line_position(self):
        if self.horizontal_line:
            return self.horizontal_line.get_line_y_position()
        return None

    def update_canvas(self, new_image, new_horizontal_line):
        self.set_image(new_image)
        self.update_line_position(new_horizontal_line[1])














# class ImageWithLineView(QGraphicsView):
#     def __init__(self, image_source, most_horizontal_line):
#         super(ImageWithLineView, self).__init__()

#         self.scene = QtWidgets.QGraphicsScene(self)
#         self.setScene(self.scene)
#         self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

#         self.image = None
#         self.horizontal_line = None
#         self.line_controller = None
#         self.most_horizontal_line = most_horizontal_line

#         self.set_image(image_source)

#     def set_image(self, image):
#         self.image = numpy_to_qpixmap(image) if isinstance(image, np.ndarray) else QtGui.QPixmap(image)
#         self.update_view()

#     def update_view(self):
#         self.scene.clear()

#         if self.image:
#             self.image_item = QtWidgets.QGraphicsPixmapItem(self.image)
#             self.image_item.setPos(0, 0)
#             image_width = self.image.width()
#             image_height = self.image.height()
#             self.scene.setSceneRect(0, 0, image_width, image_height)
#             self.image_item.setFlag(QGraphicsItem.ItemIsMovable, False)
#             self.image_item.setFlag(QGraphicsItem.ItemIsSelectable, False)

#             self.scene.addItem(self.image_item)

#             # Set the fixed size of the QGraphicsView to the image size
#             self.setFixedSize(image_width, image_height)

#         self.update_line_position()

#     def update_line_position(self):
#         if self.horizontal_line:
#             try:
#                 self.scene.removeItem(self.horizontal_line)
#             except RuntimeError as e:
#                 print(f"Error removing horizontal line: {e}")
#             self.horizontal_line = None

#         if self.image is None:
#             return
        
#         image_height = self.image.height()
#         try:
#             angle, dist = self.most_horizontal_line
#             line_y = np.abs(dist) 
#         except IndexError:
#             line_y = image_height / 2

#         self.horizontal_line = MovableHorizontalLine(self.scene, 0, line_y, self.image.width(), line_y)
#         self.line_controller = LineController(self.horizontal_line)
#         #self.horizontal_line.installSceneEventFilter(self.line_controller)
#         self.scene.installEventFilter(self.line_controller)
        
#         self.line_controller.positionChanged.connect(self.on_horizontal_line_position_changed)
#         self.scene.addItem(self.horizontal_line)

#     def on_horizontal_line_position_changed(self, new_y):
#         if self.parent():
#             self.parent().on_horizontal_line_position_changed(new_y)
#         #print(f"horizontal line changed event is handled in imagewithline and new position is {new_y}")

#     def update_scene(self, new_image, new_horizontal_lines):
#         self.set_image(new_image)
#         self.most_horizontal_lines = new_horizontal_lines
#         self.update_line_position()

#     def get_horizontal_line_position(self):
#         if self.horizontal_line:
#             return self.horizontal_line.get_line_y_position()
#         return None

#     def update_canvas(self, new_image, new_horizontal_line):
#         self.set_image(new_image)
#         self.most_horizontal_line = new_horizontal_line
#         self.update_line_position()




























# #### this one is not working but its funktioning at least 

# from PyQt5.QtCore import Qt 
# import numpy as np
# from PyQt5 import QtWidgets, QtGui, QtCore
# from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem
# import numpy as np
# from ui.home.prediction.interactiveimage.moveable_horizontal_line import MovableHorizontalLine
# from utils.numpy_to_qpixmap import numpy_to_qpixmap
    
# class ImageWithLineView(QGraphicsView):
#     def __init__(self, image_source, most_horizontal_line):
#         super(ImageWithLineView, self).__init__()

#         self.scene = QtWidgets.QGraphicsScene(self)
#         self.setScene(self.scene)
#         self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
#         self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
#         self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#         self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

#         self.image = None
#         self.horizontal_line = None

#         self.most_horizontal_line = most_horizontal_line

#         self.set_image(image_source)

#         self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
#         #self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

#     def set_image(self, image):
#         self.image = numpy_to_qpixmap(image) if isinstance(image, np.ndarray) else QtGui.QPixmap(image)
#         self.update_view()

#     def update_view(self):
#         self.scene.clear()

#         if self.image:
#             self.image_item = QtWidgets.QGraphicsPixmapItem(self.image)
#             self.image_item.setPos(0, 0)
#             image_width = self.image.width()
#             image_height = self.image.height()
#             self.scene.setSceneRect(0, 0, image_width, image_height)
            
#             self.image_item.setFlag(QGraphicsItem.ItemIsMovable, False)
#             self.image_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
#             self.scene.addItem(self.image_item)

#         #self.adjust_scene_size()
#         self.update_line_position()

#     # def adjust_scene_size(self):
#     #     if self.image:
#     #         image_width = self.image.width()
#     #         image_height = self.image.height()
#     #         self.scene.setSceneRect(0, 0, image_width, image_height)
#             #self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

#     # def resizeEvent(self, event):
#     #     super(ImageWithLineView, self).resizeEvent(event)
#     #     self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
#     #     self.update_line_position()

#     def update_line_position(self):
#         if self.horizontal_line:
#             try:
#                 self.scene.removeItem(self.horizontal_line)
#             except RuntimeError as e:
#                 print(f"Error removing horizontal line: {e}")
#             self.horizontal_line = None

#         if self.image is None:
#             return
        
#         image_width = self.image.width()
#         image_height = self.image.height()

#         #self.scene.setSceneRect(0, 0, image_width, image_height)

#         widget_height = self.viewport().height()
#         scale_factor = widget_height / image_height

#         print(widget_height, image_height, self.most_horizontal_line)

#         try:
#             angle, dist =  self.most_horizontal_line
#             line_y = widget_height + (dist * scale_factor)
#             #_, line_y = self.most_horizontal_line
#         except IndexError:
#             line_y = image_height/2

#         # try:
#         #     if self.most_horizontal_lines[0] is not None:
#         #         _, line_y = self.most_horizontal_lines[0]
#         #     else:
#         #        line_y = image_height / 2 * scale_factor
#         #     line_y *= scale_factor
#         # #         File "D:\CNC_MonitoringAPP\ui\home\prediction\interactiveimage\test_2.py", line 75, in update_line_position
#         # #     _, line_y = self.most_horizontal_lines[0]
#         # # ValueError: too many values to unpack (expected 2)
#         # except IndexError:
#         #     line_y = image_height / 2 * scale_factor

#         self.horizontal_line = MovableHorizontalLine(0, line_y, self.image.width(), line_y)
#         self.scene.addItem(self.horizontal_line)

#     def update_scene(self, new_image, new_horizontal_lines):
#         self.set_image(new_image)
#         self.most_horizontal_lines = new_horizontal_lines
#         self.update_line_position()

#     def get_horizontal_line_position(self):
#         if self.horizontal_line:
#             return self.horizontal_line.get_line_y_position()
#         return None
    
#     def update_canvas(self, new_image, new_horizontal_line):
#         self.set_image(new_image)
#         self.most_horizontal_line = new_horizontal_line
#         self.update_line_position()



















# # import sys
# # from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
# # from PyQt5 import QtGui
# # from PyQt5.QtGui import QPixmap

# # class ImageWithLineView(QGraphicsView):
# #     def __init__(self, image_source, pred_mask=None, most_horizontal_lines=None):
# #         super(ImageWithLineView, self).__init__()

# #         self.scene = QGraphicsScene(self)
# #         self.setScene(self.scene)

# #         # Handle image source
# #         if isinstance(image_source, np.ndarray):
# #             image = numpy_to_qpixmap(image_source)
# #         else:
# #             image = QtGui.QPixmap(image_source)
        
# #         # Load the image and set to fixed size
# #         self.fixed_width = 1280
# #         self.fixed_height = 960

# #         # Load the image and set to fixed size
# #         self.pixmap_item = QGraphicsPixmapItem(image.scaled(self.fixed_width, self.fixed_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
# #         self.scene.addItem(self.pixmap_item)
        
# #         self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
# #         self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
# #         self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
# #         self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
# #         self.setRenderHint(QtGui.QPainter.Antialiasing)
# #         self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
# #         self.updateImagePosition()

# #     def resizeEvent(self, event):
# #         super().resizeEvent(event)
# #         self.updateImagePosition()

# #     def updateImagePosition(self):
# #         view_width = self.viewport().width()
# #         view_height = self.viewport().height()
        
# #         # Center the pixmap item in the view
# #         x_offset = (view_width - self.fixed_width) / 2
# #         y_offset = (view_height - self.fixed_height) / 2
# #         self.pixmap_item.setPos(x_offset, y_offset)
