import os
import json
from typing import List

# Directory for storing keys and shares
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

def sign_message(message: str, shares: List[dict], threshold: int):
    """
    Sign a message using the provided shares and threshold.
    """
    print(f"🔐 Signing message: {message}")
    
    # Check if sufficient shares are provided
    if len(shares) < threshold:
        print(f"❌ Error: Insufficient shares provided! Needed {threshold}, got {len(shares)}.")
        return None

    # Combine shares (placeholder logic for demonstration)
    combined_value = "".join(share["value"] for share in shares[:threshold])  # Combine first `threshold` values
    signature = f"Signed({message})-{combined_value}"

    print(f"✅ Message approved and signed successfully!")
    return signature

def broadcast_message():
    """
    The main function for the message proposal and voting system.
    """
    print("📢 Welcome to the Emergency Broadcast System!")

    # Step 1: Message Proposal
    message = input("Enter the broadcast message: ").strip()
    print(f"📝 Proposed message: \"{message}\"")

    # Step 2: Collect Votes
    threshold = int(input("Enter the threshold (t) for approval: ").strip())
    n = int(input("Enter the number of participants (n): ").strip())

    print(f"📩 Collecting shares from participants...")
    share_files = []
    for i in range(n):
        file_path = input(f"Enter the file path for participant {i + 1}'s secret_share.txt: ").strip()
        share_files.append(file_path)

    shares = collect_shares(share_files)

    # Step 3: Threshold Check and Signing
    print(f"🔎 Checking if the threshold ({threshold}) is met...")
    signature = sign_message(message, shares, threshold)

    # Step 4: Broadcast the Message
    if signature:
        print("🌍 Broadcasting the message with the following details:")
        print(f"Message: {message}")
        print(f"Signature: {signature}")
        save_broadcast(message, signature)
    else:
        print("❌ Message rejected due to insufficient votes.")

def save_broadcast(message: str, signature: str):
    """
    Save the broadcast message and its signature to a file.
    """
    file_path = os.path.join(KEYS_DIR, "broadcast.txt")
    ensure_dir(KEYS_DIR)
    try:
        with open(file_path, "w") as f:
            f.write(f"Message: {message}\n")
            f.write(f"Signature: {signature}\n")
        print(f"✅ Broadcast details saved → {file_path}")
    except Exception as e:
        print(f"❌ Error saving broadcast details: {e}")

if __name__ == "__main__":
    broadcast_message()
