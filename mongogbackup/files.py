import subprocess, os

class MongoBackupHandler:
    def __init__(self, db_name,host='localhost', port=27017, username=None, passwword=None, auth_db=None):
        self.db_name=db_name

        script_dir = os.path.dirname(__file__)
        output_folder_path = os.path.join(script_dir, 'BackupFiles')
        formatted_output_dir = output_folder_path.replace("\\", "/")
        self.dir=formatted_output_dir

        self.host=host
        self.port=port
        #if user authentication is required to access the database:
        self.username=username
        self.password=passwword
        self.auth_db=auth_db
    
    def backup(self):
        os.makedirs(self.dir, exist_ok=True)
        
        command = ['mongodump', '--host', self.host, '--port', str(self.port), '--db', self.db_name, '--out', self.dir]

        if self.username and self.password and self.auth_db:
            command.extend(['--username', self.username, '--password', self.password, '--authenticationDatabase', self.auth_db])

        print("Executing command:", " ".join(command))
        result=subprocess.run(command, capture_output=True,text=True)
        if result.returncode == 0:
            print(f"Backup successful; added to: {self.dir}")
        else:
            print(f"Backup failed with error: {result.stderr}")

    def restore(self):
        command= ['mongorestore', '--host', self.host, '--port', str(self.port), '--db', self.db_name, self.dir]
        
        if self.username and self.password and self.auth_db:
            command.extend(['--username', self.username, '--password', self.password, '--authenticationDatabase', self.auth_db])
        
        result= subprocess.run(command, capture_output= True, text=True)
        
        if result.returncode == 0:
            print(f"Restore succesful; restored from: {self.dir}")
        else:
            print(f"Restore failed with error: {result.stderr}")


backup_handler = MongoBackupHandler(db_name='flask_database')
#use double backslashes in windows paths as python interprets single backlashes as end of string sequence or use raw string
backup_handler.backup()
backup_handler.restore()