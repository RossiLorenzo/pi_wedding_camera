import os
import socket

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
# Using appendonly scope which allows uploading photos and creating albums
# without requiring full photoslibrary access (which needs app verification)
SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
]


def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None

        if not creds or not creds.valid:
            # Look for client_secret file
            secret_file = None
            for file in os.listdir("."):
                if file.startswith("client_secret_") and file.endswith(".json"):
                    secret_file = file
                    break

            if not secret_file:
                print("Error: Could not find client_secret_*.json file.")
                return None

            print(f"Using secret file: {secret_file}")
            flow = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES)

            local_ip = get_local_ip()
            print(f"\n=== OAuth Authentication ===")
            print(f"Starting auth server on http://{local_ip}:8080")
            print(f"If running headless, open browser on another device.")
            print(f"The redirect will go to localhost:8080 which is this Pi.\n")

            # Force consent prompt to ensure we get a refresh_token
            # This is needed because Google only returns refresh_token on first consent
            creds = flow.run_local_server(
                host="localhost",
                port=8080,
                open_browser=False,
                success_message="Authentication successful! You can close this window.",
                prompt="consent",
            )

        # Save the credentials for the next run
        if creds:
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                print("Token saved to token.json")

    return creds


if __name__ == "__main__":
    result = authenticate()
    if result:
        print("Authentication successful!")
    else:
        print("Authentication failed.")
