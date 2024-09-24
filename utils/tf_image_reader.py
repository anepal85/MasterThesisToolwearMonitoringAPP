import os 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf 
import numpy as np 
import cv2 

def preprocess_input(image_input, channels = 3) -> tf.Tensor:
    if isinstance(image_input, str):
        image = tf.io.read_file(image_input)
        image = tf.image.decode_image(image, channels=channels)
    elif isinstance(image_input, np.ndarray):
        image = tf.convert_to_tensor(image_input/255, dtype=tf.float32)
    image = tf.image.convert_image_dtype(image, tf.float32)
    return image

def tf_add_batch_1(image:tf.Tensor)-> tf.Tensor:
    return tf.expand_dims(image, axis=0)

def squeeze_tensor_to_np(tf_image: tf.Tensor, **kwargs)-> np.array:
    return np.squeeze(tf_image, **kwargs)

def image_reader(image_path)->np.array:
    img  =cv2.imread(image_path, 1)
    return np.array(img, np.uint8)