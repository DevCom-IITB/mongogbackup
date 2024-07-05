from hashlib import sha256
import datetime

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
        
class Encryptor:
    def __init__(self):
        pass