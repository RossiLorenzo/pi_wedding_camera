import os
import time
import subprocess
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
    cmd = [
        "libcamera-still",
        "-o", filepath,
        "-t", "2000", # Warm up for 2 seconds (good for auto white balance/exposure)
        "--nopreview",
        "--width", "1920",
        "--height", "1080"
    ]

    try:
        # Run the command
        subprocess.run(cmd, check=True)
        print("Photo taken successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error taking photo: {e}")
        print("Ensure 'libcamera-still' is installed and camera is connected.")
        print("If you are on Legacy OS, you might need to use 'raspistill' instead.")
    except FileNotFoundError:
        print("Command 'libcamera-still' not found. Are you running on a Raspberry Pi with libcamera installed?")

if __name__ == "__main__":
    # Path relative to the script: ../Pictures
    # We resolve it to absolute path to be safe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pictures_dir = os.path.abspath(os.path.join(script_dir, "..", "Pictures"))
    
    take_photo(pictures_dir)
