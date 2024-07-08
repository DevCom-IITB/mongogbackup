import subprocess, os, sys

class MongoBackupHandler:
    """Handles backup and restore operations for MongoDB databases."""
    def __init__(self, db_name,host='localhost', port=27017, username=None, passwword=None, auth_db=None):
        """
        Initializes the MongoBackupHandler object with database details and checks if mongodump and mongorestore are installed and added to PATH.

        Parameters:-
        db_name[type:String]- Name of the database to be backedup/restored. 
        host[type:String]- MongoDb host address. Defaults to 'localhost'. 
        port[type:int]- MongoDb port number. Defaults to 27017. 
        username[type:String]- (Optional) MongoDb username for user authentication.
        password[type:String]- (Optional but required if username is mentioned) MongoDb password for user authentication.
        auth_db[type:String]- (Optional but required if username is mentioned) MongoDB database to authenticate the user details.
        
        """
        command =[ 'mongodump', '--version']
        result= subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:  
            print("Error: mongodump not found. Please install MongoDB on your system and add it to your PATH.")
            exit(1)
        command= [ 'mongorestore', '--version']
        result= subprocess.run(command, capture_output=True, text=True)
        if result.returncode!=0 :
            print("Error: mongorestore not found. Please install MongoDB on your system and add it to your PATH.")
            exit(1)
        
        self.db_name=db_name
        self.host=host
        self.port=port

        #if user authentication is required to access the database:
        self.username=username
        self.password=passwword
        self.auth_db=auth_db
        
    def backup(self, dir):
        """Performs a backup of the specified MongoDB database and saves it to the specified directory(dir)."""
        formatted_dir = dir.replace("\\", "/")
        os.makedirs(formatted_dir, exist_ok=True)
        
        command = ['mongodump', '--host', self.host, '--port', str(self.port), '--db', self.db_name, '--out', formatted_dir]

        if self.username and self.password and self.auth_db:
            command.extend(['--username', self.username, '--password', self.password, '--authenticationDatabase', self.auth_db])

        print("Executing command:", " ".join(command))  #for testing purposes
        result=subprocess.run(command, capture_output=True,text=True)
        if result.returncode == 0:
            print(f"Backup successful; added to: {formatted_dir}")
        else:
            print(f"Backup failed with error: {result.stderr}")

    def restore(self,bck_dir):
        """Restore the specified MongoDB database from the backupfiles from the specified directory(bck_dir)."""
        
        formatted_bck_dir = bck_dir.replace("\\", "/")
        if not os.path.exists(formatted_bck_dir):
            print(f"Error: The specified directory {bck_dir} does not exist.")
            
        command= ['mongorestore', '--host', self.host, '--port', str(self.port), '--db', self.db_name, formatted_bck_dir]
        
        if self.username and self.password and self.auth_db:
            command.extend(['--username', self.username, '--password', self.password, '--authenticationDatabase', self.auth_db])
        
        print("Executing command:", " ".join(command))  #for testing purposes
        result= subprocess.run(command, capture_output= True, text=True)
        
        if result.returncode == 0:
            print(f"Restore succesful; restored from: {bck_dir}")
        else:
            print(f"Restore failed with error: {result.stderr}")

#testing the class
#if __name__ == '__main__':
#    backup_handler = MongoBackupHandler(db_name='flask_database')
#    #use double backslashes in windows paths as python interprets single backlashes as end of string sequence or use raw string
#    backup_handler.backup("C:\\Users\\kani1\\Downloads\\test")
#    backup_handler.restore("C:\\Users\\kani1\\Downloads\\test")