import tarfile
import os

def generate_tar_gz( source_path:str, output_path:str)  -> str:
    """Generates a tar.gz file from a source path."""    
    with tarfile.open(output_path, 'w:gz') as tar:
        tar.add(source_path, arcname=os.path.basename(source_path))
    return output_path
    
def unpack_tar_gz(source_path:str, output_path:str) -> str:
    """Unpacks a tar.gz file to a specified output path."""
    with tarfile.open(source_path, 'r:gz') as tar:
        tar.extractall(output_path)
    return output_path
    