import json


class Transaction:
    def __init__(
        self,
        sender,
        receiver,
        amount,
        nonce,
        timestamp,
        algorithm,
        public_key,
        signature
    ):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.nonce = nonce
        self.timestamp = timestamp
        self.algorithm = algorithm
        self.public_key = public_key
        self.signature = signature

    def to_dict(self):
        """Return the transaction fields that must be signed."""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "algorithm": self.algorithm,
        }

    def serialize(self):
        """Return a canonical JSON representation as UTF-8 bytes."""
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False
        ).encode("utf-8")