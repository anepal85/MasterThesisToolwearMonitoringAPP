import os
import cv2
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSlot
from database.operations.dino_image.dino_image_operation import DinoImageOperation
from database.operations.process_number.process_number_operation import CompletedProcessNumberOperation
from database.operations.toolwear_damage.toolwear_damage_operation import ToolWearDamageOperation
from database.operations.userinput_toolwear.userinput_toolwear_operation import UserInputToolWearOperation
from image_writer.writer import ImageWriterWorker, ensure_directory_exists, generate_dynamic_filename, remove_redundant_path
from schemas.dino_image import DinoImageModel
from schemas.toolwear_damage import ToolWearDamageModel
from schemas.user import UserModel
from segmentation.toolwear_caclulator.pixel_calculator import PixelCalculator
from segmentation.toolwear_caclulator.toolwear_calculator import calculate_area_mm_square, calculate_max_vertical_height_mm
from ui.home.prediction.interactiveimage.test_someshit import ToastNotification
from ui.home.prediction_worker import PredictionWorker
from ui.home.preprocessing.horizontal_line_detector import MostHorizontalLineDetector
from ui.home.preprocessing.mask_divider import MaskDivider
from utils.draw_largest_contour import draw_contour, draw_prediction_on_image, find_largest_contour, rsize_image_skimage
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import numpy as np
from database.operations.ml_model.ml_model_operation import MLModelOperation
from segmentation.prediction.image_preprocessor import tf_resize_image, squeeze_tensor_to_np
from segmentation.prediction.toolwear_predictor import ToolWearPredictor
from ui.home.dino_camera.live_view import LiveViewWidget
from ui.home.prediction.display_prediction import PredictionDisplayWidget
from utils.tf_image_reader import preprocess_input, tf_add_batch_1
from ui.home.dnx64_python.usb_example import CAMERA_HEIGHT, CAMERA_WIDTH


