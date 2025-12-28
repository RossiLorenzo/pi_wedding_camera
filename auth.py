import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
]


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

            # Check if we're running on a headless system (no DISPLAY)
            # Use console flow for headless systems like Raspberry Pi
            if os.environ.get("DISPLAY") is None and sys.stdin.isatty():
                print("\nHeadless system detected. Using console-based authentication.")
                print(
                    "You will need to open the URL on another device and paste the code here.\n"
                )
                creds = flow.run_console()
            else:
                # Try local server first, fall back to console if it fails
                try:
                    creds = flow.run_local_server(port=8080, open_browser=True)
                except Exception as e:
                    print(f"Local server failed: {e}")
                    print("Falling back to console-based authentication.\n")
                    creds = flow.run_console()

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
