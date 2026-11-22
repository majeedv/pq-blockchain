"""Standalone real ECDSA transaction demo. Run: python -m crypto.ecdsa_transaction_demo"""
import json
from crypto.signer import get_signer


def transaction_bytes(tx):
    """Canonical bytes for agreed unsigned transaction fields."""
    fields = {k: tx[k] for k in ("sender", "receiver", "amount", "nonce", "algorithm")}
    return json.dumps(fields, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def run_demo():
    signer = get_signer("ECDSA")
    alice_public, alice_private = signer.generate_keypair()
    bob_public, _ = signer.generate_keypair()
    tx = {"sender": "Alice", "receiver": "Bob", "amount": 30, "nonce": 1, "algorithm": "ECDSA"}
    signature = signer.sign(alice_private, transaction_bytes(tx))
    assert signer.verify(alice_public, transaction_bytes(tx), signature)
    changed = dict(tx, amount=300)
    assert not signer.verify(alice_public, transaction_bytes(changed), signature)
    assert not signer.verify(bob_public, transaction_bytes(tx), signature)
    print("ECDSA signed transaction: Alice -> Bob, 30 credits")
    print("Public key bytes:", len(alice_public))
    print("Signature bytes:", len(signature))
    print("Valid signature: True")
    print("Tampered amount rejected: True")
    print("Wrong public key rejected: True")
    print("NOTE: Wallet ownership, balance/nonce checks and blockchain persistence are NOT integrated yet.")

if __name__ == "__main__":
    run_demo()
