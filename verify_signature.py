import os
import json
from typing import List

# Path to the keys folder
KEYS_DIR = "keys"

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

def read_signature():
    """
    Read the previously saved signature from the signature file.
    """
    file_path = os.path.join(KEYS_DIR, "signature.txt")
    try:
        with open(file_path, "r") as f:
            signature = f.read()
        print(f"✅ Signature loaded → {file_path}")
        return signature
    except Exception as e:
        print(f"❌ Error reading signature: {e}")
        return None

def interpolate_commitments(shares, threshold):
    """
    Interpolate commitments from participant shares using placeholder logic.
    """
    interpolated_commitment = "".join(share["commitment"][0] for share in shares[:threshold])
    return interpolated_commitment

def verify_signature(message, signature, shares, threshold):
    """
    Verify the validity of a signature using any number of shares (meeting or exceeding the threshold).
    """
    print(f"🔎 Verifying signature for message: {message}")

    # Ensure sufficient shares
    if len(shares) < threshold:
        print(f"❌ Error: Insufficient shares provided! Needed {threshold}, got {len(shares)}.")
        return False

    # Reconstruct the group commitment dynamically using placeholder logic
    group_commitment = interpolate_commitments(shares, threshold)
    expected_signature = f"Signed({message})-{group_commitment}"

    # Compare signatures
    if signature == expected_signature:
        print(f"✅ Signature verification succeeded!")
        return True
    else:
        print(f"❌ Signature verification failed!")
        return False


if __name__ == "__main__":
    # Example usage
    message = "Emergency broadcast: System going offline."
    threshold = 2  # Minimum number of shares required for verification

    # List of participant share files to use
    share_files = [
        os.path.join(KEYS_DIR, "0_0", "secret_share.txt"),
        os.path.join(KEYS_DIR, "0_1", "secret_share.txt"),
    ]

    # Load the previously saved signature
    provided_signature = read_signature()
    if provided_signature:
        # Collect the shares
        shares = collect_shares(share_files)

        # Verify the signature
        is_valid = verify_signature(message, provided_signature, shares, threshold)

        if is_valid:
            print("The signature is valid!")
        else:
            print("The signature is invalid.")
    else:
        print("Failed to load the signature.")
