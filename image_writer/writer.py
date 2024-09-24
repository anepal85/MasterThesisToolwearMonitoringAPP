from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import tifffile
from PIL import Image
import os
import time

def ensure_directory_exists(path: str):
    """Check if the directory exists, and create it if it doesn't."""
    if not os.path.exists(path):
        os.makedirs(path)

def generate_dynamic_filename(base_path: str, id: int) -> str:
    """Generate a dynamic filename using user_data_id, process_number, and a timestamp."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return os.path.join(base_path, f"{id}_{timestamp}")

def remove_redundant_path(full_path, base_path):
    if full_path.startswith(base_path):
        return full_path[len(base_path):].lstrip(os.path.sep)
    return full_path

class ImageWriterWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.image = None
        self.image_file_path = None
        self.mask = None
        self.mask_file_path = None

        self.running = False

    def update_task(self, image: np.ndarray, image_file_path: str, mask: np.ndarray, mask_file_path: str):
        self.image = image
        self.image_file_path = image_file_path
        self.mask = mask
        self.mask_file_path = mask_file_path
        if not self.isRunning():
            self.start()

    def run(self):
        self.running = True
        try:
            if self.image is not None:
                if self.image.ndim == 3 and (self.image.shape[2] == 1 or self.image.shape[2] == 3):
                    #tifffile.imwrite(image_file_path, image)
                    self.save_as_jpeg(self.image, self.image_file_path)
                else:
                    raise ValueError("Invalid image format. Expected a 3D array with last dimension of size 1 or 3.")
            if self.mask is not None:
                if self.mask.ndim == 3 and (self.mask.shape[2] == 1 or self.mask.shape[2] == 3):
                    tifffile.imwrite(self.mask_file_path, self.mask)
                else:
                    raise ValueError("Invalid mask format. Expected a 3D array with last dimension of size 1 or 3.")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
        self.finished
        self.running = False

    def stop(self):
        if self.isRunning():
            self.wait()
        self.running = False
    
    def save_as_jpeg(self, image: np.ndarray, file_path: str):
        image_pil = Image.fromarray(image)
        image_pil.save(file_path, quality=95) 
