from flask import Flask, request, jsonify
from ecdsa import SigningKey, SECP256k1
from shamir_mnemonic import generate_mnemonics, combine_mnemonics  # ✅ Use `combine_mnemonics`
from nostr_sdk import Keys, Client, EventBuilder, Kind
import asyncio

app = Flask(__name__)

# Configuration: Total officials (`n`) and threshold (`t`)
n = 5  # Total number of officials
t = 3  # Minimum approvals needed

# Your Nostr (Strudel) Private Key
NOSTR_SECRET_KEY = "nsec15ruff0ehn7zd3dc3yjaq8n2vlmcz6ama3qhdx34vsp66pctpfy9qqggcws"

# Generate an ECDSA key pair
sk = SigningKey.generate(curve=SECP256k1)
private_key_bytes = sk.to_string()  # ✅ Get private key as bytes
private_key_hex = private_key_bytes.hex()  # Convert to hex

# Generate shares
# Ensure the private key is converted to a hex string and its format is valid
private_key_hex = private_key_bytes.hex()

# Check if private_key_hex is a valid string and has an even number of characters
if not isinstance(private_key_hex, str) or len(private_key_hex) % 2 != 0:
    raise ValueError("Private key must be a valid hex string with an even number of characters.")

# Generate mnemonics using the validated hex string
shares = generate_mnemonics(private_key_hex, t, n)


# Store shares (normally distributed securely)
official_shares = {i: share for i, share in enumerate(shares)}

# Store collected shares during a signing event
collected_shares = []


def reconstruct_private_key(shares):
    """Reconstruct the private key using threshold shares"""
    try:
        secret_hex = combine_mnemonics(shares)  # ✅ Use `combine_mnemonics()`
        return SigningKey.from_string(bytes.fromhex(secret_hex), curve=SECP256k1)
    except Exception as e:
        print(f"❌ Error reconstructing private key: {e}")
        return None


async def post_to_nostr(message, signature):
    """Asynchronously posts the signed emergency message to Nostr (Strudel)"""
    try:
        keys = Keys.from_nsec(NOSTR_SECRET_KEY)  # Load private key
        client = Client(keys)  # Create client instance
        await client.connect()  # Connect to Nostr relays
        
        # Build and publish the event
        event = EventBuilder.new_text_note(f"📢 Emergency Alert: {message}\n🔑 Signature: {signature}", [])
        signed_event = keys.sign_event(event)
        await client.send_event(signed_event)

        print(f"✅ Emergency Message Posted on Nostr: {signed_event.id}")
        return {"status": "Broadcasted", "event_id": signed_event.id}
    except Exception as e:
        print(f"❌ Failed to post on Nostr: {e}")
        return {"error": str(e)}


@app.route("/sign", methods=["POST"])
def sign_message():
    """Handles share submission and signing when threshold is met"""
    data = request.json
    official_id = data["official_id"]
    message = data["message"]

    if official_id not in official_shares:
        return jsonify({"error": "Invalid official ID"}), 400

    # Add the official's share to collected shares
    collected_shares.append(official_shares[official_id])
    print(f"✅ Received share from official {official_id}. Total shares collected: {len(collected_shares)}")

    if len(collected_shares) >= t:
        print("🚀 Threshold met! Signing message and broadcasting to Nostr.")

        # Reconstruct the private key
        recovered_sk = reconstruct_private_key(collected_shares[:t])
        if not recovered_sk:
            return jsonify({"error": "Failed to reconstruct private key"}), 500

        # Sign the message
        signature = recovered_sk.sign(message.encode()).hex()
        print(f"🔍 Generated Signature: {signature}")

        # Broadcast to Nostr (Strudel)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        broadcast_result = loop.run_until_complete(post_to_nostr(message, signature))

        return jsonify({"status": "Signed", "signature": signature, "broadcast_result": broadcast_result})

    return jsonify({"status": "Share Submitted", "total_shares": len(collected_shares)})


if __name__ == "__main__":
    app.run(debug=True)
