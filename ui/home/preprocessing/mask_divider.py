import numpy as np

from ui.home.preprocessing.horizontal_line_detector import plot_and_save_figure

# class MaskDivider:
#     def __init__(self, most_horizontal_line):
#         self.most_horizontal_line = most_horizontal_line

#     def divide_mask(self, prediction_mask_original):
#         # Extract angle and distance from the most horizontal line tuple
#         angle, dist = self.most_horizontal_line

#         # Create an empty mask for pixels above the most horizontal line
#         mask_above_line = np.zeros_like(prediction_mask_original, dtype=np.uint8)

#         # Iterate over each pixel in the image
#         for y in range(prediction_mask_original.shape[0]):
#             # Calculate the x-coordinate (column index) of the line at this y-coordinate
#             x = int((y * np.sin(angle)) + abs(dist))

#             # Set the pixels above the line to 1 in the mask
#             mask_above_line[y, :x] = prediction_mask_original[y, :x]

#         # Create a mask for pixels below the most horizontal line
#         mask_below_line = np.where(mask_above_line == 0, prediction_mask_original, 0)

#         #plot_and_save_figure(mask_below_line, mask_below_line, 'beloooow')
#         #plot_and_save_figure(mask_above_line, mask_above_line, 'abooove')

#         return mask_above_line, mask_below_line



class MaskDivider:
    def __init__(self, most_horizontal_line):
        self.most_horizontal_line = most_horizontal_line

    def divide_mask(self, prediction_mask_original):
        # Extract distance (rho) from the most horizontal line tuple
        _, dist = self.most_horizontal_line

        # Convert the distance to an integer y-coordinate
        y_coord = int(abs(dist))

        # Ensure y_coord is within the bounds of the image
        y_coord = min(max(y_coord, 0), prediction_mask_original.shape[0] - 1)

        # Create masks for above and below the horizontal line
        mask_above_line = np.zeros_like(prediction_mask_original, dtype=np.uint8)
        mask_below_line = np.zeros_like(prediction_mask_original, dtype=np.uint8)

        # Set the masks
        mask_above_line[:y_coord, :] = prediction_mask_original[:y_coord, :]
        mask_below_line[y_coord:, :] = prediction_mask_original[y_coord:, :]

        #plot_and_save_figure(mask_below_line, mask_below_line, 'beloooow')
        #plot_and_save_figure(mask_above_line, mask_above_line, 'abooove')

        return mask_above_line, mask_below_line