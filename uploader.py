import os
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class GooglePhotosUploader:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/photoslibrary', 'https://www.googleapis.com/auth/photoslibrary.sharing']
        self.creds = None
        self.service = None
        self.album_id = None
        self.target_album_title = "Fliss & Lorenzo 30/05/26"

    def authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                print("Error: detailed authentication required, run auth.py first")
                return False
        
        self.service = build('photoslibrary', 'v1', credentials=self.creds, static_discovery=False)
        return True

    def get_or_create_album(self):
        if not self.service:
            if not self.authenticate():
                return None

        # List albums to find the target one
        # Note: pagination might be needed if user has many albums, implementing simple search first
        try:
            results = self.service.albums().list(pageSize=50).execute()
            albums = results.get('albums', [])
            
            # support pagination just in case
            while 'nextPageToken' in results:
                page_token = results['nextPageToken']
                results = self.service.albums().list(pageSize=50, pageToken=page_token).execute()
                albums.extend(results.get('albums', []))

            for album in albums:
                if album.get('title') == self.target_album_title:
                    self.album_id = album.get('id')
                    print(f"Found existing album: {self.target_album_title}")
                    return self.album_id
            
            # If not found, create it
            print(f"Album '{self.target_album_title}' not found. Creating it...")
            album_body = {
                'album': {'title': self.target_album_title}
            }
            created_album = self.service.albums().create(body=album_body).execute()
            self.album_id = created_album.get('id')
            print(f"Created new album: {self.target_album_title}")
            
            # Share the album (optional, but requested implicitly by 'shared album')
            # The API allows creating a 'shared' album but actual sharing with specific users 
            # might usually be done via UI or creating a shareable link.
            # We will at least make it shareable.
            try:
                share_body = {
                    'sharedAlbumOptions': {
                        'isCollaborative': True,
                        'isCommentable': True
                    }
                }
                self.service.albums().share(albumId=self.album_id, body=share_body).execute()
                print("Album configured as shared.")
            except Exception as e:
                print(f"Warning: Could not set sharing options: {e}")

            return self.album_id
            
        except Exception as e:
            print(f"Error accessing albums: {e}")
            return None

    def upload_photo(self, file_path):
        if not self.album_id:
            if not self.get_or_create_album():
                print("Could not get or create album. Aborting upload.")
                return

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        print(f"Uploading {file_path}...")
        
        # 1. Upload bytes to get an upload token
        upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
        headers = {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-Type': 'application/octet-stream',
            'X-Goog-Upload-File-Name': os.path.basename(file_path),
            'X-Goog-Upload-Protocol': 'raw',
        }
        
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
                
            response = requests.post(upload_url, headers=headers, data=image_data)
            response.raise_for_status()
            upload_token = response.content.decode('utf-8')
            
            # 2. Create media item using the upload token
            new_item = {
                'albumId': self.album_id,
                'newMediaItems': [
                    {
                        'description': 'Wedding camera photo',
                        'simpleMediaItem': {
                            'uploadToken': upload_token,
                            'fileName': os.path.basename(file_path)
                        }
                    }
                ]
            }
            
            result = self.service.mediaItems().batchCreate(body=new_item).execute()
            
            status = result['newMediaItemResults'][0]['status']
            if status['message'] == 'Success':
                print("Photo uploaded successfully!")
            else:
                print(f"Failed to create media item: {status}")

        except Exception as e:
            print(f"Error uploading photo: {e}")
