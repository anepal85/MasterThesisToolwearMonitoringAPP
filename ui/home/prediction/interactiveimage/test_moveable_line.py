import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt 
import sys
from skimage import color, filters, feature, transform


def numpy_to_qpixmap(array: np.ndarray) -> QtGui.QPixmap:
    if array.ndim == 2:  # Grayscale image
        height, width = array.shape
        bytes_per_line = width
        image = QtGui.QImage(array.data, width, height, bytes_per_line, QtGui.QImage.Format_Grayscale8)
    elif array.ndim == 3:
        height, width, channels = array.shape
        if channels == 1:  # Grayscale image with extra dimension
            bytes_per_line = width
            image = QtGui.QImage(array.data, width, height, bytes_per_line, QtGui.QImage.Format_Grayscale8)
        elif channels == 3:  # RGB image
            bytes_per_line = 3 * width
            #array = array.astype(np.uint8)
            image = QtGui.QImage(array.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
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

def create_transparent_overlay(pixmap):
    image = pixmap.toImage().convertToFormat(QtGui.QImage.Format_ARGB32)
    for y in range(image.height()):
        for x in range(image.width()):
            pixel = image.pixel(x, y)
            alpha = QtGui.qAlpha(pixel)
            if alpha > 0:
                alpha = int(alpha * 0.7)  # Adjust overlay opacity as needed
                image.setPixel(x, y, QtGui.qRgba(QtGui.qRed(pixel), QtGui.qGreen(pixel), QtGui.qBlue(pixel), alpha))
    return QtGui.QPixmap.fromImage(image)

def preprocess_input(image_path: str, channels: int) -> tf.Tensor:
    image = tf.io.read_file(image_path)
    image = tf.image.decode_image(image, channels=channels)
    image = tf.image.convert_image_dtype(image, tf.uint8)
    return image

def squeeze_tensor_to_np(tf_image: tf.Tensor, **kwargs) -> np.array:
    return np.squeeze(tf_image, **kwargs)

class MostHorizontalLineDetector:
    def __init__(self, image):
        self.image = image

    def find_most_horizontal_line(self):
        # Convert the image to grayscale
        gray_image = color.rgb2gray(self.image)

        # Apply Gaussian blur to the grayscale image
        blurred_image = filters.gaussian(gray_image, sigma=3)

        # Apply Sobel filter in the x-direction
        sobel_edges = filters.sobel_h(blurred_image)

        # Perform Canny edge detection on the edges obtained from the Sobel filter
        canny_edges = feature.canny(sobel_edges)

        # Perform Hough transform to detect lines
        hough_transform, angles, distances = transform.hough_line(canny_edges)

        # Find the peaks in Hough space
        peaks = transform.hough_line_peaks(hough_transform, angles, distances)

        # Initialize lists to store multiple horizontal lines with maximum length
        max_lengths = []
        most_horizontal_lines = []

        for _, angle, dist in zip(*peaks):
            y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
            y1 = (dist - canny_edges.shape[1] * np.cos(angle)) / np.sin(angle)
            length = np.abs(y1 - y0)
            if not max_lengths or length > max(max_lengths):
                max_lengths.append(length)
                most_horizontal_lines.append((angle, dist))
            elif length == max(max_lengths):
                most_horizontal_lines.append((angle, dist))

        return most_horizontal_lines

class MovableHorizontalLine(QtWidgets.QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2):
        super(MovableHorizontalLine, self).__init__(x1, y1, x2, y2)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.isSelected():
            new_pos = value.toPoint()
            new_pos.setX(int(self.pos().x()))  # Keep x position fixed
            return new_pos
            #new_pos.setX(self.line().x1())  # Keep x position fixed
            #return new_pos
        return super(MovableHorizontalLine, self).itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setSelected(True)
        super(MovableHorizontalLine, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isSelected():
            new_pos = event.scenePos()
            new_pos.setX(self.line().x1())  # Keep x position fixed
            new_y = max(0, min(new_pos.y(), self.scene().height()))
            self.setLine(self.line().x1(), new_y, self.line().x2(), new_y)
        super(MovableHorizontalLine, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setSelected(False)
        super(MovableHorizontalLine, self).mouseReleaseEvent(event)

    def get_line_y_position(self):
        return self.line().y1()

class ImageWithLineView(QtWidgets.QGraphicsView):
    def __init__(self, image_source, pred_mask, most_horizontal_lines):
        super(ImageWithLineView, self).__init__()

        self.scene = QtWidgets.QGraphicsScene(self)
        #self.scene.setSceneRect(0, 0, image_source.shape[1], image_source.shape[0])
        self.setScene(self.scene)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setFixedSize(800, 600)

        self.image = None
        self.pred_mask = None
        self.horizontal_line = None

        self.most_horizontal_lines = most_horizontal_lines

        if image_source is not None:
            self.set_image_and_mask(image_source, pred_mask)


        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def set_image_and_mask(self, image, mask):
        self.image = numpy_to_qpixmap(image) if isinstance(image, np.ndarray) else QtGui.QPixmap(image)
        self.pred_mask = numpy_to_qpixmap(mask) if isinstance(mask, np.ndarray) else QtGui.QPixmap(mask)
        self.update_view()

    def update_view(self):
        self.scene.clear()
        if self.image:
            self.image_item = QtWidgets.QGraphicsPixmapItem(self.image)
            self.image_item.setPixmap(self.image)
            self.image_item.setPos(0, 0)
            # self.image_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            # self.image_item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
            self.scene.addItem(self.image_item)

        # if self.pred_mask is not None:
        #     q_image = numpy_to_qpixmap(self.pred_mask)
        #     mask_pixmap = create_transparent_overlay(q_image) #QtGui.QPixmap.fromImage(q_image)
        #     mask_item = QtWidgets.QGraphicsPixmapItem(mask_pixmap)
        #     mask_item.setPos(0,0)
        #     mask_item.setOpacity(0.9)  # Adjust opacity for overlay effect
        #     # mask_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        #     # mask_item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        #     self.scene.addItem(mask_item)
        #print("afte update_view")
        self.update_line_position()


    # def resizeEvent(self, event):
    #     super(ImageWithLineView, self).resizeEvent(event)
    #     self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
    #     self.update_line_position()

    def update_line_position(self):
        if self.horizontal_line:
            try:
                self.scene.removeItem(self.horizontal_line)
            except RuntimeError as e:
                print(f"Error removing horizontal line: {e}")
            self.horizontal_line = None

        if self.image is None:
            return
        
        image_width = self.image.width()
        image_height = self.image.height()

        self.scene.setSceneRect(0, 0, image_width, image_height)
        # Calculate the conversion factor
        widget_width = self.viewport().width()
        widget_height = self.viewport().height()


        scale_factor = min(widget_width / image_width, widget_height / image_height)
        scene_height = self.scene.height()
        adjusted_horizontal_lines = [
            (angle, widget_height - dist * scale_factor) for angle, dist in self.most_horizontal_lines
        ]
        try:
            _, line_y = self.most_horizontal_lines[0] #adjusted_horizontal_lines[2]
            print('\n', line_y, '\n')
        except IndexError:
            line_y = image_height/2

        self.horizontal_line = MovableHorizontalLine(0, line_y, self.image.width(), line_y)
        self.scene.addItem(self.horizontal_line)
        print(image_height, image_width, widget_height, widget_width)
        print(scale_factor)
        print("-----------------")
        

    def update_canvas(self, new_image, new_mask):
        self.set_image_and_mask(new_image, new_mask)

    def get_horizontal_line_position(self):
        if self.horizontal_line:
            return self.horizontal_line.get_line_y_position()
        return None


def tf_resize_image(image: tf.Tensor, width: int, height: int) -> tf.Tensor:
    return tf.image.resize(image, (width, height), method = 'nearest')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Movable Horizontal Line on Image")
        self.setGeometry(100, 100, 800, 600)

        # Load the image
        image_path = r"D:\MA\App\Data\April_2024\April_2024\3_4\3_4_100mm.jpg"
        image = preprocess_input(image_path, 3)
        image = squeeze_tensor_to_np(tf_resize_image(image, 512, 512))

        detector = MostHorizontalLineDetector(image)
        most_horizontal_lines = detector.find_most_horizontal_line()
        print(most_horizontal_lines)

        self.image_view = ImageWithLineView(image, np.zeros_like(image), most_horizontal_lines)
        self.setCentralWidget(self.image_view)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
