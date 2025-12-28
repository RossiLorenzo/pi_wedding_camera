#!/usr/bin/env python3
"""
Sync Service for Wedding Camera

This service runs in the background and:
1. Monitors for internet connectivity
2. When online, uploads any pending photos to Google Photos
3. Tracks which photos have been successfully uploaded

This allows photos to be taken offline and synced later when WiFi is available.
"""

import json
import os
import socket
import time
from datetime import datetime

from uploader import GooglePhotosUploader

# Configuration
PICTURES_DIR = os.path.expanduser("~/Pictures")
SYNC_STATE_FILE = os.path.expanduser("~/pi_wedding_camera/sync_state.json")
CHECK_INTERVAL = 30  # seconds between connectivity checks
UPLOAD_DELAY = 5  # seconds between uploads to avoid rate limiting


def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Check if internet is available by trying to connect to Google's DNS.
    Returns True if connected, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.error, OSError):
        return False


def load_sync_state():
    """Load the sync state from disk."""
    if os.path.exists(SYNC_STATE_FILE):
        try:
            with open(SYNC_STATE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"uploaded": []}


def save_sync_state(state):
    """Save the sync state to disk."""
    try:
        with open(SYNC_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        print(f"Error saving sync state: {e}")


def get_pending_photos(sync_state):
    """
    Get list of photos that haven't been uploaded yet.
    Returns list of full file paths.
    """
    if not os.path.exists(PICTURES_DIR):
        return []

    uploaded = set(sync_state.get("uploaded", []))
    pending = []

    valid_extensions = (".jpg", ".jpeg", ".png")

    for filename in os.listdir(PICTURES_DIR):
        if filename.lower().endswith(valid_extensions):
            if filename.startswith("wedding_"):  # Only sync wedding photos
                if filename not in uploaded:
                    pending.append(os.path.join(PICTURES_DIR, filename))

    # Sort by filename (which includes timestamp) to upload oldest first
    pending.sort()
    return pending


def sync_photos():
    """
    Main sync function. Uploads all pending photos to Google Photos.
    Returns number of photos successfully uploaded.
    """
    sync_state = load_sync_state()
    pending = get_pending_photos(sync_state)

    if not pending:
        return 0

    print(f"Found {len(pending)} photos to sync")

    # Initialize uploader
    uploader = GooglePhotosUploader()

    uploaded_count = 0

    for photo_path in pending:
        filename = os.path.basename(photo_path)
        print(f"\nSyncing: {filename}")

        try:
            uploader.upload_photo(photo_path)

            # Mark as uploaded
            sync_state["uploaded"].append(filename)
            sync_state["last_sync"] = datetime.now().isoformat()
            save_sync_state(sync_state)

            uploaded_count += 1
            print(f"Successfully synced: {filename}")

            # Small delay between uploads
            if uploaded_count < len(pending):
                time.sleep(UPLOAD_DELAY)

        except Exception as e:
            print(f"Error syncing {filename}: {e}")
            # Continue with next photo

    return uploaded_count


def run_sync_service():
    """
    Main service loop. Continuously monitors connectivity and syncs when online.
    """
    print("=" * 50)
    print("Wedding Camera Sync Service Started")
    print(f"Pictures directory: {PICTURES_DIR}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("=" * 50)

    last_online_status = None

    while True:
        try:
            is_online = check_internet_connection()

            # Log status changes
            if is_online != last_online_status:
                status = "ONLINE" if is_online else "OFFLINE"
                print(
                    f"\n[{datetime.now().strftime('%H:%M:%S')}] Network status: {status}"
                )
                last_online_status = is_online

            if is_online:
                # Check for pending photos
                sync_state = load_sync_state()
                pending = get_pending_photos(sync_state)

                if pending:
                    print(
                        f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting sync of {len(pending)} photos..."
                    )
                    uploaded = sync_photos()
                    print(f"Sync complete. Uploaded {uploaded} photos.")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\nSync service stopped.")
            break
        except Exception as e:
            print(f"Error in sync loop: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_sync_service()
