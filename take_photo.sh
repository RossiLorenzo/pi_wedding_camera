#!/bin/bash
# Fast photo capture script for Wedding Camera
# Bypasses Python startup overhead for faster capture (~2s)

PICTURES_DIR="$HOME/Pictures"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="wedding_${TIMESTAMP}.jpg"
FILEPATH="${PICTURES_DIR}/${FILENAME}"

# Ensure directory exists
mkdir -p "$PICTURES_DIR"

# Take photo with optimized settings
rpicam-still \
    -o "$FILEPATH" \
    -t 1 \
    -n \
    --width 2304 \
    --height 1296 \
    --quality 95 \
    --denoise off \
    --autofocus-mode continuous \
    --immediate \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "Photo saved: $FILEPATH"
else
    echo "Error taking photo"
    exit 1
fi
