__all__ = ('backups', 'files', 'gdrive', 'targz')

from mongogbackup import backups, files, gdrive, targz

class MongoConfig:
    def __init__(self, db_name:str, host:str='localhost', port:int=27017, username:str=None, password:str=None, auth_db:str=None) -> None:
        self.db_name = db_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth_db = auth_db

class MongoGBackup:
    def __init__(self, mongoConfig:MongoConfig, credentials_file:str, key:str) -> None:
        self. backups = backups.MongoBackupHandler(
            db_name=mongoConfig.db_name,
            host=mongoConfig.host,
            port=mongoConfig.port,
            username=mongoConfig.username,
            password=mongoConfig.password,
            auth_db=mongoConfig.auth_db
        )
        self.gdrive = gdrive.GoogleDriveHandler(credentials_file)
        self.hash = files.HashVerifier()
        self.encrypt = files.FileEncryptor(generate_key=False, key=key)