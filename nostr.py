import asyncio
from nostr_sdk import Keys, Client, EventBuilder, NostrSigner
import os
import json
import frostpy

KEYS_DIR = "keys"
LATEST_SIGNATURE_FILE = os.path.join(KEYS_DIR, "latest_signature.txt")

async def publish_frost_event():
    try:
        #___________ATTENTION___________
        private_key_hex = "nsec25ruff1ehn7zd3dc3yjaq8n2vlmcz6ama3qhdx34vsp66pctpfy9hqgfcws" #This is a dummy key and won't work. 
        #Kindly replace it with your own key from no-struddle.  
        
        
        signature_file = LATEST_SIGNATURE_FILE
        public_key_file = os.path.join(KEYS_DIR, "public_key.txt")

        if not os.path.exists(signature_file):
            raise FileNotFoundError(f"Signature file not found at {signature_file}. Run 'python cli.py broadcast' first.")
        with open(signature_file, "r") as f:
            data = json.load(f)
            frost_signature_b64 = data["signature"]
            frost_message = data["message"]

        if not os.path.exists(public_key_file):
            raise FileNotFoundError(f"Public key file not found at {public_key_file}. Run 'python cli.py generate' first.")
        with open(public_key_file, "r") as f:
            public_key_b64 = f.read().strip()

        if not frostpy.verify_signature_py(frost_message, frost_signature_b64, public_key_b64):
            raise ValueError("FROST signature verification failed.")
        print("✅ FROST signature verified successfully")

        keys = Keys.parse(private_key_hex)
        signer = NostrSigner.keys(keys)
        client = Client(signer)

        await client.add_relay("wss://nos.lol/")
        await client.add_relay("wss://relay.damus.io/")
        await client.connect()
        await asyncio.sleep(1)

        message = f"{frost_message}\nFROST Signature: {frost_signature_b64}"
        event_builder = EventBuilder.text_note(message)

        res = await client.send_event_builder(event_builder)
        event_id = res.id.to_bech32() if res.id else "Failed to get ID"
        print(f"FROST Message: {frost_message}")
        print(f"FROST Signature: {frost_signature_b64}")
        print(f"Nostr Event ID: {event_id}")
        print(f"Sent to: {res.success}")
        print(f"Not sent to: {res.failed}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(publish_frost_event())