class HomeWidget(QtWidgets.QWidget):
    def __init__(self, mlmodel_operation: MLModelOperation, user_model: UserModel,
                 userinput_toolwear_operation: UserInputToolWearOperation,
                 process_number_operation : CompletedProcessNumberOperation,
                 toolwear_damage_operation : ToolWearDamageOperation, 
                 dino_image_operation : DinoImageOperation) -> None:
        super(HomeWidget, self).__init__()

        self.mlmodel_operation = mlmodel_operation
        self.user_model = user_model
        self.userinput_toolwear_operation = userinput_toolwear_operation
        self.process_number_operation = process_number_operation
        self.toolwear_damage_operation = toolwear_damage_operation
        self.dino_image_operation = dino_image_operation 

        self.selected_config_id = None
        self.current_input_config_data = None 
        self.toolwear_predictor = None
        self.prediction_worker = None
        self.is_predicting = False
        self.is_image_saved = False 

        self.amr = None
        self.fovx = None
        self.user_selected_frame = None

        self.segmentation_mask_np = None
        self.image_drawn_np = None
        self.pixels_total = None
        self.vb_down_height = None
        self.vb_up_height = None
        self.y_manual = None

        main_layout = QtWidgets.QVBoxLayout(self)

        firs_row_layout = QtWidgets.QHBoxLayout()
        self.second_row_layout = QtWidgets.QHBoxLayout()

        self.live_widget = LiveViewWidget(self.mlmodel_operation)
        self.live_widget.snaped_signal.connect(self.handle_snap)

        firs_row_layout.addWidget(self.live_widget)

        # Initialize prediction widget with static image and prediction
        initial_image_path = r"D:\MA\App\Data\April_2024\April_2024\\3_4\\3_4_100mm.jpg"
        initial_image = preprocess_input(initial_image_path, 3)

        resize_for_horizontal_detection = squeeze_tensor_to_np(tf_resize_image(initial_image, 512, 512))
        self.horizontal_line = self.get_most_horizontal_lines(resize_for_horizontal_detection)[0]

        # self.angle_for_horizontal_line = self.horizontal_line[0]
        # #print(horizonta_line, self.angle_for_horizontal_line)

        initial_image, initial_prediction = self.get_initial_image_and_prediction(initial_image)
        self.prediction_widget = PredictionDisplayWidget(initial_image, initial_prediction, self.horizontal_line)

        # Initialization of ImageWriter 
        self.image_writer_worker = ImageWriterWorker()
        self.image_writer_worker.finished.connect(self.on_image_write_finished)
        self.image_writer_worker.error.connect(self.on_image_write_error)

        self.prediction_widget.horizontal_line_position_changed.connect(self.handle_horizontal_line_positionchanged_by_user)
        self.prediction_widget.save_btn_clicked.connect(self.handle_save_clicked)
        self.prediction_widget.complete_btn_clicked.connect(self.hanlde_process_complete_clicked)

        firs_row_layout.addWidget(self.prediction_widget)
        main_layout.addLayout(firs_row_layout)

    @pyqtSlot(int)
    def update_config_id(self, config_id):
        #print(f'Selected config id {config_id}')
        self.selected_config_id = config_id
        self.current_input_config_data = self.userinput_toolwear_operation.get_user_input_data(self.selected_config_id)

    def get_initial_image_and_prediction(self, initial_image):
        if self.live_widget.current_model:
            initial_prediction, processed_image = self.predict_with_model(initial_image, self.live_widget.current_model)
            segmentation_mask_np = np.squeeze(initial_prediction, axis=0)
            largest_contour = find_largest_contour(segmentation_mask_np)
            im = draw_contour(np.squeeze(processed_image), largest_contour)
            return im, segmentation_mask_np

        return initial_image, np.zeros_like(initial_image)

    def predict_with_model(self, image, model):
        processed_image, processed_image_batched = self.process_image(image, model)
        predictor = self.initialize_predictor(model)
        prediction = predictor.predict(processed_image_batched)
        return prediction, processed_image

    def process_image(self, image, model):
        height, width = model.input_im_height, model.input_im_width
        processed_image = tf_resize_image(image, height, width)
        processed_image_batched = tf_add_batch_1(processed_image)
        return processed_image, processed_image_batched

    def initialize_predictor(self, model):
        selected_model_pydantic = self.mlmodel_operation.convert_db_model_to_pydantic(model)
        return ToolWearPredictor(selected_model_pydantic)

    def handle_snap(self, image, amr, fovx):
        if image is None or self.live_widget.current_model is None or self.is_predicting:
            return
        
        self.user_selected_frame = image
        
        if self.selected_config_id is None:
            QMessageBox.warning(self, "Warning", "Select config id in Config Input")
            return

        currently_selected_model = self.live_widget.current_model

        t = preprocess_input(image)
        # this line is working for prediction
        processed_image = tf_add_batch_1(self.np_to_tensor_and_resize(t, currently_selected_model))

        #processed_image = tf_add_batch_1(tf_resize_image(image, currently_selected_model.input_im_height, currently_selected_model.input_im_width))
        ## this line gives processed imag of tensor uint8 type

        if self.toolwear_predictor is None or self.toolwear_predictor.model != currently_selected_model:
            self.toolwear_predictor = self.initialize_predictor(currently_selected_model)

            if not self.prediction_worker:
                self.prediction_worker = PredictionWorker(self.toolwear_predictor, processed_image)
                self.prediction_worker.result_ready.connect(self.handle_prediction_result)

        #processed_image = tf_add_batch_1(self.np_to_tensor_and_resize(image, currently_selected_model))
        self.amr = amr
        self.fovx = fovx

        print(f"During Snap --> AMR : {self.amr}  FOVx: {self.fovx}")

        if not self.prediction_worker.is_running:
            self.is_predicting = True
            self.prediction_worker.update_image(processed_image)
            self.prediction_worker.start()

    def calculate_updated_vb_for_new_horizontal_line(self, segmentation_mask_np,  horizontal_line, 
                                                     CAMERA_WIDTH = CAMERA_WIDTH, CAMERA_HEIGHT = CAMERA_HEIGHT):
        ## don't go with the name of maskdivider , just reverse them
        pred_up, pred_down = self.divide_prediction_mask(segmentation_mask_np, horizontal_line)

        pred_up_to_original =  rsize_image_skimage(pred_up, CAMERA_WIDTH, CAMERA_HEIGHT)
        pred_down_to_original = rsize_image_skimage(pred_down, CAMERA_WIDTH, CAMERA_HEIGHT)

        pixels_up = self.calculate_max_height(pred_up_to_original, 'up')
        pixels_down = self.calculate_max_height(pred_down_to_original, 'down')

        print(f"During Prediction --> AMR : {self.amr}  FOVx: {self.fovx}")
        #if self.amr is None or self.fovx is None:
            #self.amr , self.fovx = 136.5, 2.37 ### TODO  and no idea whether this is correct or not 

        fovy_current = self.calculate_fovy_from_fovx(self.fovx)

        #print(f"Camera Width {CAMERA_WIDTH} and height {CAMERA_HEIGHT} during vb calculation")
        
        vb_up_height = calculate_max_vertical_height_mm(fovy_current, pixels_up, CAMERA_WIDTH)
        vb_down_height = calculate_max_vertical_height_mm(fovy_current, pixels_down, CAMERA_WIDTH)

        return vb_down_height, vb_up_height

    def handle_prediction_result(self, image_np, tf_segmentation_mask):

        self.is_predicting = False

        self.segmentation_mask_np = np.squeeze(tf_segmentation_mask, axis=0)
        self.image_drawn_np = draw_prediction_on_image(image_np, self.segmentation_mask_np)

        self.horizontal_line = self.get_most_horizontal_lines(image_np)[0]

        self.pixels_total = self.calculate_toolwear_total_area(self.segmentation_mask_np, 'total_area')

        self.vb_down_height, self.vb_up_height = self.calculate_updated_vb_for_new_horizontal_line(
            self.segmentation_mask_np, self.horizontal_line, self.user_selected_frame.shape[1], self.user_selected_frame.shape[0])
        
        self.prediction_widget.update_display(self.image_drawn_np, self.segmentation_mask_np,
                                               self.horizontal_line, self.vb_down_height, self.vb_up_height,
                                                 self.current_input_config_data.definierter_vbmax_value)
        self.y_manual = None 

        # self.prediction_widget.save_btn_clicked.connect(self.handle_save_clicked)
        # self.prediction_widget.complete_btn_clicked.connect(self.hanlde_process_complete_clicked)

    def handle_horizontal_line_positionchanged_by_user(self, new_y):
        if self.segmentation_mask_np is None or self.image_drawn_np is None :
            return
        horizontal_line_with_new_y = (0, new_y)

        self.y_manual = new_y

        self.vb_down_height, self.vb_up_height = self.calculate_updated_vb_for_new_horizontal_line(self.segmentation_mask_np, 
                            horizontal_line_with_new_y, self.user_selected_frame.shape[1], self.user_selected_frame.shape[0])

        self.prediction_widget.update_display(self.image_drawn_np, self.segmentation_mask_np, horizontal_line_with_new_y, 
                                              self.vb_down_height, self.vb_up_height, self.current_input_config_data.definierter_vbmax_value)
        print(f"new horizontal line postion form Homewidget is {new_y}")


    def handle_save_clicked(self, is_bad_prediction):

        if self.user_selected_frame is None:
            QMessageBox.warning(self, "Warning", "No frame selected")
            return
        
        if self.selected_config_id is None:
            QMessageBox.warning(self, "Warning", "Select config id in Config Input")
            return

        if self.pixels_total is None:
            QMessageBox.warning(self, "Warning", "No Toolwear detected")
            return
        try:
            #current_input_config_data = self.userinput_toolwear_operation.get_user_input_data(self.selected_config_id)
            current_image_folder = self.current_input_config_data.images_folder

            fovy = self.calculate_fovy_from_fovx(self.fovx)
            damage_area_in_mm_Square = self.calculate_area_in_mm_square(self.fovx,
                                fovy, self.pixels_total, self.user_selected_frame.shape[1], self.user_selected_frame.shape[0])

        except Exception as e:
            QMessageBox.warning(self, "warning", str(e))

        ### gather all the data to fill ToolwearDamageDB
        ### store it in database
        toolwear_data = ToolWearDamageModel(
            ml_model_id = self.live_widget.current_model.id,
            user_id = self.user_model.id,
            user_data_id = self.selected_config_id,
            damage_area_pixel = self.pixels_total,
            damage_area = damage_area_in_mm_Square,
            damage_up= self.vb_up_height,
            damage_down= self.vb_down_height,
            process_number = self.process_number_operation.get_max_process_number(),
            is_manual = False if self.y_manual is None else True,
            y_algo = int(np.abs(self.horizontal_line[1])),
            y_manual = 0 if self.y_manual is None else int(self.y_manual),
            created_at= datetime.now(),
            correct_prediction= not is_bad_prediction)

        is_toolwear_saved = self.toolwear_damage_operation.create_toolwear_damage(toolwear_data)

        if is_toolwear_saved:
            # Ensure the necessary directories exist
            images_dir = os.path.join(current_image_folder, 'images', str(toolwear_data.process_number))
            masks_dir = os.path.join(current_image_folder, 'masks', str(toolwear_data.process_number))

            ensure_directory_exists(images_dir)
            ensure_directory_exists(masks_dir)

            image_file_path = generate_dynamic_filename(images_dir, is_toolwear_saved.id)+'.jpg'
            mask_file_path = generate_dynamic_filename(masks_dir, is_toolwear_saved.id)+'.tif'

            self.image_writer_worker.update_task(self.user_selected_frame, image_file_path, 
                                                self.segmentation_mask_np, mask_file_path)
            
            image_file_path_encoded = remove_redundant_path(image_file_path, current_image_folder)

            #create dinoimage_image model
            # create dinoimage_image model
            dino_image_model = DinoImageModel(
                toolwear_damage_id=is_toolwear_saved.id, 
                image_path=image_file_path_encoded, 
                magnification=self.amr, 
                fovx=self.fovx, 
                fovy=fovy, 
                created_at=datetime.now())
            
            self.dino_image_operation.create_dino_image(dino_image_model)

    def on_image_write_finished(self):
        print("Success ! Image saved successfully!")
        #QMessageBox.information(self, "Success", "Image saved successfully")
        test = ToastNotification("Image saved successfully!", 3000, 'black', self.prediction_widget)
        test.show_toast()

    def on_image_write_error(self, error_message):
        print(f"Error ! Failed to save image: {error_message}")
        QMessageBox.critical(self, "Error", f"Failed to save data: {error_message}")

    def hanlde_process_complete_clicked(self):
        if self.process_number_operation.complete_process():
            return QMessageBox.information(self, "Success", f"Process completed successfully !")
        else:
            return QMessageBox.critical(self, "Error", f"Failed to complete process !")

    def np_to_tensor_and_resize(self, image, model):
        return tf_resize_image(tf.convert_to_tensor(image, dtype=tf.float32), model.input_im_height, model.input_im_width)

    def tf_resize_image(image: tf.Tensor, model) -> tf.Tensor:
        return tf.image.resize(image, model.input_im_height, model.input_im_width)

    def closeEvent(self, event):
        for worker in [self.prediction_worker, self.image_writer_worker]:
            if worker:
                worker.stop()
        super(HomeWidget, self).closeEvent(event)

    def get_most_horizontal_lines(self, image: np.array) -> list:
        """Get the most horizontal lines for the given image."""
        detector = MostHorizontalLineDetector(image)
        return detector.find_most_horizontal_line()

    def divide_prediction_mask(self, mask, horizontal_line):
        return MaskDivider(horizontal_line).divide_mask(mask)

    def calculate_max_height(self, prediction_mask:np.array, fname)->int:
        return PixelCalculator(prediction_mask, fname).get_max_height()

    def calculate_toolwear_total_area(self, prediction_mask:np.array, fname)->int:
        return PixelCalculator(prediction_mask, fname).get_segmented_object_area()


    def calculate_fovy_from_fovx(self, fovx:float)->float:
        return (fovx * CAMERA_HEIGHT) / CAMERA_WIDTH

    def calculate_area_in_mm_square(self, fovx, fovy, total_pixels_nr, im_width, im_height):
        return calculate_area_mm_square(fovx, fovy, total_pixels_nr, im_width, im_height)


    # def handle_prediction_result(self, image, segmentation_mask_np):
    #     self.is_predicting = False
    #     ## here i need to calculate the pixels
    #     prediction_resized_to_old = tf_resize_image(segmentation_mask_np, CAMERA_WIDTH, CAMERA_HEIGHT)
    #     pred_up, pred_down = self.divide_prediction_mask(prediction_resized_to_old, )

    #     self.prediction_widget.update_display(image, segmentation_mask_np)

    # def handle_prediction_result(self, image_np, tf_segmentation_mask):
    #     self.is_predicting = False

    #     #print(image.dtype, image.shape)
    #     segmentation_mask_np = np.squeeze(tf_segmentation_mask, axis=0)
    #     image_drawn_np = draw_prediction_on_image(image_np, segmentation_mask_np)

    #     ## here i need to calculate the pixels
    #     #prediction_resized_to_back = tf_resize_image(tf_segmentation_mask[0], CAMERA_WIDTH, CAMERA_HEIGHT)

    #     #print(self.get_most_horizontal_lines(image_np))

    #     horizontal_line = self.get_most_horizontal_lines(image_np)[0]

    #     ## don't go with the name of maskdivider , just reverse them
    #     pred_down, pred_up = self.divide_prediction_mask(segmentation_mask_np, horizontal_line)

    #     pred_up_to_original =  rsize_image_skimage(pred_up, CAMERA_WIDTH, CAMERA_HEIGHT)
    #     pred_down_to_original = rsize_image_skimage(pred_down, CAMERA_WIDTH, CAMERA_HEIGHT)

    #     #plot_and_save_figure(pred_up_to_original, pred_down_to_original)

    #     pixels_up = self.calculate_max_height(pred_up_to_original, 'up')
    #     pixels_down = self.calculate_max_height(pred_down_to_original, 'down')

    #     #toatal_toolwear_pixel_area = self.calculate_toolwear_total_area(prediction_resized_to_back)

    #     if self.amr is None or self.fovx is None:
    #         self.amr , self.fovx = 164.87, 2.37
    #         #return
    #     fovy_current = self.calculate_fovy_from_fovx(self.fovx)

    #     vb_up_height = calculate_max_vertical_height_mm(fovy_current, pixels_up, CAMERA_WIDTH)
    #     vb_down_height = calculate_max_vertical_height_mm(fovy_current, pixels_down, CAMERA_WIDTH)

    #     #toatal_toolwear_pixel_area_in_mm2 = calculate_area_mm_square(fovx_current, fovy_current, toatal_toolwear_pixel_area)
    #     print(self.amr, self.fovx, fovy_current, pixels_up, pixels_down,vb_up_height, vb_down_height)

    #     self.prediction_widget.update_display(image_drawn_np, segmentation_mask_np, horizontal_line, vb_down_height, vb_up_height)

    #     self.prediction_widget.save_btn_clicked.connect(self.handle_save_clicked)
    #     self.prediction_widget.complete_btn_clicked.connect(self.hanlde_process_complete_clicked)


