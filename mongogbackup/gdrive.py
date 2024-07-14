from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, HttpError
from typing import Dict, Optional, List
import json
import requests

class LoadCredentialsError(Exception):
    """Raised when there is an error loading credentials from file."""
    def __init__(self, message: str):
        self.message = message
    def __str__(self):
        return f"Error in reading the credentials file: {self.message}"
    
class InvalidCredentialsError(Exception):
    """Raised when credentials are invalid"""
    def __init__(self, message: str):
        self.message = message
    def __str__(self):
        return f"Invalid credentials: {self.message}"

class GoogleDriveAPIError(Exception):
    """Raised when there is an error connecting to Google Drive API."""
    def __init__(self, message: str):
        self.message = message
    def __str__(self):
        return f"Google Drive API error: {self.message}"
    
class InvalidParentIDError(Exception):
    """Raised when the parent ID is invalid or does not exist."""
    def __init__(self, parent_id: str):
        self.parent_id = parent_id
    def __str__(self):
        return f"Invalid parent ID: {self.parent_id}. The folder may not exist or the ID is incorrect."
    
class FileUploadError(Exception):
    """Raised when there is an error during file upload."""
    def __init__(self, file_name: str, message: str):
        self.file_name = file_name
        self.message = message
    def __str__(self):
        return f"Error deleting file {self.file_name}: {self.message}"

class FileDeletionError(Exception):
    """Raised when there is an error during file deletion."""
    def __init__(self, file_name: str, file_id: str, message: str):
        self.file_name = file_name
        self.file_id = file_id
        self.message = message
    def __str__(self):
        return f"Error deleting file {self.file_name} (ID: {self.file_id}): {self.message}"

class FileQueryError(Exception):
    """Raised when there is an error querying files on Google Drive."""
    def __init__(self, message: str):
        self.message = message
    def __str__(self):
        return f"File query error: {self.message}"
    
class InternetConnectivityError(Exception):
    """Raised when there is no active internet connection."""
    def __init__(self):
        pass
    def __str__(self):
        return "No internet connection"


class GoogleDriveHandler:
    def __init__(self, credentials_file: str, parent_id: str, file_name: str) -> None:
        self.parent_id = parent_id
        self.file_name = file_name
        if self.check_internet_connectivity() == False:
            raise InternetConnectivityError()
        try:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise LoadCredentialsError(str(e))
        except (IOError, ValueError) as e:
            raise InvalidCredentialsError(str(e))
        except HttpError as e:
            raise GoogleDriveAPIError(str(e))
        
    def check_internet_connectivity(self) -> bool:
        """Checks if there is an active internet connection."""
        try:
            requests.get('https://www.google.com', timeout=5)
            return True
        except requests.ConnectionError:
            return False
            
    def find_existing_files(self, file_name: str, parent_id: str) -> Optional[List[Dict[str, str]]]:
        """Finds all existing files with the same name in the target folder"""
        try: 
            query = f"name='{file_name}' and '{parent_id}' in parents and trashed=false"
            response = self.drive_service.files().list(q=query, fields='files(id, name)').execute()
            files = response.get('files', [])
            print(f'Existing files: {files}')
            return files if files else None
        except HttpError as e:
            if e.resp.status in [403, 404]:
                raise InvalidParentIDError(parent_id)
            raise FileQueryError(str(e))

    def delete_files(self, files: List[dict]) -> None:
        """Deletes files from Google Drive"""
        for file in files:
            try:
                self.drive_service.files().delete(fileId=file['id']).execute()
                print(f"Deleted file: {file['name']} (ID: {file['id']})")
            except HttpError as e:
                FileDeletionError(file['name'], file['id'], str(e))
    
    def delete_older_files(self, parent_id: str, num_files: int) -> None:
        """Deletes older files if there are more than 3 files in the target folder"""
        try:
            query = f"'{parent_id}' in parents and trashed=false"
            response = self.drive_service.files().list(q=query, fields='files(id, name)', orderBy='createdTime asc').execute()
            files = response.get('files', [])
            if len(files) > num_files:
                for file in files[0:len(files)-num_files]:
                    try:
                        self.drive_service.files().delete(fileId=file['id']).execute()
                        print(f"Deleted file: {file['name']}")
                    except HttpError as e:
                        FileDeletionError(file['name'], file['id'], str(e))
        except HttpError as e:
            if e.resp.status in [403, 404]:
                raise InvalidParentIDError(parent_id)
            raise FileQueryError(str(e))

    def upload_file_to_drive(self, file_name: str, parent_id: str) -> dict:
        """Uploads a file to Google Drive"""
        media = MediaFileUpload(file_name, mimetype='application/gzip', resumable=True)
        file_metadata = {
            'name': file_name,
            'parents': [parent_id]
        }
        
        try:
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
            return response
        except HttpError as e:
            if e.resp.status in [403, 404]:
                raise InvalidParentIDError(parent_id)
            FileUploadError(file_name, str(e))
            raise e
    
    # this implementation overwrites any previous files with the same name in the target folder, essentially keeping only the latest file
    def overwrite_and_upload_to_drive(self, file_name: str, parent_id: str) -> None:
        """Uploads a file to Google Drive and deletes any previous files with the same name in the target folder"""
        existing_files = self.find_existing_files(file_name, parent_id)

        try:
            response = self.upload_file_to_drive(file_name, parent_id)
            if existing_files:
                self.delete_files(existing_files)

        except (FileUploadError, FileDeletionError, FileQueryError) as e:
            print(f'Unable to overwrite and upload file, error: {e}')

    # this implementation keeps the 'num_files' newest files at any point in time in the target folder
    def upload_to_drive_with_rfh(self, file_name: str, parent_id: str, num_files: int) -> None:
        """Uploads a file to Google Drive and deletes older files if there are more than 3 files in the target folder"""
        try:
            response = self.upload_file_to_drive(file_name, parent_id)
            self.delete_older_files(parent_id, num_files) 

        except (FileUploadError, FileDeletionError, FileQueryError) as e:
            print(f'Unable to upload file with RFH, error: {e}')



if __name__ == "__main__":
    credentials_file = 'mongogbackup/credentials.json'
    parent_id = '1kIvfXUgB7QnXfhoaueMKJjsYCLGr1zUU'  # Replace with your desired target folder ID
    gdrive = GoogleDriveHandler(credentials_file, parent_id, 'mongogbackup/backup.zip')
    num_files = 3
    gdrive.overwrite_and_upload_to_drive('mongogbackup/backup.zip', parent_id) #if you want to overwrite previously uploaded backup files
    # gdrive.upload_to_drive_with_rfh('mongogbackup/backup.zip', parent_id, num_files) #if you want to keep only n newest files in the target folder
    # gdrive.upload_file_to_drive('mongogbackup/backup.zip', parent_id) #if you want to keep all backup files in the target folder