import tensorflow as tf
import numpy as np

def read_image_from_path(image_path: str, channels: int):
    try:
        # Read image from file
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
    except FileNotFoundError as e:
        # If the file is not found, raise an exception with a meaningful message
        raise FileNotFoundError(f"File not found: {image_path}") from e

    # Decode image
    image = tf.image.decode_image(img_bytes, channels=channels)
    return image

def convert_to_tensor(image: np.ndarray, channels: int) -> tf.Tensor:
    """
    Convert a numpy array image to a TensorFlow tensor and preprocess it.
    """
    image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
    if channels == 1:
        image_tensor = tf.image.rgb_to_grayscale(image_tensor)
    elif channels == 3 and image_tensor.shape[-1] == 1:
        image_tensor = tf.image.grayscale_to_rgb(image_tensor)
    return image_tensor


def tf_resize_image(image: tf.Tensor, width: int, height: int) -> tf.Tensor:
    return tf.image.resize(image, (height, width), method = 'nearest') 

def resize_segmmask_back_tooriginal(seg_mask: tf.Tensor, width: int = 2592, height: int = 1944) -> tf.Tensor:
    return tf.image.resize(seg_mask[0], (height, width), method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)[tf.newaxis]


def squeeze_tensor_to_np(tf_image: tf.Tensor, **kwargs) -> np.array:
    return np.squeeze(tf_image, **kwargs)