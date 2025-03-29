import os
import json
from frostpy import generate_keys_py

KEYS_DIR = "keys" # Directory to save generated shares and the public key

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# Method to save participant's shares into a file in a directory
def save_share(participant_id, encoded_share):
    dir_path = os.path.join(KEYS_DIR, f"{participant_id}")
    ensure_dir(dir_path)
    file_path = os.path.join(dir_path, "secret_share.txt")
    with open(file_path, "w") as f:
        f.write(encoded_share)
    print(f"Saved share for participant {participant_id} → {file_path}")


def save_public_key_package(public_key_package):
    file_path = os.path.join(KEYS_DIR, "public_key_package.txt")
    try:
        with open(file_path, "w") as f:
            f.write(public_key_package)
        print(f"Group public key package saved → {file_path}")
    except Exception as e:
        print(f"Error saving public key package: {e}")


def generate_and_store_shares(n: int, t: int):
    """
    Generate `n` shares with a threshold `t` and save them along with the group public key.
    """
    print(f"Generating {n} FROST shares with threshold {t}...")
    try:
        # Generate shares using the frostpy module
        raw_json = generate_keys_py(n, t)
    except Exception as e:
        print(f"Error during key generation: {e}")
        return

    try:
        # Parse the JSON result to get shares and the public key
        result = json.loads(raw_json)
        shares = result["shares"]  # Extract shares from the result
        public_key = result["group_public_key"]  # Extract the group public key
    except Exception as e:
        print(f"JSON parsing error: {e}")
        return

    # Save the group public key
    save_public_key_package(public_key_package)


    # Loop through each share and save it
    for share in shares:
        pid = share["participant_id"]  # Get the participant ID
        encoded = share["share"]  # Get the encoded secret share
        print(f"🔍 Debug: Saving share for participant ID {pid}")
        save_share(pid, encoded)

    print("All shares and public key generated and saved successfully.")


if __name__ == "__main__":
    # Specify the number of participants (n) and threshold (t)
    generate_and_store_shares(n=3, t=2)