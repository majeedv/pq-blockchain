
import unittest

from chain.blockchain import Blockchain


class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.blockchain = Blockchain()

    def test_genesis_block(self):
        self.assertEqual(len(self.blockchain.chain), 1)
        self.assertEqual(self.blockchain.chain[0].index, 0)
        self.assertTrue(self.blockchain.is_chain_valid())

    def test_add_blocks(self):
        transaction1 = {
            "from": "A",
            "to": "B",
            "amount": 5
        }

        transaction2 = {
            "from": "B",
            "to": "C",
            "amount": 3
        }

        self.blockchain.add_block([transaction1])
        self.blockchain.add_block([transaction2])

        self.assertEqual(len(self.blockchain.chain), 3)
        self.assertEqual(self.blockchain.chain[1].index, 1)
        self.assertEqual(self.blockchain.chain[2].index, 2)

        self.assertEqual(
            self.blockchain.chain[1].previous_hash,
            self.blockchain.chain[0].hash
        )

        self.assertEqual(
            self.blockchain.chain[2].previous_hash,
            self.blockchain.chain[1].hash
        )

        self.assertTrue(self.blockchain.is_chain_valid())

    def test_tampering_detection(self):
        transaction = {
            "from": "A",
            "to": "B",
            "amount": 5
        }

        self.blockchain.add_block([transaction])
        self.blockchain.add_block([
            {"from": "B", "to": "C", "amount": 2}
        ])

        # Change an old transaction.
        self.blockchain.chain[1].transactions[0]["amount"] = 999

        # The blockchain should now detect tampering.
        self.assertFalse(self.blockchain.is_chain_valid())


    def test_transaction_fields_are_preserved(self):
        transaction = {
            "sender": "Alice",
            "receiver": "Bob",
            "amount": 5,
            "nonce": 1,
            "timestamp": "2026-11-04T00:00:00+00:00",
            "algorithm": "ECDSA",
            "public_key": "sample-public-key",
            "signature": "sample-signature",
        }

        self.blockchain.add_block([transaction])

        self.assertEqual(
            self.blockchain.chain[1].transactions[0],
            transaction
        )

        self.assertTrue(self.blockchain.is_chain_valid())

if __name__ == "__main__":
    unittest.main()
