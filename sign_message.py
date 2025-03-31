import os
import json
from typing import List
from frostpy import sign_message_py  # Import the Rust signing function

KEYS_DIR = "keys"

def ensure_dir(path):
    """
    Ensure that a directory exists.
    """
    os.makedirs(path, exist_ok=True)

def read_share(file_path):
    """
    Read and parse the secret share from a file into a Python dictionary.
    """
    try:
        with open(file_path, "r") as f:
            share_data = json.loads(f.read())  # Parse the JSON string into a dict
        return share_data
    except Exception as e:
        print(f"❌ Error reading share from {file_path}: {e}")
        return None

def collect_shares(share_paths: List[str]):
    """
    Collect and validate shares from the provided file paths, returning them as a list of dictionaries.
    """
    shares = []
    for path in share_paths:
        share = read_share(path)
        if share:
            shares.append(share)
        else:
            print(f"Skipping invalid share at {path}")
    return shares

def read_public_key_package():
    """
    Read the group public key package from a file.
    """
    file_path = os.path.join(KEYS_DIR, "public_key_package.txt")
    try:
        with open(file_path, "r") as f:
            public_key_package = f.read()
        print(f"Public key package loaded → {file_path}")
        return public_key_package
    except Exception as e:
        print(f"❌ Error reading public key package: {e}")
        return None

def save_signature(signature):
    """
    Save the generated signature to a file.
    """
    file_path = os.path.join(KEYS_DIR, "signature.txt")
    try:
        with open(file_path, "w") as f:
            f.write(signature)
        print(f"Signature saved → {file_path}")
    except Exception as e:
        print(f"❌ Error saving signature: {e}")

