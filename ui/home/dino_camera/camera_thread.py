import time
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from ui.home.dnx64_python.usb_example import initialize_camera, microscope , DEVICE_INDEX

class CameraThread(QThread):
    image_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = False
        self._fps = 10  # Default FPS
        self.microscope = microscope
        self.capture = None
        self.initialize_camera_and_microscope()  # Initialize here

    def initialize_camera_and_microscope(self):
        self.microscope.SetVideoDeviceIndex(DEVICE_INDEX)
        self.microscope.Init()
        self.capture = initialize_camera()

    def set_fps(self, fps):
        self._fps = fps

    def run(self):
        self._is_running = True

        if not self.capture.isOpened():
            print('Error opening the camera device.')
            return

        while self._is_running:
            start_time = time.time()
            ret, frame = self.capture.read()
            if ret:
                self.image_signal.emit(frame)

            elapsed_time = time.time() - start_time
            sleep_time = max(0, (1 / self._fps) - elapsed_time)
            time.sleep(sleep_time)

        self.capture.release()

    def stop(self):
        self._is_running = False
        self.wait()



# import cv2
# import numpy as np
# from PyQt5.QtCore import QThread, pyqtSignal

# from ui.home.dnx64_python.usb_example import initialize_camera, microscope , DEVICE_INDEX

# class CameraThread(QThread):
#     """
#     Thread class for capturing frames from a camera.

#     This class extends the QThread class to create a separate thread for capturing frames from a camera.
#     It continuously reads frames from the camera and emits them as signals. It also provides a method to stop
#     the thread and release the camera capture object.

#     Signals:
#     - image_signal: emitted when a new frame is captured, sending the frame as a numpy array.

#     """
#     image_signal = pyqtSignal(np.ndarray)
    
#     def __init__(self, parent=None):
#         """
#         Initialize the CameraThread object.

#         :param parent: Parent QObject (default: None)
#         """
#         super().__init__(parent)
        
#         self._is_running = False
#         self.microscope = microscope
    
#     def initialize_microscope(self):
#         if not self.microscope_initialized:
#             self.microscope.SetVideoDeviceIndex(DEVICE_INDEX)
#             self.microscope.Init()
#             self.microscope_initialized = True
        
#     def run(self):
#         self._is_running = True

#         #self.microscope.SetVideoDeviceIndex(DEVICE_INDEX)
#         #self.microscope.Init()
#         self.initialize_microscope()
#         capture =  initialize_camera()

#         if not capture.isOpened():
#             print('Error opening the camera device.')
#             return
        
#         # Continuously read frames from the camera and emit them as signals
#         while self._is_running:
#             ret, frame = capture.read()
#             if ret:
#                 self.image_signal.emit(frame)
        
#         # Release the camera capture object
#         capture.release()
    
#     def stop(self):
#         self._is_running = False
#         self.wait()


# import os 

# class CameraThread(QThread):
#     image_signal = pyqtSignal(np.ndarray)
    
#     def __init__(self, parent=None):
#         """
#         Initialize the ImageEmitterThread object.

#         :param folder_path: Path to the folder containing images.
#         :param parent: Parent QObject (default: None)
#         """
#         super().__init__(parent)
#         self._is_running = False
#         folder_path = r'D:\MA\TestDataForMa\01_Testdaten\S355_2\S355_2'
#         self.image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
#         self.index = 0
        
#     def run(self):
#         self._is_running = True
#         while self._is_running and self.index < len(self.image_files):
#             image_path = self.image_files[self.index]
#             frame = cv2.imread(image_path)
#             if frame is not None:
#                 self.image_signal.emit(frame)
#             self.index += 1

#     def stop(self):
#         self._is_running = False
#         self.wait()