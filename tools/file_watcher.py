import hashlib


def file_hash(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def has_file_changed(filepath: str, previous_hash: str) -> tuple[bool, str]:
    current_hash = file_hash(filepath)
    return current_hash != previous_hash, current_hash
