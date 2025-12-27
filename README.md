# Pi Wedding Camera

This project captures photos using a Raspberry Pi Zero W connected to a camera module.

## Setup

1.  **Hardware**:
    *   Raspberry Pi Zero W
    *   Raspberry Pi Camera Module
2.  **OS**:
    *   Raspberry Pi OS (Bullseye or Bookworm recommended) with `libcamera` support.

## Usage

The main script is `main.py`. It uses `libcamera-still` to capture images.

```bash
python3 main.py
```

Images will be saved in the `../Pictures` directory (relative to this repository).

## Troubleshooting

### "Input/output error" or "Device timeout"
If you see `Input/output error` (especially on basic commands like `ls` or `rpicam-hello`) or `Device timeout detected`, this is almost always a **hardware power issue** or detailed SD card failure.
*   **Power Supply**: The camera draws significant current when activating. If your power supply is weak, the voltage drops, causing the Pi to brownout or the SD card/Camera to disconnect. Use a high-quality 2.5A+ power supply.
*   **Ribbon Cable**: Check calls `libcamera` or `rpicam` fail. Ensure the ribbon cable is seated correctly on both ends.
*   **SD Card**: If `ls` fails, your file system might be corrupt. Try rebooting or fsck.

### "Command not found"
The script now automatically tries to find:
1.  `rpicam-still` (Newer OS)
2.  `libcamera-still` (Modern OS)
3.  `raspistill` (Legacy OS)

If none are found, ensure your camera interface is enabled in `raspi-config`.
