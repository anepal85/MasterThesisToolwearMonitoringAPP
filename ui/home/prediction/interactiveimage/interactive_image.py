import numpy as np
import cv2
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QSlider, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap

class InteractiveImageWidget(QWidget):
    def __init__(self, image_np, most_horizontal_lines):
        super().__init__()
        self.image_np = image_np
        self.most_horizontal_lines = most_horizontal_lines
        self.current_index = 0

        layout = QVBoxLayout(self)

        self.label_above_line = QLabel(self)
        self.label_below_line = QLabel(self)

        layout.addWidget(self.label_above_line)
        layout.addWidget(self.label_below_line)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.most_horizontal_lines) - 1)
        self.slider.valueChanged.connect(self.update_line)
        layout.addWidget(self.slider)

        self.update_line(0)

    def update_line(self, index):
        most_horizontal_line = self.most_horizontal_lines[index]
        angle, dist = most_horizontal_line

        # Create an image with the line drawn on it
        image_with_line = self.image_np.copy()
        y0 = int((dist - 0 * np.cos(angle)) / np.sin(angle))
        y1 = int((dist - image_with_line.shape[1] * np.cos(angle)) / np.sin(angle))
        cv2.line(image_with_line, (0, y0), (image_with_line.shape[1], y1), (0, 0, 255), 2)

        # Generate masks based on the most horizontal line
        mask_above_line, mask_below_line = self.generate_masks(most_horizontal_line)

        # Display the updated images
        image_above_line_pixmap = QPixmap("D:\MA\App\Data\April_2024\April_2024\\3_4\\3_4_100mm.jpg")
        image_below_line_pixmap = QPixmap("")

        self.label_above_line.setPixmap(image_above_line_pixmap)  # Display image above the line
        self.label_below_line.setPixmap(image_below_line_pixmap)  # Display image below the line

        # Update current index
        self.current_index = index

    def generate_masks(self, most_horizontal_line):
        angle, dist = most_horizontal_line

        # Create an empty mask for pixels above the most horizontal line
        mask_above_line = np.zeros_like(self.image_np, dtype=np.uint8)

        # Iterate over each pixel in the image
        for y in range(self.image_np.shape[0]):
            # Calculate the x-coordinate (column index) of the line at this y-coordinate
            x = int((y * np.sin(angle)) + abs(dist))

            # Set the pixels above the line to 1 in the mask
            mask_above_line[y, :x] = self.image_np[y, :x]

        # Create a mask for pixels below the most horizontal line
        mask_below_line = np.where(mask_above_line == 0, self.image_np, 0)

        return mask_above_line, mask_below_line
