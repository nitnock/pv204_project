from flask import Flask, request, jsonify
from ecdsa import SigningKey, SECP256k1
import numpy as np
import random
import math

app = Flask(__name__)

n, t = 5, 3  # 3-of-5 threshold system
shares = []  # Stores received signature shares

# **Custom Shamir's Secret Sharing Implementation**
def generate_shares(secret, num_shares, threshold):
    """
    Split a secret into shares using Shamir's Secret Sharing.
    """
    coeffs = [secret] + [random.randint(1, 2**256) for _ in range(threshold - 1)]
    shares = []
    
    for x in range(1, num_shares + 1):
        y = sum([coeff * (x**i) for i, coeff in enumerate(coeffs)])
        shares.append((x, y))
    
    return shares

def reconstruct_secret(shares):
    """
    Reconstruct the secret from at least 't' shares using Lagrange interpolation.
    """
    def lagrange_interpolate(x, x_values, y_values):
        """
        Perform Lagrange interpolation at x = 0 to reconstruct the secret.
        """
        total = 0
        modulus = 2**256  # Large prime modulus for cryptographic security

        print(f"🔹 x_values: {x_values}")
        print(f"🔹 y_values: {y_values}")

        for i in range(len(x_values)):
            term = y_values[i]
            print(f"\n➡️ Processing term {i}: y_value = {term}")

            for j in range(len(x_values)):
                if i != j:
                    denominator = (x_values[i] - x_values[j]) % modulus  # Ensure it's within modulus
                    if denominator < 0:
                        denominator += modulus  # Make sure denominator is positive
                    
                    # Ensure denominator is not zero
                    if denominator == 0:
                        print(f"  ❌ Error: Zero denominator detected! Skipping term.")
                        return None

                    print(f"  ⚙️ Computing inverse of denominator ({x_values[i]} - {x_values[j]}) mod {modulus} = {denominator}")

                    # **New Fix: Try to Compute Modular Inverse Safely**
                    try:
                        inverse_denominator = pow(denominator, modulus - 2, modulus)  # Using Fermat's Theorem for inversion
                        print(f"  ✅ Modular inverse found: {inverse_denominator}")
                    except ValueError:
                        print(f"  ❌ Cannot find modular inverse for {denominator}, skipping term.")
                        return None  # Return None if an error occurs

                    term = (term * (x - x_values[j]) * inverse_denominator) % modulus
                    print(f"  🔄 Updated term: {term}")

            total = (total + term) % modulus

        print(f"✅ Reconstructed Secret: {total}")
        return total





# **Generate an ECDSA key pair**
sk = SigningKey.generate(curve=SECP256k1)
vk = sk.verifying_key

# Convert private key to integer
private_key_int = int.from_bytes(sk.to_string(), byteorder="big")

# Generate shares
key_shares = generate_shares(private_key_int, n, t)

@app.route('/sign', methods=['POST'])
def sign_message():
    global shares
    data = request.json
    official_id = data['official_id']
    message = data['message']

    if len(shares) < t:
        share = key_shares[official_id]
        shares.append(share)
        print(f"✅ Received share from official {official_id}. Total shares collected: {len(shares)}")  # Debugging print

        if len(shares) >= t:
            print("🚀 Threshold met! Reconstructing private key and signing message.")
            recovered_private_key_int = reconstruct_secret(shares[:t])
            
            if recovered_private_key_int is None:
                return jsonify({"error": "Failed to reconstruct private key"}), 500
            
            recovered_sk = SigningKey.from_string(recovered_private_key_int.to_bytes(32, byteorder="big"), curve=SECP256k1)
            signature = recovered_sk.sign(message.encode()).hex()
            print(f"🔍 Generated Signature: {signature}")  # Debugging print

            return jsonify({"status": "Signed", "signature": signature})

        return jsonify({"status": "Share Submitted", "total_shares": len(shares)})

    return jsonify({"error": "Threshold already met"}), 400


@app.route('/verify', methods=['POST'])
def verify_signature():
    data = request.json
    message = data['message'].encode()
    signature = data['signature']

    # Debugging: Print the received signature
    print(f"🔍 Received Signature: {signature}")

    try:
        signature_bytes = bytes.fromhex(signature)
    except ValueError:
        return jsonify({"error": "Invalid signature format. Expected a hex string."}), 400

    valid = vk.verify(signature_bytes, message)
    return jsonify({"status": "Valid" if valid else "Invalid"})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
