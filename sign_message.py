import os
import json
from typing import List

# Path to the keys folder
KEYS_DIR = "keys"

def ensure_dir(path):
    """
    Ensure that a directory exists.
    """
    os.makedirs(path, exist_ok=True)

def read_share(file_path):
    """
    Read the secret share from a file.
    """
    try:
        with open(file_path, "r") as f:
            share_data = json.load(f)  # Load the JSON content
        return share_data
    except Exception as e:
        print(f"❌ Error reading share from {file_path}: {e}")
        return None

def collect_shares(share_paths: List[str]):
    """
    Collect and validate shares from the provided file paths.
    """
    shares = []
    for path in share_paths:
        share = read_share(path)
        if share:
            shares.append(share)
    return shares

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

def sign_message(message, shares, threshold):
    """
    Sign a message using the provided shares and threshold.
    """
    print(f"Signing message: {message}")
    
    # Ensure sufficient shares
    if len(shares) < threshold:
        print(f"Error: Insufficient shares provided! Needed {threshold}, got {len(shares)}.")
        return None

    # Reconstruct the group commitment (placeholder logic for now)
    group_commitment = "".join(share["commitment"][0] for share in shares[:threshold])  # Combine commitments

    # Create signature
    signature = f"Signed({message})-{group_commitment}"

    print(f"Message signed successfully!")
    return signature


if __name__ == "__main__":
    # Example usage
    message = "Emergency broadcast: System going offline."
    threshold = 2  # Minimum number of shares required to sign a message

    # List of participant share files to use
    share_files = [
        os.path.join(KEYS_DIR, "0_0", "secret_share.txt"),
        os.path.join(KEYS_DIR, "0_1", "secret_share.txt"),
    ]

    # Collect the shares
    shares = collect_shares(share_files)

    # Attempt to sign the message
    signature = sign_message(message, shares, threshold)

    if signature:
        print(f"Generated Signature: {signature}")
        save_signature(signature)
    else:
        print("Failed to generate the signature.")
