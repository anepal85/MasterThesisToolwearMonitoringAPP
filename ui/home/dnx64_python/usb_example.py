import threading
import time
import cv2
#from dnx64 import DNX64

from ui.home.dnx64_python import DNX64

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 400
CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS = 2592, 1944, 30
DNX64_PATH = 'C:\\Program Files\\DNX64\\DNX64.dll'
DEVICE_INDEX = 0
QUERY_TIME = 0.05 # Buffer time for Dino-Lite to return value
COMMAND_TIME = 0.25 # Buffer time to allow Dino-Lite to process command 

# Initialize microscope
microscope = DNX64(DNX64_PATH)

def threaded(func):
    """Wrapper to run a function in a separate thread with @threaded decorator"""
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return wrapper

def custom_microtouch_function():
    """Executes when MicroTouch press detected"""
    print("MicroTouch press detected!")
    
def print_amr():
    microscope.Init()
    amr = microscope.GetAMR(DEVICE_INDEX)
    amr = round(amr,1)
    print(f"{amr}x")
    time.sleep(QUERY_TIME)

def get_amr():
    microscope.Init()
    amr = microscope.GetAMR(DEVICE_INDEX)
    return round(amr, 2)

def set_index():    
    microscope.Init()
    microscope.SetVideoDeviceIndex(1)
    time.sleep(COMMAND_TIME)

def print_fov_mm():
    microscope.Init()
    fov = microscope.FOVx(DEVICE_INDEX,microscope.GetAMR(DEVICE_INDEX))
    fov = round(fov / 1000,2)
    print(fov, "mm")
    time.sleep(QUERY_TIME)


def get_fov_mm():
    microscope.Init()
    fov = microscope.FOVx(DEVICE_INDEX,microscope.GetAMR(DEVICE_INDEX))
    return round(fov / 1000, 2)

def print_deviceid():
    microscope.Init()
    print(microscope.GetDeviceIDA(1))
    time.sleep(QUERY_TIME)

@threaded
def flash_leds():
    microscope.Init()
    microscope.SetLEDState(0,0)
    time.sleep(COMMAND_TIME)
    microscope.SetLEDState(0,1)
    time.sleep(COMMAND_TIME)
    
def capture_image(frame):
    """Capture an image and save it in the current working directory."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.png"
    cv2.imwrite(filename, frame)
    print(f"Saved image to {filename}")

def start_recording(frame_width, frame_height, fps):
    """Start recording video and return the video writer object."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"video_{timestamp}.avi"
    fourcc = cv2.VideoWriter.fourcc(*'XVID')
    video_writer = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
    print(f"Video recording started: {filename}\nPress SPACE to stop.")
    return video_writer

def stop_recording(video_writer):
    """Stop recording video and release the video writer object."""
    video_writer.release()
    print("Video recording stopped")

def initialize_camera():
    """Setup OpenCV camera parameters and return the camera object."""
    camera = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    return camera

def process_frame(frame):
    """Resize frame to fit window."""
    return cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))

def start_camera():
    """Starts camera, initializes variables for video preview, and listens for shortcut keys."""
    camera = initialize_camera()

    if not camera.isOpened():
        print('Error opening the camera device.')
        return

    recording = False
    video_writer = None

    while True:
        ret, frame = camera.read()
        if ret:
            resized_frame = process_frame(frame)
            cv2.imshow('Dino-Lite Camera', resized_frame)

            if recording:
                video_writer.write(frame)
        
        key = cv2.waitKey(25) & 0xff
        
        # Press '1' to print AMR value
        if key == ord('1'):
            print_amr()

        # Press '2' to flash LEDs
        if key == ord('2'):
            flash_leds()
        
        # Press 'f' to show fov
        if key == ord('f'):
            print_fov_mm()
        # Press 'd' to show device id
        if key == ord('d'):
            print_deviceid()

        # Press 's' to save a snapshot
        if key == ord('s'):
            capture_image(frame)

        # Press 'r' to start recording
        if key == ord('r') and not recording:
            recording = True
            video_writer = start_recording(CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS)

        # Press 'SPACE' to stop recording
        if key == 32 and recording:
            recording = False
            stop_recording(video_writer)

        # Press ESC to close
        if key == 27:
            break

    if video_writer is not None:
        video_writer.release()
    camera.release()
    cv2.destroyAllWindows()

def main():
    """Main function to run the camera and set the MicroTouch event callback."""
    microscope.SetVideoDeviceIndex(DEVICE_INDEX) # Set index of video device. Call before Init().
    microscope.Init() # Initialize the control object. Required before using other methods, otherwise return values will fail or be incorrect.
    microscope.EnableMicroTouch(True) # Enabled MicroTouch Event
    microscope.SetEventCallback(custom_microtouch_function) # Function to execute when MicroTouch event detected
    initialize_camera()
    start_camera()
    #print(microscope.GetConfig(0), 'Seperator', microscope.GetAMR(0))
    
    

if __name__ == "__main__":
    main()
