def save_hash(hash_value, filepath='last_hash.txt') -> None:
    with open(filepath, 'w') as file:
        file.write(hash_value)


def load_hash(filepath='last_hash.txt') -> str | None:
    try:
        with open(filepath) as file:
            return file.readline().strip()
    except FileNotFoundError:
        return None
