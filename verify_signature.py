import os
import json  # Add this import
from frostpy import verify_signature_py

KEYS_DIR = "keys"

def read_signature():
    file_path = os.path.join(KEYS_DIR, "signature.txt")
    try:
        with open(file_path, "r") as f:
            data = json.load(f)  # Parse JSON
            return data["signature"]  # Extract signature
    except Exception as e:
        print(f"Error reading signature: {e}")
        return None

def read_public_key():
    file_path = os.path.join(KEYS_DIR, "public_key.txt")
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading public key: {e}")
        return None

def verify_signature(message: str, signature: str, public_key: str) -> bool | None:
    print(f"🔍 Verifying signature for message: '{message}'")
    try:
        is_valid = verify_signature_py(message, signature, public_key)
        print(f"Signature is {'valid' if is_valid else 'invalid'}")
        return is_valid
    except Exception as e:
        print(f"Verification error: {e}")
        return None

if __name__ == "__main__":
    message = "Emergency broadcast: System going offline."
    signature = read_signature()
    public_key = read_public_key()
    if signature and public_key:
        result = verify_signature(message, signature, public_key)
        if result is not None:
            print(f"Verification result: {result}")
        else:
            print("Failed to verify signature.")
    else:
        print("Missing signature or public key.")
