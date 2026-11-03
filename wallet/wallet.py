class Wallet:
    def __init__(self, wallet_id, balance=0):
        self.wallet_id = wallet_id
        self.balance = balance
        self.nonce = 0