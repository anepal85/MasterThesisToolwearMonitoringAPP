from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal 
from database.operations.ml_model.ml_model_operation import MLModelOperation
from ui.home.dino_camera.camera import CameraWidget
from ui.home.dino_camera.camera_thread import CameraThread
import numpy as np
from ui.home.dnx64_python.usb_example import get_amr, get_fov_mm 
import cv2 

class LiveViewWidget(QtWidgets.QWidget):    
    snaped_signal = pyqtSignal(np.ndarray, float, float)

    def __init__(self, mlmodel_operation: MLModelOperation) -> None:
        super(LiveViewWidget, self).__init__()

        self.camera_is_on = False
        self.mlmodel_operation = mlmodel_operation
        
        # Set the font size for the widget
        self.setStyleSheet("font-size: 18px;")
        
        # Set the size policy to expanding
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


        # Create the layout for the widget
        layout = QtWidgets.QVBoxLayout(self)
        
        # Create the first row containing labels and combo boxes
        row1 = QtWidgets.QHBoxLayout()
        ### Camera Enable 
        self.enable_camera_button = QtWidgets.QPushButton('ON', self)
        self.enable_camera_button.setCheckable(True)
        self.enable_camera_button.toggled.connect(self.toggle_camera)

        row1.addWidget(self.enable_camera_button)
        
        label1 = QtWidgets.QLabel('Select Segmentation MODEl: ', self)
        self.combo1 = QtWidgets.QComboBox(self)
        self.combo1.addItems(self.fetch_model_names())
        self.combo1.currentIndexChanged.connect(self.change_model)
        self.current_model = self.mlmodel_operation.get_by_name(self.combo1.currentText())
        row1.addWidget(label1)
        row1.addWidget(self.combo1)

        self.change_button = QtWidgets.QPushButton('Change Model', self)
        #submit_button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)  # Set size policy
        self.change_button.clicked.connect(self.change_model)
        row1.addWidget(self.change_button)

        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        row1.addItem(spacerItem)
        # Add stretchable space to fill the remaining width
        row1.addStretch(1)
        layout.addLayout(row1)

        # Create the second row containing Plot
        row2 = QtWidgets.QHBoxLayout()
        self.camera_widget = CameraWidget()
        self.camera_thread = CameraThread()
        self.camera_thread.image_signal.connect(self.on_new_frame)
      
        row2.addWidget(self.camera_widget)
        layout.addLayout(row2)

        row3 = QtWidgets.QHBoxLayout()

        self.snap_button = QtWidgets.QPushButton('Snap', self)
        self.snap_button.setFixedHeight(40)
        self.snap_button.clicked.connect(self.take_snapshot)

        # Add the upload button
        self.upload_button = QtWidgets.QPushButton('Upload', self)
        self.upload_button.setFixedHeight(40)
        self.upload_button.clicked.connect(self.upload_image)

        row3.addWidget(self.snap_button)
        row3.addWidget(self.upload_button)

        layout.addLayout(row3)

        self.setLayout(layout)

        #self.enable_camera_button.clicked.connect(self.start_camera_thread)

    def fetch_model_names(self)->list[str]:
        return [el.name for el in self.mlmodel_operation.get_all_mlmodel()]
    
    def toggle_camera(self, checked):
        if checked:
            self.enable_camera_button.setText('Off')
            self.start_camera()
        else:
            self.enable_camera_button.setText('On')
            self.stop_camera()

    def start_camera(self):
        self.camera_thread.start()
        self.camera_is_on = True

    def stop_camera(self):
        self.camera_thread.stop()
        self.camera_is_on = False


    def take_snapshot(self):
        if not self.camera_is_on:
            return 
        frame = self.camera_widget.get_current_frame()
        if frame is not None:
            amr = get_amr() #164.87 #
            fovx = get_fov_mm() #2.37 #  
            #amr = 136.5#
            #fovx = 2.92 #  

            self.snaped_signal.emit(frame, amr, fovx)


    def start_camera_thread(self, checked):
        if checked:
            self.enable_camera_button.setText('Off')
            self.camera_thread.start()
            self.camera_is_on = True 
        else:
            self.enable_camera_button.setText('On')
            self.camera_thread.stop()
            self.camera_is_on = False

    def change_model(self):
        """Callback function for changine the model"""
        self.combo1.currentIndexChanged.connect(self.handle_model_selection) 

    def handle_model_selection(self, index):
        """Handle the selection of a model from the combo box."""
        # Retrieve the selected model name
        selected_model_name = self.combo1.currentText()
        try: 
            self.current_model = self.mlmodel_operation.get_by_name(selected_model_name)
        except Exception as e:
            QtWidgets.QMessageBox.warning(str(e))

    def resizeEvent(self, event):
        # Resize the camera widget when the main window is resized
        super().resizeEvent(event)
        self.camera_widget.setMinimumSize(1, 1)

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()

    def on_new_frame(self, frame):
        #frame = (frame*255).astype(np.uint8)
        self.camera_widget.set_image(frame)

    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Upload Image", "", "Image Files (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            frame = self.load_image(file_path)
            if frame is not None:
                self.camera_widget.set_image(frame)
                try:
                    amr =  get_amr() #136.5#
                    fovx =  get_fov_mm() #2.92 # 
                except OSError as e:
                    amr =  136.5#
                    fovx =  2.92 # 
                self.snaped_signal.emit(frame, amr, fovx)

    def load_image(self, file_path):
        image = cv2.imread(file_path, 1)
        if image is not None:
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        else:
            QtWidgets.QMessageBox.warning(self, "Image Load Error", "Failed to load the image.")
            return None
    