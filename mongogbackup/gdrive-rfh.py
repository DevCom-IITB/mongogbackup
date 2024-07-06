from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io
import datetime

# this implementation keeps the 3 newest files at any point in time in the target folder
class GoogleDriveHandler:
    def __init__(self, credentials_file: str) -> None:
        self.credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def upload_to_drive(self, file_name: str, parent_id: str) -> None:
        """Uploads a file to Google Drive and deletes older files if there are more than 3 files in the target folder"""
        media = MediaFileUpload(file_name, mimetype='application/gzip', resumable=True)
        timestamp = str(datetime.datetime.now())
        file_metadata = {
            'name': timestamp + '-' + file_name,
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

            self.delete_older_files(parent_id) # delete older files if there are more than 3 files in the target folder
            print(f"File uploaded successfully! File Id: {response.get('id')}")

        except Exception as e:
            print(f'Unable to upload file, error: {e}')

    def delete_older_files(self, parent_id: str) -> None:
        """Deletes older files if there are more than 3 files in the target folder"""
        query = f"'{parent_id}' in parents and trashed=false"
        response = self.drive_service.files().list(q=query, fields='files(id, name)', orderBy='createdTime asc').execute()
        files = response.get('files', [])
        if len(files) > 3:
            for file in files[0:len(files)-3]:
                try:
                    self.drive_service.files().delete(fileId=file['id']).execute()
                    print(f"Deleted file: {file['name']}")
                except Exception as e:
                    print(f'Unable to delete file, error: {e}')


if __name__ == "__main__":
    credentials_file = 'mongogbackup/credentials.json'
    parent_id = 'XXXXXX' # Replace with your desired target folder ID
    gdrive = GoogleDriveHandler(credentials_file)
    gdrive.upload_to_drive(f'mongogbackup/backup.zip', parent_id)
    
