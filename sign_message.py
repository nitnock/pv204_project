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
        print(f"Error reading share from {file_path}: {e}")
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
        print(f"Error reading public key package: {e}")
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

def sign_message(message: str, share_paths: List[str], threshold: int) -> str | None:
    """
    Sign a message using FROST threshold cryptography with the specified shares and threshold.
    """
    print(f"Signing message: '{message}' with threshold {threshold}")

    # Collect shares
    shares = collect_shares(share_paths)
    if len(shares) < threshold:
        print(f"❌ Error: Insufficient shares provided! Needed {threshold}, got {len(shares)}.")
        return None

    # Load the group public key package
    public_key_package = read_public_key_package()
    if not public_key_package:
        print("❌ Cannot sign message without the public key package.")
        return None

    # Prepare shares as a JSON string of KeyPackage structs
    shares_json = json.dumps(shares)
    print(f"🔍 Debug: Shares JSON prepared: {shares_json[:100]}...")  # Truncate for readability

    # Call the Rust signing function
    try:
        signature = sign_message_py(message, shares_json, threshold, public_key_package)
        print("Message signed successfully!")
        return signature
    except Exception as e:
        print(f"❌ Error during signing: {e}")
        return None

