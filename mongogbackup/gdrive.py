from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io
from typing import Dict, Optional

# this implementation overwrites any previous files with the same name in the target folder
class GoogleDriveHandler:
    def __init__(self, credentials_file: str) -> None:
        self.credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    def find_existing_file(self, file_name: str, parent_id: str) -> Optional[Dict[str, str]]:
        """Finds an existing file with the same name in the target folder"""
        query = f"name='{file_name}' and '{parent_id}' in parents and trashed=false"
        response = self.drive_service.files().list(q=query, fields='files(id, name)').execute()
        files = response.get('files', [])
        print(f'Existing files: {files}')
        return files[0] if files else None
    
    def upload_to_drive(self, file_name: str, parent_id: str) -> None:
        """Uploads a file to Google Drive and overwrites any previous files with the same name in the target folder"""
        media = MediaFileUpload(file_name, mimetype='application/gzip', resumable=True)
        existing_file = self.find_existing_file(file_name, parent_id)

        try:
            if existing_file:
                file_metadata = {
                    'name': file_name,
                }
                request = self.drive_service.files().update(
                    fileId=existing_file['id'],
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                )
            else:
                file_metadata = {
                    'name': file_name,
                    'parents': [parent_id]
                }
                request = self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")
            print(f"File uploaded successfully! File Id: {response.get('id')}")

        except Exception as e:
            print(f'Unable to upload file, error: {e}')


if __name__ == "__main__":
    credentials_file = 'mongogbackup/credentials.json'
    parent_id = 'XXXXXX'  # Replace with your desired target folder ID
    gdrive = GoogleDriveHandler(credentials_file)
    gdrive.upload_to_drive('mongogbackup/backup.zip', parent_id)
