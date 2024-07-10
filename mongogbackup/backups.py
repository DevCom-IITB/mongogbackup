import subprocess, os, sys
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ConnectionFailure

class MongoCommandUnavailableError(Exception):
    """Raised when the required MongoDB command is not available."""
    def __init__(self, command:str):
        self.command = command
    def __str__(self):
        return f"Command {self.command} not found. Please install MongoDB Database Tools on your system and add them to your PATH."
    
class MongoAdminError(Exception):
    def __init__(self,error_code:int):
        self.error_code=error_code
        
    def __str__(self):
        if self.error_code == 1:
            return "Error: User authentication is required. Please provide username, password and authentication database."
        elif self.error_code == 2:
            return "Error: Invalid username or password. Please check the provided credentials."

class MongoConnectionError(Exception):
    def __str__(self):
        return "Error: Unable to connect to the specified MongoDB database. Please check host,port and database name"

class DirectoryNotFoundError(Exception):
    def __init__(self, dir:str):
        self.dir=dir
    def __str__(self):
        return f"Error: The specified directory {self.dir} does not exist."
    
class UnexpectedError(Exception):
    def __init__(self, error:str):
        self.error=error
    def __str__(self):
        return f"An unexpected error occured. Refer to: {self.error}"

class MongoBackupHandler:
    """Handles backup and restore operations for MongoDB databases."""

    def __init__(
        self,
        db_name:list[str],
        host:list[str]=None, 
        port:list[int]=None,
        username:str=None,
        password:str=None, 
        auth_db:str='Admin'
        ):
        """Initializes the MongoBackupHandler object with database details and 
        checks if mongodump and mongorestore are installed and added to PATH.

        Parameters:
            db_name [type:List of Strings] -- Name of the databases to be backedup/restored. 
            host [type:List of String] -- MongoDb host addressess. Defaults to a list of 'localhost'. 
            port [type:List of int] -- MongoDb port numbers. Defaults to a list of 27017. 
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

        num_db=len(self.db_name)
        self.num_db=num_db
        if self.host == None:
            self.host=['localhost']*num_db
        if self.port == None:
            self.port=[27017]*num_db
        # if user authentication is required to access the database:
        self.username=username
        self.password=password
        self.auth_db=auth_db
        
        self.check_connection()
    
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

    def check_connection(self) -> None:
        """Checks if the connection to the database is succesful or not. Also checks if the password provided is correct or not."""
        if self.username and self.password == None:
            try:
                for i in range(self.db_num):
                    client= MongoClient(host=self.host[i],port=self.port[i])
                    client.admin.command('listDatabases')

            except ConnectionFailure:
                raise MongoConnectionError()
            except OperationFailure:
                raise MongoAdminError(1)
            finally:
                client.close()
        else:
            try:
                for i in range(self.num_db):
                    client= MongoClient(host=self.host[i], port=self.port[i],
                                    username=self.username,
                                    password=self.password,
                                    authSource=self.auth_db)
                    client.admin.command('listDatabases')
            except OperationFailure:
                raise MongoAdminError(2)
            finally:
                client.close()
    
    def check_directory(self, dir:str) -> bool:
        """Checks if the specified directory exists or not."""
        if not os.path.exists(dir):
            return False
        return True

    def backup(self, dir:str) -> None:
        """Executes mongodump and saves backup files to the specified directory(dir)."""
        
        formatted_dir = dir.replace("\\", "/")
        check_dir= self.check_directory(formatted_dir)
        if not check_dir:
            raise DirectoryNotFoundError(dir)
        for i in range(self.num_db):
            db_name=self.db_name[i]
            host=self.host[i]
            port=self.port[i]
            command = [
                'mongodump', 
                '--host', host, 
                '--port', str(port), 
                '--db', db_name, 
                '--out', formatted_dir
                ]

            if self.username and self.password :
                command.extend([
                    '--username', self.username, 
                    '--password', self.password, 
                    '--authenticationDatabase', self.auth_db
                    ])

            print("Executing command:", " ".join(command))  #for testing purposes
            result=subprocess.run(command, capture_output=True,text=True)
            if result.returncode == 0:
                print(f"Database {db_name} successfully backed up to: {formatted_dir}  {i+1} out of {self.num_db} complete. ")
                continue
            raise UnexpectedError(result.stderr)
        print("Backup complete.")
        return
        

    def restore(self,bck_dir:str) -> None:
        """Executes mongorestore and loads backupfiles from the specified directory(bck_dir)."""
        
        formatted_bck_dir = bck_dir.replace("\\", "/")
        check_dir= self.check_directory(formatted_bck_dir)
        if not check_dir:
            raise DirectoryNotFoundError(dir)
        
        for i in range(self.num_db):
            host=self.host[i]
            port=self.port[i]
            db_name=self.db_name[i]
            command= [
                'mongorestore', 
                '--host', host, 
                '--port', str(port), 
                '--db', db_name, 
                formatted_bck_dir
                ]
        
            if self.username and self.password:
                command.extend([
                    '--username', self.username, 
                    '--password', self.password, 
                    '--authenticationDatabase', self.auth_db
                    ])
        
            print("Executing command:", " ".join(command))  #for testing purposes
            result= subprocess.run(command, capture_output= True, text=True)
        
            if result.returncode == 0:
                print(f"Restored database {db_name} from {formatted_bck_dir}  {i+1} out of {self.num_db} complete.")
                continue 
            raise UnexpectedError(result.stderr)
        print("Restore complete.")
        return
