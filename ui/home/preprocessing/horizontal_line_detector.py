import numpy as np
from skimage import color, filters, feature, transform

class MostHorizontalLineDetector:
    def __init__(self, image):
        self.image = image

    def find_most_horizontal_line(self):
        #print(self.image, self.image.shape)
        # Convert the image to grayscale
        gray_image = color.rgb2gray(self.image)

        # Apply Gaussian blur to the grayscale image
        blurred_image = filters.gaussian(gray_image, sigma=2)

        # Apply Sobel filter in the x-direction
        sobel_edges = filters.sobel_h(blurred_image)

        # Perform Canny edge detection on the edges obtained from the Sobel filter
        canny_edges = feature.canny(sobel_edges)

        plot_and_save_figure(sobel_edges, canny_edges, 'h')
        # Perform Hough transform to detect lines
        hough_transform, angles, distances = transform.hough_line(canny_edges)
        # Find the peaks in Hough space
        peaks = transform.hough_line_peaks(hough_transform, angles, distances)

        # Initialize lists to store multiple horizontal lines with maximum length
        max_lengths = []
        most_horizontal_lines = []

        for _, angle, dist in zip(*peaks):
            if angle != 0:  # Exclude lines with zero angle
                sin_angle = np.sin(angle)
                if sin_angle == 0:
                    continue  # Skip line

            y0 = (dist - 0 * np.cos(angle)) / np.sin(angle)
            y1 = (dist - canny_edges.shape[1] * np.cos(angle)) / np.sin(angle)
            length = np.abs(y1 - y0)
            if not max_lengths or length > max(max_lengths):
                max_lengths.append(length)
                most_horizontal_lines.append((angle, dist))
            elif length == max(max_lengths):
                most_horizontal_lines.append((angle, dist))

        return most_horizontal_lines


import matplotlib.pyplot as plt 

def plot_and_save_figure(image1, image2, fname):
    # Plot the figure
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].imshow(image1)
    ax[0].set_title('edges')
    ax[1].imshow(image2)
    ax[1].set_title('line')
    # Save the figure
    save_path = f'{fname}_linedetector.png'
    plt.savefig(save_path)
    plt.close(fig)  # Close the figure to release resources
    return 0
