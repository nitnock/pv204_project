import os
import json
from frostpy import generate_keys_py

KEYS_DIR = "keys"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def save_share(participant_id, encoded_share):
    dir_path = os.path.join(KEYS_DIR, f"{participant_id}")
    ensure_dir(dir_path)
    file_path = os.path.join(dir_path, "secret_share.txt")
    with open(file_path, "w") as f:
        f.write(encoded_share)
    print(f" Saved share for participant {participant_id} → {file_path}")

def save_public_key_package(public_key_package):
    file_path = os.path.join(KEYS_DIR, "public_key_package.txt")
    try:
        with open(file_path, "w") as f:
            f.write(public_key_package)
        print(f" Group public key package saved → {file_path}")
    except Exception as e:
        print(f" Error saving public key package: {e}")

def save_group_public_key(group_verifying_key):
    file_path = os.path.join(KEYS_DIR, "public_key.txt")
    try:
        with open(file_path, "w") as f:
            f.write(group_verifying_key)
        print(f" Group verifying key saved → {file_path}")
    except Exception as e:
        print(f" Error saving group verifying key: {e}")

def generate_and_store_shares(n: int, t: int):
    print(f" Generating {n} FROST shares with threshold {t}...")
    try:
        raw_json = generate_keys_py(n, t)
    except Exception as e:
        print(f" Error during key generation: {e}")
        return

    try:
        result = json.loads(raw_json)
        shares = result["shares"]
        public_key_package = result["group_public_key"]
        group_verifying_key = result["group_verifying_key"]  # New field
    except Exception as e:
        print(f" JSON parsing error: {e}")
        return

    save_public_key_package(public_key_package)
    save_group_public_key(group_verifying_key)  # Save the verifying key

    for share in shares:
        pid = share["participant_id"]
        encoded = json.dumps(share["share"])
        print(f" Debug: Saving share for participant ID {pid}")
        save_share(pid, encoded)

    print(" All shares and public key package generated and saved successfully.")

if __name__ == "__main__":
    generate_and_store_shares(n=3, t=2)
