import cv2
import math
import time
from dnx64 import DNX64

#from dnx64_python import DNX64

DNX64_PATH = 'C:\\Program Files\\DNX64\\DNX64.dll'

class DinoLiteMicroscope:
    CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS = 1280, 960, 30

    def __init__(self, dnx64_path: str, device_index: int = 0, cam_index: int = 0):
        self.dnx64_path = dnx64_path
        self.device_index = device_index
        self.cam_index = cam_index
        self.microscope = None
        self.camera = None

    def initialize_microscope(self):
        """Initialize the microscope."""
        try:
            #DNX64 = getattr(importlib.import_module("DNX64"), "DNX64")
            self.microscope = DNX64(self.dnx64_path)#DNX64(self.dnx64_path)
            self.microscope.SetVideoDeviceIndex(self.device_index)
            time.sleep(0.1)
            self.microscope.Init()
            time.sleep(0.1)
            self.microscope.EnableMicroTouch(True)
        except ImportError as e:
            print("Error importing DNX64:", e)
            return False
        return True

    def initialize_camera(self):
        """Initialize the camera."""
        self.camera = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_HEIGHT)
        self.camera.set(cv2.CAP_PROP_FPS, self.CAMERA_FPS)
        return True

    def capture_single_image(self):
        """Capture a single image and return it as a numpy array."""
        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                return frame
            else:
                print("Error capturing image")
        else:
            print("Camera not initialized")
        return None

    def get_amr(self):
        """Retrieve and return the AMR (Automatic Magnification Reading)."""
        if self.microscope:
            amr = self.microscope.GetAMR(self.device_index)
            return round(amr, 1)
        else:
            print("Microscope not initialized")
            return None

    def get_fov_mm(self):
        """Retrieve and return the field of view in millimeters."""
        if self.microscope:
            amr = self.get_amr()
            print(f'amr during calling fov : {amr}')
            fov = self.microscope.FOVx(self.device_index, amr)
            if fov == math.inf:
                fov = self.microscope.FOVx(self.device_index, 50.0) / 1000.0
            else:
                fov /= 1000.0
            return round(fov, 2)
        else:
            print("Microscope not initialized")
            return None

    def get_pixel_per_mm(self):
        """Calculate and return the pixel per mm using current magnification and image size."""
        fov_mm = self.get_fov_mm()
        image_width = self.CAMERA_WIDTH
        pixel_per_mm = image_width / fov_mm
        return pixel_per_mm

    def release_resources(self):
        """Release resources (microscope and camera)."""
        if self.microscope:
            del self.microscope
        if self.camera:
            self.camera.release()

if __name__ == '__main__':
    dino = DinoLiteMicroscope(DNX64_PATH)
    
    if dino.initialize_microscope() and dino.initialize_camera():
        # Capture a single image
        image = dino.capture_single_image()
        
        # Save the captured image
        if image is not None:
            cv2.imwrite('captured_image.jpg', image)
            print("Image saved successfully.")

        # Get and print the FOV and AMR
        fov_mm = dino.get_fov_mm()
        amr = dino.get_amr()
        pixel_per_mm = dino.get_pixel_per_mm()
        print("Field of View (FOV): {} mm".format(fov_mm))
        print("Automatic Magnification Reading (AMR): {}".format(amr))
        print("Pixel per mm {} mm".format(pixel_per_mm))


        # Release resources
        #dino.release_resources()
    else:
        print("Failed to initialize microscope or camera.")