def save_prediction_mask(prediction_mask, file_path):
    # Squeeze the mask to remove any unnecessary dimensions
    squeezed_mask = np.squeeze(prediction_mask, axis=0)

    # Convert to uint8 and scale to 255 if necessary
    if squeezed_mask.dtype != np.uint8:
        squeezed_mask = (squeezed_mask * 255).astype(np.uint8)

    # Ensure it's a single channel image
    if len(squeezed_mask.shape) == 3 and squeezed_mask.shape[2] == 1:
        squeezed_mask = squeezed_mask[:, :, 0]

    # Save the mask as a grayscale image
    cv2.imwrite(file_path, squeezed_mask)
    print("test.png written")

#     def get_initial_image_and_prediction(self):
#         initial_image_path = r"D:\MA\App\Data\April_2024\April_2024\\3_4\\3_4_100mm.jpg"
#         initial_image = preprocess_input(initial_image_path, 3)
#         if self.live_widget.current_model:
#             height, width = self.live_widget.current_model.input_im_height, self.live_widget.current_model.input_im_width
#             processed_image = tf_resize_image(initial_image, height, width)
#             processed_image_batched = tf_add_batch_1(processed_image)
#             selected_model_pydantic = self.mlmodel_operation.convert_db_model_to_pydantic(self.live_widget.current_model)
#             self.toolwear_predictor = ToolWearPredictor(selected_model_pydantic)
#             initial_prediction = self.toolwear_predictor.predict(processed_image_batched)
#             segmentation_mask_np = np.squeeze(initial_prediction, axis=0)
#             largest_contour = find_largest_contour(segmentation_mask_np)
#             im = draw_contour(np.squeeze(processed_image), largest_contour)
#             return im, segmentation_mask_np
#         return initial_image_path, np.zeros_like(initial_image)

