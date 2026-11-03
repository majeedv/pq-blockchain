
import tempfile
import unittest
from pathlib import Path

from chain.blockchain import Blockchain
from chain.storage import BlockchainStorage


class TestBlockchainStorage(unittest.TestCase):

    def setUp(self):
        self.temp_folder = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temp_folder.name) / "test_blockchain.db"
        )

        self.storage = BlockchainStorage(self.database_path)

        # This blockchain uses memory only.
        self.blockchain = Blockchain()

        self.blockchain.add_block([
            {"from": "A", "to": "B", "amount": 5}
        ])

        self.blockchain.add_block([
            {"from": "B", "to": "C", "amount": 3}
        ])

    def tearDown(self):
        self.temp_folder.cleanup()

    def test_save_and_load_chain(self):
        self.storage.save_chain(self.blockchain.chain)

        loaded_chain = self.storage.load_chain()

        self.assertEqual(len(loaded_chain), 3)

        self.assertEqual(
            loaded_chain[1].transactions[0]["amount"],
            5
        )

        self.assertEqual(
            loaded_chain[2].transactions[0]["to"],
            "C"
        )

        restored_blockchain = Blockchain()
        restored_blockchain.chain = loaded_chain

        self.assertTrue(restored_blockchain.is_chain_valid())

    def test_database_size(self):
        self.storage.save_chain(self.blockchain.chain)

        size = self.storage.get_database_size_bytes()

        self.assertGreater(size, 0)

        size_kb = self.storage.get_database_size_kb()

        self.assertGreater(size_kb, 0)

    def test_loaded_chain_detects_tampering(self):
        self.storage.save_chain(self.blockchain.chain)

        loaded_chain = self.storage.load_chain()

        loaded_chain[1].transactions[0]["amount"] = 999

        restored_blockchain = Blockchain()
        restored_blockchain.chain = loaded_chain

        self.assertFalse(restored_blockchain.is_chain_valid())

    def test_automatic_saving_and_reloading(self):
        # Start a persistent blockchain.
        first_blockchain = Blockchain(
            storage=BlockchainStorage(self.database_path)
        )

        # The Genesis Block should be created and saved automatically.
        self.assertEqual(len(first_blockchain.chain), 1)

        # Add a transaction. Its block should be saved automatically.
        first_blockchain.add_block([
            {"from": "A", "to": "B", "amount": 10}
        ])

        self.assertEqual(len(first_blockchain.chain), 2)

        # Create another blockchain using the same database.
        # It should restore the two saved blocks.
        second_blockchain = Blockchain(
            storage=BlockchainStorage(self.database_path)
        )

        self.assertEqual(len(second_blockchain.chain), 2)

        self.assertEqual(
            second_blockchain.chain[1].transactions[0]["amount"],
            10
        )

        self.assertTrue(second_blockchain.is_chain_valid())

    def test_empty_database_creates_genesis_block(self):
        persistent_blockchain = Blockchain(
            storage=BlockchainStorage(self.database_path)
        )

        self.assertEqual(len(persistent_blockchain.chain), 1)
        self.assertEqual(persistent_blockchain.chain[0].index, 0)

        # Confirm the Genesis Block was saved.
        loaded_chain = self.storage.load_chain()

        self.assertEqual(len(loaded_chain), 1)
        self.assertEqual(loaded_chain[0].index, 0)


if __name__ == "__main__":
    unittest.main()
