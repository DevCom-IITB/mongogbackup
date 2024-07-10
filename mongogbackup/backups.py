import subprocess, os, sys

class MongoCommandUnavailableError(Exception):
    """Raised when the required MongoDB command is not available."""
    def __init__(self, command:str):
        self.command = command
    def __str__(self):
        return f"Command {self.command} not found. Please install MongoDB Database Tools on your system and add them to your PATH."
    

class MongoBackupHandler:
    """Handles backup and restore operations for MongoDB databases."""

    def __init__(
        self,
        db_name:str,
        host:str='localhost', 
        port:int=27017,
        username:str=None,
        password:str=None, 
        auth_db:str=None
        ):
        """Initializes the MongoBackupHandler object with database details and 
        checks if mongodump and mongorestore are installed and added to PATH.

        Parameters:
            db_name [type:String] -- Name of the database to be backedup/restored. 
            host [type:String] -- MongoDb host address. Defaults to 'localhost'. 
            port [type:int] -- MongoDb port number. Defaults to 27017. 
            username [type:String] -- (Optional) MongoDb username for user authentication.
            password [type:String] -- (Optional but required if username is mentioned) MongoDb password for user authentication.
            auth_db [type:String] -- (Optional but required if username is mentioned) MongoDB database to authenticate the user details."""
            
        mongodump_available = self.check_mongodump()
        mongorestore_available = self.check_mongoerstore()
        if not  mongodump_available or not mongorestore_available:      
            raise MongoCommandUnavailableError("mongodump" if not mongodump_available else "mongorestore")

        self.db_name=db_name
        self.host=host
        self.port=port

        # if user authentication is required to access the database:
        self.username=username
        self.password=password
        self.auth_db=auth_db
    
    def check_mongodump(self) -> bool:
        """Check mongodump command availability"""
        command =[ 'mongodump', '--version']
        result= subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:  
            return False
        return True
        
    def check_mongoerstore(self) -> bool:
        """Check mongorestore command availability"""
        command =[ 'mongorestore', '--version']
        result= subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:  
            return False
        return True
        
    def backup(self, dir:str) -> bool:
        """Executes mongodump and saves backup files to the specified directory(dir)."""
        formatted_dir = dir.replace("\\", "/")
        os.makedirs(formatted_dir, exist_ok=True)
        
        command = [
            'mongodump', 
            '--host', self.host, 
            '--port', str(self.port), 
            '--db', self.db_name, 
            '--out', formatted_dir
            ]

        if self.username and self.password and self.auth_db:
            command.extend([
                '--username', self.username, 
                '--password', self.password, 
                '--authenticationDatabase', self.auth_db
                ])

        print("Executing command:", " ".join(command))  #for testing purposes
        result=subprocess.run(command, capture_output=True,text=True)
        if result.returncode == 0:
            print(f"Backup successful; added to: {formatted_dir}")
            return True
        print(f"Backup failed with error: {result.stderr}")
        return False

    def restore(self,bck_dir:str) -> bool:
        """Executes mongorestore and loads backupfiles from the specified directory(bck_dir)."""
        
        formatted_bck_dir = bck_dir.replace("\\", "/")
        
        if not os.path.exists(formatted_bck_dir):
            print(f"Error: The specified directory {bck_dir} does not exist.")

        command= [
            'mongorestore', 
            '--host', self.host, 
            '--port', str(self.port), 
            '--db', self.db_name, 
            formatted_bck_dir
            ]
        
        if self.username and self.password and self.auth_db:
            command.extend([
                '--username', self.username, 
                '--password', self.password, 
                '--authenticationDatabase', self.auth_db
                ])
        
        print("Executing command:", " ".join(command))  #for testing purposes
        result= subprocess.run(command, capture_output= True, text=True)
        
        if result.returncode == 0:
            print(f"Restore succesful; restored from: {bck_dir}")
            return True
        print(f"Restore failed with error: {result.stderr}")
        return False