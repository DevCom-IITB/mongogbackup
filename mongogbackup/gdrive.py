import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class GoogleDriveHandler:
  def __init__(self, credentials_file):
    self.credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
    self.drive_service = build('drive', 'v3', credentials=self.credentials)

  def upload_to_drive(self, file_name, parent_id):
    file_metadata = {
      'name': file_name,
    }
    media = MediaFileUpload(file_name, mimetype='application/gzip')
    existing_file = self.find_existing_file(parent_id)

    try:
      if existing_file:
        file = self.drive_service.files().update(
          fileId=existing_file['id'],
          body=file_metadata,
          media_body=media,
          fields='id'
        ).execute()
        print(f'File updated successfully! File Id: {file.get("id")}')

      else:
        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f'File uploaded successfully! File Id: {file.get("id")}')

    except Exception as e:
      print(f'Unable to upload file, error: {e}')
  
  def find_existing_file(self, parent_id):
    response = self.drive_service.files().list(q=f"'{parent_id}' in parents and trashed=false", fields='files(id, name)').execute()
    files = response.get('files', [])
    print(f'Existing files: {files}')
    return files[0] if files else None

if __name__ == "__main__":
  credentials_file = 'mongogbackup/credentials.json' 
  parent_id = 'XXXXX' # Folder ID
  gdrive = GoogleDriveHandler(credentials_file)
  gdrive.upload_to_drive('mongogbackup/backup.zip', parent_id)

#TODO: resumable uploads