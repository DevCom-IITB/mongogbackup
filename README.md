# mongogbackup
Secure Mongo DB backups on Google Drive

## Installation
```bash
$ pip install mongogbackup
```

## Usage
### Import
```python
from  mongogbackup import MongoConfig, MongoGBackup
```

### Initialization
```python
mongo_config = MongoConfig(
                                db_name='your_db',
                                host='localhost',
                                port=27017,
                                # optional parameters below
                                username='root',
                                password='password',
                                auth_db='admin'
                            )
backup_handler =MongoGBackup(
                            mongoConfig=mongo_config,
                            credentials_file='path/credentials.json',  
                            key='fernet_key'
                        )
```
## Creating dump
```python
backup_handler.backups.backup(dir='backup_path/dump/')
```
### Compressing the dump
```python
backup_handler.targz.pack(source_path='backup_path/dump/', output_path='filename.tar.gz')
```
### Encrypting the dump
```python
backup_handler.encrypt.encrypt_file('filename.tar.gz', 'destination.file')
```
### Uploading to Google Drive
```python
# To-Do: write upload instructions
```

## Restore Backups
Download the backup file from google drive (say: backup.encr)

### Decrypt the file
```python
backup_handler.encrypt.encrypt_file('backup.encr', 'filename.tar.gz')
```
### Decompressing the tar-gz dump
```python
backup_handler.targz.unpack(source_path='filename.tar.gz', output_path='backup_dir/dump/')
```

### Restoring the dump
```python
backup_handler.backups.restore(bck_dir='backup_dir/dump/')
```

## Hash Checks
To ensure that your backup file has not been tampered with, you can perform a SHA-256 hash check.

```python
backup_handler.hash.generate_file_hash('source.file')
```

You can also save the hash into a txt file by executing
```python
backup_handler.hash.save('hash.txt')
```

or print the hash by executing
```python
print(backup_handler.hash.last_hash())
```

You can also compare the current generated hash with any other string using
```python
backup_handler.hash.compare_generated('hash-string')
# returns True or False on comparision
```

Made with ❤️ by DevCom, 2024