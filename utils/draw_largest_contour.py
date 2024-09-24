import cv2 
import numpy as np 

def find_largest_contour(prediction_mask : np.array)->np.array:
    # Convert prediction mask to binary
    binary_mask = (prediction_mask > 0).astype(np.uint8)
    
    # Find contours
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # # Find the contour with the largest area
    #largest_contour = max(contours, key=cv2.contourArea)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
    else:
        largest_contour = np.array([])  # Empty array if no contours are found
    
    return largest_contour

def draw_contour(image: np.array, contour: np.array, color = (0, 255, 0))->np.array:
    # Create a blank RGB image
    output_image = image.copy() #np.zeros_like(image, dtype=np.uint8)
    output_image = (output_image*255).astype(np.uint8)
    
    # Draw the contour on the image
    cv2.drawContours(output_image, [contour], -1, color, thickness=2)
    
    return output_image


def draw_prediction_on_image(image_np:np.array, prediction_mask_np)->np.array:
    if prediction_mask_np.shape[0] == 1 :
        ## doesnot have batch size 
        prediction_mask_np = np.squeeze(prediction_mask_np, axis=0)
    largest_contour = find_largest_contour(prediction_mask_np)

    return draw_contour(image_np, largest_contour)

# p_mask = np.squeeze(prediction_mask, axis=0)
# im = np.squeeze(image_resized, axis=0)

# largest_contour = find_largest_contour(p_mask)
# output_image = draw_contour(im, largest_contour)


from skimage.transform import resize

def rsize_image_skimage(image, width, height):
    return resize(
    image, (height, width), anti_aliasing=True
)