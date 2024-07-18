from  mongogbackup import MongoConfig, MongoGBackup

mongoConfig = MongoConfig(
                                db_name='test_db',
                                host='localhost',
                                port=27017,
                            )

backup_handler = MongoGBackup(
                            mongoConfig=mongoConfig,
                            credentials_file='credentials.json',  
                            key='key'
                        )
# backup_handler.backups.backup(dir='output_path')
backup_handler.targz.pack(source_path='venv/', output_path='venv.tar.gz')

backup_handler.encrypt.encrypt_file('source.file', 'destination.file')
backup_handler.encrypt.decrypt_file('source.file', 'destination.file')

backup_handler.targz.unpack(source_path='venv.tar.gz', output_path='venv/')
backup_handler.backups.restore(bck_dir='output_path')

backup_handler.hash.generate_file_hash('source.file')