from crypto.signer import get_signer


class Wallet:
    def __init__(self, wallet_id, balance=0):
        self.wallet_id = wallet_id
        self.balance = balance
        self.nonce = 0

        self.keys = {}

        for algorithm in ("ECDSA", "ML-DSA-44"):
            signer = get_signer(algorithm)
            public_key, private_key = signer.generate_keypair()

            self.keys[algorithm] = {
                "public_key": public_key,
                "private_key": private_key
            }