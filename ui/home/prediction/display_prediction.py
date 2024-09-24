from PyQt5 import QtWidgets , QtCore
import numpy as np
from ui.home.prediction.display_vb.vb_displayer import VBDisplayer2
from ui.home.prediction.interactiveimage.test_2 import ImageWithLineView
from PyQt5.QtCore import pyqtSignal

class PredictionDisplayWidget(QtWidgets.QWidget):
    save_btn_clicked = pyqtSignal(bool)
    complete_btn_clicked = pyqtSignal()
    horizontal_line_position_changed = pyqtSignal(float)

    def __init__(self, image:np.array, pred_mask: np.array, horizontal_line) -> None:
        super(PredictionDisplayWidget, self).__init__()

        # Set the font size for the widget
        #self.setStyleSheet("font-size: 12px;")
        # Set the font size for the widget
        self.setStyleSheet("font-size: 18px;")
        # Set the size policy to expanding
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


        main_layout = QtWidgets.QVBoxLayout(self)

        heading_label = QtWidgets.QLabel("Predicted ToolWear")
        # Center the text horizontally
        heading_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Customize the font of the heading
        font = heading_label.font()
        font.setPointSize(28)  # Set a larger font size for the heading
        heading_label.setFont(font)
        heading_label.setContentsMargins(0, 10, 0, 10)  # (Left, Top, Right, Bottom)

        # Add the heading label to the main layout at the top
        main_layout.addWidget(heading_label)

        self.firs_row_layout = QtWidgets.QHBoxLayout()
        self.second_row_layout = QtWidgets.QHBoxLayout()
        self.third_row_layout = QtWidgets.QHBoxLayout()
        
        self.image = image
        self.pred_mask = pred_mask 

        self.most_horizontal_line = horizontal_line #self.get_most_horizontal_lines(self.image)
        self.my_canvas = ImageWithLineView(self.image, self.most_horizontal_line)
        #self.my_canvas.line_controller.positionChanged.connect(self.on_horizontal_line_position_changed)
        self.firs_row_layout.addWidget(self.my_canvas)
        
        self.bad_prediction_checkbox = QtWidgets.QCheckBox("Needs Correction")
        self.vb_displayer = VBDisplayer2(self)
        
        self.second_row_layout.addWidget(self.bad_prediction_checkbox, 0)
        self.second_row_layout.addWidget(self.vb_displayer)

        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.second_row_layout.addItem(spacerItem)

        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setFixedHeight(40)
        ## handle it in home widget 
        self.save_btn.clicked.connect(self.emit_save_btn_clicked)

        self.process_complete_btn =  QtWidgets.QPushButton("Complete")
        self.process_complete_btn.setFixedHeight(40)
        ## handle it in home widget 
        self.process_complete_btn.clicked.connect(self.complete_btn_clicked.emit)

        self.third_row_layout.addWidget(self.save_btn)
        self.third_row_layout.addWidget(self.process_complete_btn)

        main_layout.addLayout(self.firs_row_layout)
        main_layout.addLayout(self.second_row_layout)
        main_layout.addLayout(self.third_row_layout)

    def update_display(self, new_image: np.array, new_pred_mask: np.array, horizontal_line, vb_below : float = 0, vb_up:float = 0, 
                       vb_max_threshold = 0.2) -> None:
        """Update the display with a new image and its prediction mask."""
        self.image = new_image
        self.pred_mask = new_pred_mask

        self.most_horizontal_line = horizontal_line
        self.my_canvas.update_canvas(self.image, self.most_horizontal_line)
        self.vb_displayer.update_values(vb_up, vb_below, vb_max_threshold) 

    def on_horizontal_line_position_changed(self, new_y):
        self.horizontal_line_position_changed.emit(new_y)

    def emit_save_btn_clicked(self):
        is_checked = self.bad_prediction_checkbox.isChecked()
        self.save_btn_clicked.emit(is_checked)

