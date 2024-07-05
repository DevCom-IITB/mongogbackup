from hashlib import sha256
import datetime
from cryptography.fernet import Fernet

class HashVerifier:
    """Generates and verifies sha-256 checksums for files."""
        
    def __init__(self):
        """Initializes the HashVerifier class."""
        self._BUF_SIZE: int = 65336 # 64Kb
        self._last_hash: str = None
        self._last_hash_time:datetime.datetime = None
        
    def last_hash(self):
        """Last generated hash and the generation time.
        
        Returns:
            dict -- A dictionary containing the hash and the time it was generated
            {"hash":str, "time":datetime.datetime}.
            """
        return {"hash": self._last_hash, "time": self._last_hash_time}
    
    def settings(self, buf_size: int = None):
        """Settings for the HashVerifier class.

        Keword Arguments:
            buf_size -- The buffer size to use when reading the file. Default is 64Kb.
        """
        self._BUF_SIZE = buf_size if buf_size is not None else self._BUF_SIZE

    def generate_file_hash(self, file_path: str) -> str:
        """Generates and caches SHA-256 checksum for a file."""
        sha = sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(self._BUF_SIZE)
                if not data:
                    break
                sha.update(data)
        self._last_hash = sha.hexdigest()
        self._last_hash_time = datetime.datetime.now()
        return self._last_hash
    
    def compare_generated(self, hash: str) -> bool:
        """Compares input hash with the last generated hash."""
        return hash == self._last_hash
    
    def save(self, file_name: str = "hash.txt"):
        """Saves the last generated hash to a file."""
        file_output =[  
                      "MongoGBackup File Hash\n",
                      "--------------------------------------\n",
                      "SHA256 Checksum: " + self._last_hash+"\n",
                      "Generated at: " + str(self._last_hash_time)+" (local)",
                      ]
        with open(file_name, 'w') as f:
            f.writelines(file_output)
        
class FileEncryptor:
    """Encrypts and decrypts files using Fernet symmetric encryption."""
    
    def __init__(self, generate_key=False, key:str = None):
        """Initializes the Encryptor class."""
        
        if(not generate_key and key is None):
            raise ValueError("Either provide a key or generate_key must be set to True.")
        
        self._FERNET_KEY = Fernet.generate_key() + str(datetime.datetime.now().timestamp()).encode() if generate_key  else key
    
    def get_key(self):
        """Returns the encryption key."""
        return self._FERNET_KEY
    
    def encrypt_file(self, source_file_path:str, encrypted_file_path:str):
        """Encrypts a file using Fernet symmetric encryption."""
       
        # Create a Fernet Instance
        key = self._FERNET_KEY 
        f = Fernet(key)
        
        # Encrypt the file
        with open(source_file_path, 'rb') as file:
            data = file.read()
        encrypted = f.encrypt(data)
        
        # Write the encrypted file
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted)
        
        return encrypted_file_path
        
    def decrypt_file(self, encrypted_file_path, decrypted_file_path):
        """Decrypts a file using Fernet symmetric encryption."""
        
        # Create a Fernet Instance
        key = self._FERNET_KEY
        fernet = Fernet(key)
        
        # Decrypt the file
        with open(encrypted_file_path, 'rb') as enc_file:
            encrypted = enc_file.read()
        decrypted = fernet.decrypt(encrypted)
        
        # Write the decrypted file
        with open(decrypted_file_path, 'wb') as dec_file:
            dec_file.write(decrypted)
        return decrypted_file_path
