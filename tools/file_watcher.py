import hashlib


def file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def has_file_changed(filepath, previous_hash):
    current_hash = file_hash(filepath)
    return current_hash != previous_hash, current_hash
