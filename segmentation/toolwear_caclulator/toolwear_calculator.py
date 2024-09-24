def calculate_max_vertical_height_mm(fovy: float, max_height_pixels: int, image_width_pixels: int) -> float:
    """
    Calculate the maximum vertical height in millimeters.
    
    :param fovy: Field of view in the y direction in millimeters.
    :param max_height_pixels: Number of pixels in the maximum height.
    :return: Maximum vertical height in millimeters.
    """
    if image_width_pixels == 0:
        return 0 
    pixel_size_y_mm = fovy / image_width_pixels
    max_vertical_height_mm = max_height_pixels * pixel_size_y_mm
    return round(max_vertical_height_mm, 5)

def calculate_area_mm_square(fovx: float, fovy: float, segmented_object_area_pixels: int, image_width_pixels:int , image_height_pixels:int) -> float:
    """
    Calculate the area in square millimeters.
    
    :param fovx: Field of view in the x direction in millimeters.
    :param fovy: Field of view in the y direction in millimeters.
    :param segmented_object_area_pixels: Number of pixels in the segmented object area.
    :return: Area in square millimeters.
    """
    if image_width_pixels == 0 or image_height_pixels == 0:
        return 0 
    pixel_size_x_mm = fovx / image_height_pixels
    pixel_size_y_mm = fovy / image_width_pixels
    area_mm_square = segmented_object_area_pixels * (pixel_size_x_mm * pixel_size_y_mm)
    return round(area_mm_square, 5)




# from schemas.camera_specification import CameraSpecs
# from toolwear_caclulator.pixel_calculator import PixelCalculator  

# class ToolWearCalculator:
#     def __init__(self, camera_specs: CameraSpecs, pixel_converter: PixelCalculator):
#         self.camera_specs = camera_specs
#         self.pixel_converter = pixel_converter
#         self.magnification_index =  0 
#         self.segmented_object_area_pixels, self.max_height_pixels = self.pixel_converter.calculate_segmented_object_area_and_height()

#     def calculate_max_vertical_height_mm(self) -> float:
#         #magnification_index = self.camera_specs.magnification.index(self.pixel_converter.magnification)
#         field_of_view_mm = self.camera_specs.field_of_view[self.magnification_index]

#         #pixel_size_x_mm = field_of_view_mm[0] / self.pixel_converter.segmentation_mask.shape[1]
#         pixel_size_y_mm = field_of_view_mm[1] / self.pixel_converter.segmentation_mask.shape[0]

#         max_vertical_height_mm = self.max_height_pixels * pixel_size_y_mm

#         return max_vertical_height_mm

#     def calculate_area_mm_square(self) -> float:
#         #magnification_index = self.camera_specs.magnification.index(self.magnification_index)
#         field_of_view_mm = self.camera_specs.field_of_view[self.magnification_index]

#         pixel_size_x_mm = field_of_view_mm[0] / self.pixel_converter.segmentation_mask.shape[1]
#         pixel_size_y_mm = field_of_view_mm[1] / self.pixel_converter.segmentation_mask.shape[0]

#         area_mm_square = self.segmented_object_area_pixels * (pixel_size_x_mm * pixel_size_y_mm)

#         return area_mm_square