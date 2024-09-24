from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np

from ui.home.prediction.interactiveimage.test_moveable_line import tf_resize_image
from utils.tf_image_reader import squeeze_tensor_to_np

#from utils.draw_largest_contour import draw_contour, find_largest_contour

class PredictionWorker(QThread):
    result_ready = pyqtSignal(np.ndarray, np.ndarray)

    def __init__(self, predictor, image):
        super().__init__()
        self.predictor = predictor
        self.image = image
        self.is_running = False

    def run(self):
        if self.is_running:
            return
        self.is_running = True
        try:
            #print(self.image.dtype, self.image.shape)
            prediction_mask = self.predictor.predict(self.image)
            #print(prediction_mask.shape, prediction_mask.dtype)
            #tf.keras.utils.save_img('test.png', np.squeeze(prediction_mask, axis=0))
            #save_prediction_mask(prediction_mask, 'test.jpg')
            
            # segmentation_mask_np = np.squeeze(prediction_mask, axis=0)

            # largest_contour = find_largest_contour(segmentation_mask_np)
            # im = draw_contour(np.squeeze(self.image), largest_contour)
            
            #segmentation_mask_np = np.squeeze(prediction_mask, axis=0)
            #self.result_ready.emit(squeeze_tensor_to_np(self.image, axis=0), segmentation_mask_np)
            
            self.result_ready.emit(np.squeeze(self.image, axis=0), prediction_mask)
            #self.result_ready.emit(squeeze_tensor_to_np(tf_resize_image(self.image, 512, 512), axis=0), prediction_mask)
        finally:
            self.is_running = False

    def update_image(self, image):
        self.image = image

    def stop(self):
        if self.isRunning():
            self.wait()







## This was working 

# from PyQt5.QtCore import QThread, pyqtSignal
# import numpy as np

# from utils.draw_largest_contour import draw_contour, find_largest_contour

# class PredictionWorker(QThread):
#     result_ready = pyqtSignal(np.ndarray, np.ndarray)

#     def __init__(self, predictor, image):
#         super().__init__()
#         self.predictor = predictor
#         self.image = image
#         self.is_running = False

#     def run(self):
#         if self.is_running:
#             return
#         self.is_running = True
#         try:
#             print(self.image.dtype, self.image.shape)
#             prediction_mask = self.predictor.predict(self.image)
#             #print(prediction_mask.shape, prediction_mask.dtype)
#             #tf.keras.utils.save_img('test.png', np.squeeze(prediction_mask, axis=0))
#             #save_prediction_mask(prediction_mask, 'test.jpg')
#             segmentation_mask_np = np.squeeze(prediction_mask, axis=0)

#             largest_contour = find_largest_contour(segmentation_mask_np)
#             im = draw_contour(np.squeeze(self.image), largest_contour)
            
#             #segmentation_mask_np = np.squeeze(prediction_mask, axis=0)
#             #self.result_ready.emit(squeeze_tensor_to_np(self.image, axis=0), segmentation_mask_np)
            
#             self.result_ready.emit(im, segmentation_mask_np)
#         finally:
#             self.is_running = False

#     def update_image(self, image):
#         self.image = image

#     def stop(self):
#         if self.isRunning():
#             self.wait()