# import numpy as np
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import matplotlib.pyplot as mpl


# class MyFigureCanvas(FigureCanvas):
#     '''
#     This is the FigureCanvas in which the live plot is drawn.

#     '''
#     def __init__(self, x, y:list, y_label_name:list) -> None:
#         super().__init__(mpl.figure())

#         self.x = x 
#         self.y = y 
#         self.y_label_name = y_label_name
        
#         # Store a figure ax
        
#         self._ax_ = self.figure.subplots() 
#         #self._ax_.set_ylim(ymin=self._y_range_[0], ymax=self._y_range_[1]) # added
        
#         color = ['blue','green','red','orange','cyan']
        

#         if len(self.y)>1 and len(color) >= len(self.y):
#             for i, diff_y in enumerate(self.y):
#                 self._line_, = self._ax_.plot(self.x, diff_y, color[i])
#                 self._line_.set_label(self.y_label_name[i])
#                 self._line_.set_ydata(diff_y)

#                 self._ax_.draw_artist(self._ax_.patch)
#                 self._ax_.draw_artist(self._line_)

#         self._ax_.set_xlabel('Time')
#         self._ax_.set_ylabel('Value')
#         self._ax_.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
#              borderaxespad=0, mode="expand", ncol=len(self.y))
#         self.draw()  
        
# import numpy as np
# import matplotlib.pyplot as mpl
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


# class MyFigureCanvas(FigureCanvas):
#     '''
#     This is the FigureCanvas in which two images are drawn side by side.

#     '''
#     def __init__(self, image1, image2) -> None:
#         super().__init__(mpl.figure())

#         self.image1 = image1
#         self.image2 = image2

#         # Create subplots for two images
#         self._ax1_ = self.figure.add_subplot(1, 2, 1)
#         self._ax2_ = self.figure.add_subplot(1, 2, 2)

#         # Plot the first image
#         self._ax1_.imshow(self.image1)
#         self._ax1_.set_title('Image 1')

#         # Plot the second image
#         self._ax2_.imshow(self.image2)
#         self._ax2_.set_title('Image 2')

#         self.draw()

# Usage Example:
# Assuming 'image1' and 'image2' are two images you want to plot
# Replace 'image1' and 'image2' with your actual images
# my_canvas = MyFigureCanvas(image1, image2)
# my_canvas.show()


# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# class MyFigureCanvas(FigureCanvas):
#     '''
#     This is the FigureCanvas in which two images are drawn with one on top of another.

#     '''
#     def __init__(self, image, prediction_mask) -> None:
#         self.figure = plt.figure()
#         super().__init__(self.figure)
#         self.update_canvas(image, prediction_mask)

#     def update_canvas(self, image, prediction_mask):
#         self.figure.clear()
#         ax = self.figure.add_subplot(1, 1, 1)
#         ax.imshow(image, cmap='gray')
#         ax.imshow(np.ma.masked_array(prediction_mask, prediction_mask == 0), cmap='viridis', alpha=0.7)
#         ax.set_title('Original Image with Prediction Mask')
#         self.draw()



import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

class ImageOverlayWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(ImageOverlayWidget, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = None
        self.overlay_item = None

    def set_images(self, image, overlay):
        self.update_canvas(image, overlay)
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def update_canvas(self, image, overlay):
        if isinstance(image, str):
            self.image = QtGui.QPixmap(image)
        else:
            self.image = self.numpy_to_qpixmap(image)

        if isinstance(overlay, str):
            overlay_image = QtGui.QPixmap(overlay)
        else:
            overlay_image = self.numpy_to_qpixmap(overlay)

        overlay_image = self.create_transparent_overlay(overlay_image)

        if self.image_item:
            self.scene.removeItem(self.image_item)
        if self.overlay_item:
            self.scene.removeItem(self.overlay_item)

        self.image_item = QtWidgets.QGraphicsPixmapItem(self.image)
        self.scene.addItem(self.image_item)
        self.overlay_item = QtWidgets.QGraphicsPixmapItem(overlay_image)
        self.scene.addItem(self.overlay_item)

    def numpy_to_qpixmap(self, array):
        if array.ndim == 2:  # Grayscale image
            height, width = array.shape
            bytes_per_line = width
            image = QtGui.QImage(array.data, width, height, bytes_per_line, QtGui.QImage.Format_Grayscale8)
        elif array.ndim == 3:  # RGB image
            height, width, channel = array.shape
            if channel == 3:  # RGB
                bytes_per_line = 3 * width
                image = QtGui.QImage(array.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        else:
            raise ValueError("Unsupported image format")
        return QtGui.QPixmap.fromImage(image)

    def create_transparent_overlay(self, pixmap):
        image = pixmap.toImage().convertToFormat(QtGui.QImage.Format_ARGB32)
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                alpha = QtGui.qAlpha(pixel)
                if alpha > 0:
                    alpha = int(alpha * 0.7)  # Adjust overlay opacity as needed
                    image.setPixel(x, y, QtGui.qRgba(QtGui.qRed(pixel), QtGui.qGreen(pixel), QtGui.qBlue(pixel), alpha))
        return QtGui.QPixmap.fromImage(image)

    def resizeEvent(self, event):
        super(ImageOverlayWidget, self).resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Image Overlay Example")
        #self.setGeometry(100, 100, 800, 600)

        # Example images as numpy arrays (replace with your actual images)
        image_array = np.random.randint(0, 255, size=(600, 800, 3), dtype=np.uint8)
        overlay_array = np.random.randint(0, 255, size=(600, 800, 3), dtype=np.uint8)

        self.image_widget = ImageOverlayWidget()
        self.setCentralWidget(self.image_widget)
        self.image_widget.set_images(image_array, overlay_array)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
