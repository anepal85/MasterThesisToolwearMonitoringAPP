import subprocess
import sys
import os

def run_label_studio():
    os.environ['LOCAL_FILES_SERVING_ENABLED'] = 'True'
    # Check the operating system
    if os.name == 'nt':  # For Windows
        cmd = 'start cmd /k label-studio start --port 8080'
    elif os.name == 'posix':  # For Unix-based systems (Linux, MacOS)
        cmd = 'gnome-terminal -- bash -c "label-studio start --port 8080; exec bash"'
    else:
        print("Unsupported OS")
        sys.exit(1)

    try:
        subprocess.Popen(cmd, shell=True)
        print("Label Studio started successfully.")
    except Exception as e:
        print(f"Failed to start Label Studio: {e}")

if __name__ == "__main__":
    run_label_studio()
