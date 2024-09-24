
import numpy as np
from schemas.ml_model import MLModel
import tensorflow as tf
from typing import Any
from keras.models  import load_model


class ToolWearPredictor:
    def __init__(self, model: MLModel):
        self.model = model
        self.loaded_model = self.load_trained_model(model.ml_model_path)
    
    @staticmethod 
    def load_trained_model(path: str) -> Any:
        return load_model(path, compile=False)

    def predict(self, image: tf.Tensor, threshold: float = 0.5) -> tf.Tensor:
        prediction = self.loaded_model.predict(image)
        prediction_mask = np.zeros_like(prediction, np.uint8)
        prediction_mask[prediction > threshold] = 255
        return prediction_mask



