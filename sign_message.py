import os
import json
from typing import List
from frostpy import sign_message_py

KEYS_DIR = "keys"
SIGNATURES_FILE = os.path.join(KEYS_DIR, "signatures.txt")
LATEST_SIGNATURE_FILE = os.path.join(KEYS_DIR, "latest_signature.txt")

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def read_share(file_path):
    try:
        with open(file_path, "r") as f:
            share_data = json.loads(f.read())
        return share_data
    except Exception as e:
        print(f"Error reading share from {file_path}: {e}")
        return None

def collect_shares(share_paths: List[str]):
    shares = []
    for path in share_paths:
        share = read_share(path)
        if share:
            shares.append(share)
        else:
            print(f"Skipping invalid share at {path}")
    return shares

def read_public_key_package():
    file_path = os.path.join(KEYS_DIR, "public_key_package.txt")
    try:
        with open(file_path, "r") as f:
            public_key_package = f.read()
        print(f"Public key package loaded → {file_path}")
        return public_key_package
    except Exception as e:
        print(f"Error reading public key package: {e}")
        return None

def save_signature(signature: str, message: str):
    ensure_dir(KEYS_DIR)
    # Append to signatures.txt as a list
    entry = {"message": message, "signature": signature}
    if os.path.exists(SIGNATURES_FILE):
        with open(SIGNATURES_FILE, "r") as f:
            signatures = json.load(f)
    else:
        signatures = []
    signatures.append(entry)
    with open(SIGNATURES_FILE, "w") as f:
        json.dump(signatures, f)
    print(f"Signature appended to → {SIGNATURES_FILE}")
    
    # Write only the latest to latest_signature.txt
    with open(LATEST_SIGNATURE_FILE, "w") as f:
        json.dump(entry, f)
    print(f"Latest signature saved → {LATEST_SIGNATURE_FILE}")

def sign_message(message: str, share_paths: List[str], threshold: int) -> str | None:
    print(f" Signing message: '{message}' with threshold {threshold}")
    shares = collect_shares(share_paths)
    if len(shares) < threshold:
        print(f"Error: Insufficient shares provided! Needed {threshold}, got {len(shares)}.")
        return None

    public_key_package = read_public_key_package()
    if not public_key_package:
        print("Cannot sign message without the public key package.")
        return None

    shares_json = json.dumps(shares)
    try:
        signature_b64, signed_message = sign_message_py(message, shares_json, threshold, public_key_package)
        print("Message signed successfully!")
        save_signature(signature_b64, signed_message)
        return signature_b64
    except Exception as e:
        print(f"Error during signing: {e}")
        return None

if __name__ == "__main__":
    message = "Emergency broadcast: System going offline."
    threshold = 2
    share_files = [
        os.path.join(KEYS_DIR, "1", "secret_share.txt"),
        os.path.join(KEYS_DIR, "2", "secret_share.txt"),
    ]
    signature = sign_message(message, share_files, threshold)
    if signature:
        print(f"Generated Signature: {signature}")
    else:
        print("Failed to generate the signature.")
