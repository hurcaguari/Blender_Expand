import zlib , sys
import hashlib
from os.path import exists


def sha256(text: str):
#    """生成SHA256摘要"""
    return hashlib.sha256(text.encode()).hexdigest()

print(sha256('aaaaaaaaaaaaaaa'))

def file_hash(file_path:str,hash_method) -> str:
    return False if not exists(file_path) else True