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