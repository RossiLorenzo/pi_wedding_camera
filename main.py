import os
import time
import subprocess
import shutil
from datetime import datetime

def take_photo(save_dir):
    """
    Takes a photo using libcamera-still and saves it to the specified directory.
    """
    # Ensure the directory exists
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            print(f"Created directory: {save_dir}")
        except OSError as e:
            print(f"Error creating directory {save_dir}: {e}")
            return

    # Generate filename based on timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wedding_{timestamp}.jpg"
    filepath = os.path.join(save_dir, filename)

    print(f"Taking photo: {filepath}")

    # Command to take photo
    # -o: output file
    # -t 1: timeout (wait 1ms before taking, effectively immediate after warmup)
    # --nopreview: disable preview window (headless)
    # Detect available camera command
    camera_cmd = None
    if shutil.which("rpicam-still"):
        camera_cmd = "rpicam-still"
    elif shutil.which("libcamera-still"):
        camera_cmd = "libcamera-still"
    elif shutil.which("raspistill"):
        camera_cmd = "raspistill"

    if not camera_cmd:
        print("Error: No suitable camera command found (rpicam-still, libcamera-still, or raspistill).")
        return

    print(f"Using camera command: {camera_cmd}")

    # specific flags might need adjustment for raspistill vs libcamera
    # For simplicity, we assume libcamera/rpicam syntax mostly. 
    # raspistill uses similar syntax for -o and -t, but --nopreview is -n. 
    # We will stick to libcamera syntax for now and add a basic fallback for raspistill if needed or just warn.
    
    cmd = [
        camera_cmd,
        "-o", filepath,
        "-t", "2000",
        "--nopreview",
        "--width", "1920",
        "--height", "1080"
    ]
    
    # Adapt flags for legacy raspistill if necessary
    if camera_cmd == "raspistill":
        cmd = [
            "raspistill",
            "-o", filepath,
            "-t", "2000",
            "-n", # nopreview equivalent
            "-w", "1920",
            "-h", "1080"
        ]

    try:
        # Run the command
        subprocess.run(cmd, check=True)
        print("Photo taken successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error taking photo: {e}")
    except FileNotFoundError:
        print(f"Command '{camera_cmd}' failed to execute.")

if __name__ == "__main__":
    # Path relative to the script: ../Pictures
    # We resolve it to absolute path to be safe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pictures_dir = os.path.abspath(os.path.join(script_dir, "..", "Pictures"))
    
    take_photo(pictures_dir)