#     def np_to_tensor_and_resize(self, image, model):
#         return tf_resize_image(tf.convert_to_tensor(image, dtype=tf.float32), model.input_im_height, model.input_im_width)

#     def handle_snap(self, image):
#         if image is None or self.live_widget.current_model is None or self.is_predicting:
#             return

#         currently_selected_model = self.live_widget.current_model

#         # Load the predictor model only once
#         if self.toolwear_predictor is None or self.toolwear_predictor.model != currently_selected_model:
#             selected_model_pydantic = self.mlmodel_operation.convert_db_model_to_pydantic(currently_selected_model)
#             self.toolwear_predictor = ToolWearPredictor(selected_model_pydantic)
#             if not self.prediction_worker:
#                 self.prediction_worker = PredictionWorker(self.toolwear_predictor, image)
#                 self.prediction_worker.result_ready.connect(self.handle_prediction_result)

#         processed_image = tf_add_batch_1(self.np_to_tensor_and_resize(image, currently_selected_model))

#         if not self.prediction_worker.is_running:
#             self.is_predicting = True
#             self.prediction_worker.update_image(processed_image)
#             self.prediction_worker.start()

#     def handle_prediction_result(self, image, segmentation_mask_np):
#         self.is_predicting = False
#         self.prediction_widget.update_display(image, segmentation_mask_np)

# def resize_segmmask_back_tooriginal(seg_mask: tf.Tensor, width: int = 512, height: int = 512) -> tf.Tensor:
#     return tf.image.resize(seg_mask[0], (height, width), method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)[tf.newaxis]

# def plot_and_save_figure(segmentation_mask_np, processed_age):
#     # Plot the figure
#     fig, ax = plt.subplots(1, 2, figsize=(12, 6))
#     ax[0].imshow(processed_age)
#     ax[0].set_title('Processed Image')
#     ax[1].imshow(segmentation_mask_np, cmap='viridis', alpha=0.7)
#     # Save the figure
#     save_path = 'test.png'
#     plt.savefig(save_path)
#     plt.close(fig)  # Close the figure to release resources
#     return save_path

# def overlay_mask(image, prediction_mask, mask_color=(0, 255, 255), alpha = 1):

#     # Step 4: Create a colorful mask based on the masked array
#     colored_mask = np.zeros_like(image)
#     colored_mask[prediction_mask>0] = mask_color

#     overlayed_image = cv2.addWeighted(image, 1, colored_mask, alpha, 0)

#     return overlayed_image


