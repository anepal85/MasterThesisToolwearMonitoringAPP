from PyQt5 import QtGui, QtWidgets
import numpy as np
from PyQt5.QtCore import Qt 
import sys 
import tensorflow as tf 
 

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

class ImageWithLineView(QtWidgets.QGraphicsView):
    def __init__(self, image_source):
        super(ImageWithLineView, self).__init__()

        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)

        self.image = numpy_to_qpixmap(image_source) 

        if self.image:
            self.image_item = QtWidgets.QGraphicsPixmapItem(self.image)
            self.image_item.setPos(0, 0)
            self.scene.addItem(self.image_item)
            self.scene.setSceneRect(0, 0, self.image.width(), self.image.height())

def preprocess_input(image_path: str, channels: int) -> tf.Tensor:
    image = tf.io.read_file(image_path)
    image = tf.image.decode_image(image, channels=channels)
    image = tf.image.convert_image_dtype(image, tf.uint8)
    return image

if __name__ == "__main__":
    # Initialize the Qt application
    app = QtWidgets.QApplication(sys.argv)

    initial_image_path = r"D:\MA\App\Data\April_2024\April_2024\3_4\3_4_100mm.jpg" 
    initial_image = preprocess_input(initial_image_path, 1)

    #sample_array = np.random.randint(0, 256, (512, 512, 1), dtype=np.uint8)
    #initial_image = 
    imwithlineview = ImageWithLineView(initial_image.numpy())
    imwithlineview.show()
    # try:
    #     # pixmap = numpy_to_qpixmap(sample_array)
    #     # print("Pixmap conversion successful")
    # except ValueError as e:
    #     print(e)

    # Ensure proper cleanup
    sys.exit(app.exec_())