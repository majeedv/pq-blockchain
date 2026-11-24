import unittest
from crypto.signer import get_signer
from crypto.ecdsa_transaction_demo import transaction_bytes

class TestECDSATransaction(unittest.TestCase):
    def setUp(self):
        self.signer = get_signer("ECDSA")
        self.pub, self.priv = self.signer.generate_keypair()
        self.tx = {"sender": "Alice", "receiver": "Bob", "amount": 30, "nonce": 1, "algorithm": "ECDSA"}
        self.sig = self.signer.sign(self.priv, transaction_bytes(self.tx))

    def test_valid(self):
        self.assertTrue(self.signer.verify(self.pub, transaction_bytes(self.tx), self.sig))

    def test_tampered_amount(self):
        self.assertFalse(self.signer.verify(self.pub, transaction_bytes(dict(self.tx, amount=300)), self.sig))

    def test_wrong_public_key(self):
        other, _ = self.signer.generate_keypair()
        self.assertFalse(self.signer.verify(other, transaction_bytes(self.tx), self.sig))

    def test_tampered_nonce(self):
        self.assertFalse(self.signer.verify(self.pub, transaction_bytes(dict(self.tx, nonce=2)), self.sig))

    def test_deterministic_serialization(self):
        reversed_tx = dict(reversed(list(self.tx.items())))
        self.assertEqual(transaction_bytes(self.tx), transaction_bytes(reversed_tx))
