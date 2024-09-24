from skimage.measure import label, regionprops
import numpy as np 
from skimage.draw import rectangle_perimeter

from ui.home.preprocessing.horizontal_line_detector import plot_and_save_figure

class PixelCalculator:
    def __init__(self, segmentation_mask, fname):
        assert segmentation_mask.shape[-1] == 1, "Mask must be gray"
        self.segmentation_mask = segmentation_mask
        self._segmented_object_area = None
        self._max_height = None
        self._drawn_image = np.dstack([self.segmentation_mask.squeeze()] * 3)
        self.fname = fname

    def _calculate_segmented_properties(self):
        # if not isinstance(self.segmentation_mask, np.ndarray): 
        #     #labeled_mask = label(np.squeeze(self.segmentation_mask, axis = 2))
        #     labeled_mask = label(self.segmentation_mask.squeeze())

        labeled_mask = label(self.segmentation_mask.squeeze())
        props = regionprops(labeled_mask)
        
        max_area = 0
        max_height = 0

        for prop in props:
            if prop.area > max_area:
                max_area = prop.area
                bbox = prop.bbox
                if len(bbox) == 4:
                    min_row, min_col, max_row, max_col = bbox
                else:
                    min_row, min_col, min_depth, max_row, max_col, max_depth = bbox
                
                rr, cc = rectangle_perimeter((min_row, min_col), end=(max_row - 1, max_col - 1), shape=self._drawn_image.shape)
                self._drawn_image[rr, cc] = [255, 0, 0]  # Red color for bounding boxes 
                #plot_and_save_figure(self._drawn_image, self.segmentation_mask, self.fname)
                #min_row, _, max_row, _ = prop.bbox
                height = max_row - min_row
                if height > max_height:
                    max_height = height


        self._segmented_object_area = max_area
        self._max_height = max_height

    def get_segmented_object_area(self) -> int:
        if self._segmented_object_area is None:
            self._calculate_segmented_properties()
        return self._segmented_object_area

    def get_max_height(self) -> int:
        if self._max_height is None:
            self._calculate_segmented_properties()
        return self._max_height
    
    def get_drawn_image(self):
        if self._drawn_image is None:
            self._calculate_segmented_properties()
        return self._drawn_image




# from skimage.measure import label, regionprops
# import tensorflow as tf

# class PixelCalculator:
#     def __init__(self, segmentation_mask: tf.Tensor):
#         assert segmentation_mask.shape[-1] == 1, "Mask must be gray"
#         self.segmentation_mask = segmentation_mask
#         self.segmented_object_area = None
#         self.max_height = None

#     def calculate_segmented_object_area_and_height(self):
#         labeled_mask = label(self.segmentation_mask.squeeze())
#         props = regionprops(labeled_mask)
        
#         segmented_object_area = 0
#         max_height = 0 

#         for prop in props:
#             if prop.area > segmented_object_area:
#                 segmented_object_area = prop.area
#                 min_row, _, max_row, _ = prop.bbox
#                 height = max_row - min_row
#                 if height > max_height:
#                     max_height = height
        
#         self.segmented_object_area = segmented_object_area
#         self.max_height = max_height

#         return segmented_object_area, max_height
