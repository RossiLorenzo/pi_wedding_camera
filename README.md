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

*   **Error: Command 'libcamera-still' not found**:
    *   Ensure your Pi is running a modern OS.
    *   If using an older OS (Buster), you may need to modify the script to use `raspistill`.
*   **Camera not detected**:
    *   Check connection ribbon.
    *   Ensure camera interface is enabled in `raspi-config`.
