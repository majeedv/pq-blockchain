from crypto.signer import get_signer


class Wallet:
    def __init__(self, wallet_id, balance=0):
        self.wallet_id = wallet_id
        self.balance = balance
        self.nonce = 0

        # Generate ECDSA keys for this wallet
        signer = get_signer("ECDSA")
        public_key, private_key = signer.generate_keypair()

        self.keys = {
            "ECDSA": {
                "public_key": public_key,
                "private_key": private_key
            }
        }

    def sign_transaction(self, transaction):
        """Sign a transaction using this wallet's private key."""

        if transaction.sender != self.wallet_id:
            raise ValueError("Cannot sign a transaction for another wallet.")

        if transaction.algorithm != "ECDSA":
            raise ValueError("This wallet currently supports ECDSA only.")

        signer = get_signer("ECDSA")
        keys = self.keys["ECDSA"]

        # Sign the canonical transaction data
        signature = signer.sign(
            keys["private_key"],
            transaction.serialize()
        )

        # Attach the public key and signature
        transaction.public_key = keys["public_key"].hex()
        transaction.signature = signature.hex()

        return transaction
