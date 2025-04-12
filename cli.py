import argparse
import sys
import os
import json
from keygen import generate_and_store_shares
from sign_message import sign_message, save_signature
from verify_signature import verify_signature, read_signature, read_public_key

KEYS_DIR = "keys"
MESSAGES_FILE = "messages.txt"
SIGNATURES_FILE = os.path.join(KEYS_DIR, "signatures.txt")
LATEST_SIGNATURE_FILE = os.path.join(KEYS_DIR, "latest_signature.txt")

def ensure_messages_file():
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "w") as f:
            f.write("")

def submit_message(message):
    ensure_messages_file()
    with open(MESSAGES_FILE, "r+") as f:
        messages = [json.loads(line) for line in f if line.strip()]
        new_id = max([m["id"] for m in messages], default=0) + 1
        new_message = {"id": new_id, "message": message, "status": "pending", "signatures": []}
        f.write(json.dumps(new_message) + "\n")
    print(f" Message submitted: ID {new_id} - '{message}'")

def list_messages():
    ensure_messages_file()
    with open(MESSAGES_FILE, "r") as f:
        messages = [json.loads(line) for line in f if line.strip()]
    if not messages:
        print("No messages pending.")
        return
    print("Pending Messages:")
    for m in messages:
        sig_count = len(m["signatures"])
        print(f"ID {m['id']}: '{m['message']}' (Signatures: {sig_count})")

def sign_partial(message_id, share_path):
    ensure_messages_file()
    with open(MESSAGES_FILE, "r") as f:
        lines = f.readlines()
    messages = [json.loads(line) for line in lines if line.strip()]
    message = next((m for m in messages if m["id"] == message_id), None)
    if not message or message["status"] != "pending":
        print(f" Message ID {message_id} not found or already processed.")
        return

    share_file = share_path.split("/")[-2]  # Extract participant ID (e.g., "1" from "keys/1/secret_share.txt")
    if any(sig["share"] == share_file for sig in message["signatures"]):
        print(f" Share {share_file} already signed this message.")
        return

    message["signatures"].append({"share": share_file})
    with open(MESSAGES_FILE, "w") as f:
        for m in messages:
            f.write(json.dumps(m) + "\n")
    print(f" Share {share_file} signed message ID {message_id}. Total signatures: {len(message['signatures'])}")

def sign(message, threshold, share_paths):
    signature = sign_message(message, share_paths, threshold)
    if signature:
        print(f" Signature generated: {signature}")
        save_signature(signature, message)
    else:
        print(" Failed to sign the message.")

def verify(message):
    signature = read_signature(message)  # Pass message to find the correct signature
    public_key = read_public_key()
    if signature and public_key:
        is_valid = verify_signature(message, signature, public_key)
        if is_valid is not None:
            if is_valid:
                print(" The signature is valid!")
            else:
                print(" The signature is invalid.")
        else:
            print(" Failed to verify the signature due to an error.")
    else:
        print(" Failed to load the signature or public key.")

def broadcast(message_id, threshold):
    ensure_messages_file()
    with open(MESSAGES_FILE, "r") as f:
        lines = f.readlines()
    messages = [json.loads(line) for line in lines if line.strip()]
    message = next((m for m in messages if m["id"] == message_id), None)
    if not message or message["status"] != "pending":
        print(f" Message ID {message_id} not found or already broadcasted.")
        return

    sig_count = len(message["signatures"])
    if sig_count < threshold:
        print(f" Insufficient signatures: {sig_count}/{threshold}.")
        return

    share_paths = [os.path.join(KEYS_DIR, sig["share"], "secret_share.txt") for sig in message["signatures"]]
    signature = sign_message(message["message"], share_paths, threshold)
    if signature:
        message["status"] = "broadcasted"
        with open(MESSAGES_FILE, "w") as f:
            for m in messages:
                f.write(json.dumps(m) + "\n")
        save_signature(signature, message["message"])
        print(f" Message ID {message_id} signed and ready for Nostr broadcast.")
        os.system("python nostr.py")  # Run nostr.py to broadcast
    else:
        print(" Failed to finalize signature.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Emergency Broadcast System CLI using FROST")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    generate_parser = subparsers.add_parser("generate", help="Generate keys and shares")
    generate_parser.add_argument("--n", type=int, required=True, help="Number of participants")
    generate_parser.add_argument("--t", type=int, required=True, help="Signing threshold")

    submit_parser = subparsers.add_parser("submit", help="Submit a new emergency message")
    submit_parser.add_argument("--message", type=str, required=True, help="Emergency message")

    list_parser = subparsers.add_parser("list", help="List pending messages")

    sign_partial_parser = subparsers.add_parser("sign-partial", help="Sign a message with a share")
    sign_partial_parser.add_argument("--id", type=int, required=True, help="Message ID to sign")
    sign_partial_parser.add_argument("--share", type=str, required=True, help="Path to share file (e.g., keys/1/secret_share.txt)")

    sign_parser = subparsers.add_parser("sign", help="Sign a message with participant shares")
    sign_parser.add_argument("--message", type=str, required=True, help="Message to sign")
    sign_parser.add_argument("--threshold", type=int, required=True, help="Threshold for signing")
    sign_parser.add_argument("--shares", nargs="+", required=True, help="Paths to share files")

    verify_parser = subparsers.add_parser("verify", help="Verify a signature")
    verify_parser.add_argument("--message", type=str, required=True, help="Message to verify")

    broadcast_parser = subparsers.add_parser("broadcast", help="Finalize and broadcast a message")
    broadcast_parser.add_argument("--id", type=int, required=True, help="Message ID to broadcast")
    broadcast_parser.add_argument("--threshold", type=int, required=True, help="Threshold for signing")

    args = parser.parse_args()

    if args.command == "generate":
        generate_and_store_shares(args.n, args.t)
    elif args.command == "submit":
        submit_message(args.message)
    elif args.command == "list":
        list_messages()
    elif args.command == "sign-partial":
        sign_partial(args.id, args.share)
    elif args.command == "sign":
        sign(args.message, args.threshold, args.shares)
    elif args.command == "verify":
        verify(args.message)
    elif args.command == "broadcast":
        broadcast(args.id, args.threshold)
    else:
        parser.print_help()
        sys.exit(1)