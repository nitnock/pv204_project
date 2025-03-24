import argparse
import sys
import os
from keygen import generate_keys_py
from sign_message import read_share, collect_shares, sign_message, save_signature
from verify_signature import verify_signature, read_signature
from broadcast_workflow import save_broadcast
import json


# Path for keys and files
KEYS_DIR = "keys"

def save_shares(shares):
    """
    Save each participant's share to a separate file.
    """
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)

    for share in shares:
        participant_id = share["participant_id"]
        participant_dir = os.path.join(KEYS_DIR, f"{participant_id}")
        os.makedirs(participant_dir, exist_ok=True)

        share_file = os.path.join(participant_dir, "secret_share.txt")
        with open(share_file, "w") as f:
            f.write(share["share"])

        print(f"✅ Saved share for participant {participant_id} → {share_file}")

def generate_keys(n, t):
    """
    Generate keys for participants and save them to files.
    """
    print(f"🔑 Generating keys for {n} participants with threshold {t}...")
    try:
        # Call the Rust key generation function
        raw_json = generate_keys_py(n, t)
        shares = json.loads(raw_json)  # Parse the JSON result

        # Save each share to a file
        save_shares(shares)

        print(f"✅ Keys generated and saved successfully!")
    except Exception as e:
        print(f"❌ Key generation failed: {e}")

def sign(message, threshold, share_paths):
    """
    Sign a message using participant shares.
    """
    shares = collect_shares(share_paths)
    signature = sign_message(message, shares, threshold)
    if signature:
        print(f"✅ Signature generated: {signature}")
        save_signature(signature)
    else:
        print("❌ Failed to sign the message.")

def verify(message, share_paths):
    """
    Verify the authenticity of a message and its signature.
    """
    shares = collect_shares(share_paths)
    signature = read_signature()
    if signature:
        is_valid = verify_signature(message, signature, shares, len(share_paths))
        if is_valid:
            print("✅ The signature is valid!")
        else:
            print("❌ The signature is invalid.")
    else:
        print("❌ Failed to load the signature for verification.")

def broadcast(message, threshold, share_paths):
    """
    Propose and broadcast a message.
    """
    print(f"📣 Broadcasting the message: \"{message}\"")
    shares = collect_shares(share_paths)
    signature = sign_message(message, shares, threshold)
    if signature:
        print("✅ Message approved and signed.")
        save_broadcast(message, signature)
    else:
        print("❌ Message not approved due to insufficient votes.")

if __name__ == "__main__":
    # Define CLI commands
    parser = argparse.ArgumentParser(description="Emergency Broadcast System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Key generation command
    generate_parser = subparsers.add_parser("generate", help="Generate keys")
    generate_parser.add_argument("--n", type=int, required=True, help="Number of participants")
    generate_parser.add_argument("--t", type=int, required=True, help="Threshold for signing")

    # Signing command
    sign_parser = subparsers.add_parser("sign", help="Sign a message")
    sign_parser.add_argument("--message", type=str, required=True, help="Message to sign")
    sign_parser.add_argument("--threshold", type=int, required=True, help="Threshold for approval")
    sign_parser.add_argument("--shares", nargs="+", required=True, help="Paths to participant shares")

    # Verification command
    verify_parser = subparsers.add_parser("verify", help="Verify a signature")
    verify_parser.add_argument("--message", type=str, required=True, help="Message to verify")
    verify_parser.add_argument("--shares", nargs="+", required=True, help="Paths to participant shares")

    # Broadcast command
    broadcast_parser = subparsers.add_parser("broadcast", help="Broadcast a message")
    broadcast_parser.add_argument("--message", type=str, required=True, help="Message to broadcast")
    broadcast_parser.add_argument("--threshold", type=int, required=True, help="Threshold for approval")
    broadcast_parser.add_argument("--shares", nargs="+", required=True, help="Paths to participant shares")

    # Parse and execute commands
    args = parser.parse_args()
    if args.command == "generate":
        generate_keys(args.n, args.t)
    elif args.command == "sign":
        sign(args.message, args.threshold, args.shares)
    elif args.command == "verify":
        verify(args.message, args.shares)
    elif args.command == "broadcast":
        broadcast(args.message, args.threshold, args.shares)
    else:
        print("❌ Invalid command. Use --help to see available options.")