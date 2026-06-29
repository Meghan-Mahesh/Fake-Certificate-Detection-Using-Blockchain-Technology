import hashlib

def generate_hash(file):

    file.seek(0)        # Move pointer to beginning
    data = file.read()
    file.seek(0)        # Reset again for safety

    return hashlib.sha256(data).hexdigest()