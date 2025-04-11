# [Unchanged from your original]
import argparse
import sys
import os
from keygen import generate_and_store_shares
from sign_message import sign_message, save_signature
from verify_signature import verify_signature, read_signature, read_public_key

KEYS_DIR = "keys"

def sign(message, threshold, share_paths):
    signature = sign_message(message, share_paths, threshold)
    if signature:
        print(f"✅ Signature generated: {signature}")
        save_signature(signature, message)  # Updated call to pass message
    else:
        print("❌ Failed to sign the message.")

def verify(message):
    signature = read_signature()
    public_key = read_public_key()
    if signature and public_key:
        is_valid = verify_signature(message, signature, public_key)
        if is_valid is not None:
            if is_valid:
                print("✅ The signature is valid!")
            else:
                print("❌ The signature is invalid.")
        else:
            print("❌ Failed to verify the signature due to an error.")
    else:
        print("❌ Failed to load the signature or public key.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Threshold Cryptography CLI using FROST")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    generate_parser = subparsers.add_parser("generate", help="Generate keys and shares")
    generate_parser.add_argument("--n", type=int, required=True, help="Number of participants")
    generate_parser.add_argument("--t", type=int, required=True, help="Signing threshold")

    sign_parser = subparsers.add_parser("sign", help="Sign a message with participant shares")
    sign_parser.add_argument("--message", type=str, required=True, help="Message to sign")
    sign_parser.add_argument("--threshold", type=int, required=True, help="Threshold for signing")
    sign_parser.add_argument("--shares", nargs="+", required=True, help="Paths to share files")

    verify_parser = subparsers.add_parser("verify", help="Verify a signature")
    verify_parser.add_argument("--message", type=str, required=True, help="Message to verify")

    args = parser.parse_args()

    if args.command == "generate":
        generate_and_store_shares(args.n, args.t)
    elif args.command == "sign":
        sign(args.message, args.threshold, args.shares)
    elif args.command == "verify":
        verify(args.message)
    else:
        parser.print_help()
        sys.exit(1)