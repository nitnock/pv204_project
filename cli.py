import argparse
import sys
import os
from keygen import generate_and_store_shares  # Key generation function
from sign_message import sign_message, save_signature  # Updated to use share_paths
from verify_signature import verify_signature, read_signature, read_public_key

# Path for keys and files
KEYS_DIR = "keys"

def sign(message, threshold, share_paths):
    """
    Sign a message using participant share file paths.
    """
    signature = sign_message(message, share_paths, threshold)
    if signature:
        print(f"✅ Signature generated: {signature}")
        save_signature(signature)
    else:
        print("❌ Failed to sign the message.")

def verify(message):
    """
    Verify the authenticity of a message and its signature using the group public key.
    """
    signature = read_signature()
    public_key = read_public_key()
    if signature and public_key:
        is_valid = verify_signature(message, signature, public_key)
        if is_valid is not None:  # Check for None in case of verification error
            if is_valid:
                print("✅ The signature is valid!")
            else:
                print("❌ The signature is invalid.")
        else:
            print("❌ Failed to verify the signature due to an error.")
    else:
        print("❌ Failed to load the signature or public key for verification.")

if __name__ == "__main__":
    # Define CLI commands
    parser = argparse.ArgumentParser(description="Threshold Cryptography CLI using FROST")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Key generation command
    generate_parser = subparsers.add_parser("generate", help="Generate keys and shares")
    generate_parser.add_argument("--n", type=int, required=True, help="Number of participants (e.g., 3)")
    generate_parser.add_argument("--t", type=int, required=True, help="Signing threshold (e.g., 2)")

    # Signing command
    sign_parser = subparsers.add_parser("sign", help="Sign a message with participant shares")
    sign_parser.add_argument("--message", type=str, required=True, help="Message to sign")
    sign_parser.add_argument("--threshold", type=int, required=True, help="Threshold for signing (e.g., 2)")
    sign_parser.add_argument("--shares", nargs="+", required=True, help="Paths to participant share files (e.g., keys/1/secret_share.txt keys/2/secret_share.txt)")

    # Verification command
    verify_parser = subparsers.add_parser("verify", help="Verify a signature against the group public key")
    verify_parser.add_argument("--message", type=str, required=True, help="Message to verify")

    # Parse and execute commands
    args = parser.parse_args()

    if args.command == "generate":
        # Handle key generation
        generate_and_store_shares(args.n, args.t)
    elif args.command == "sign":
        # Handle message signing
        sign(args.message, args.threshold, args.shares)
    elif args.command == "verify":
        # Handle signature verification
        verify(args.message)
    else:
        parser.print_help()
        sys.exit(1)
