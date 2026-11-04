
from datetime import datetime, timezone

from .block import Block
from .hashing import calculate_block_hash


class Blockchain:

    def __init__(self, storage=None):
        """
        Create a blockchain.

        If a storage object is supplied, load the saved chain.
        Otherwise, create an in-memory blockchain.
        """

        self.chain = []
        self.storage = storage

        # Try to restore previously saved blocks.
        if self.storage is not None:
            saved_chain = self.storage.load_chain()

            if saved_chain:
                self.chain = saved_chain

                # Never continue using a corrupted saved chain.
                if not self.is_chain_valid():
                    self.chain = []
                    raise ValueError(
                        "The saved blockchain is invalid. "
                        "The database may have been tampered with."
                    )

                return

        # Create the Genesis Block if no saved chain exists.
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create and optionally save the first block."""

        genesis = Block(
            index=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            transactions=[],
            previous_hash="0"
        )

        genesis.hash = calculate_block_hash(genesis.to_dict())

        # Save before adding it to the in-memory chain.
        if self.storage is not None:
            self.storage.save_block(genesis)

        self.chain.append(genesis)

    def get_latest_block(self):
        """Return the most recent block."""

        return self.chain[-1]

    def add_block(self, transactions):
        """Create a block, link it and optionally save it."""

        previous_block = self.get_latest_block()

        new_block = Block(
            index=previous_block.index + 1,
            timestamp=datetime.now(timezone.utc).isoformat(),
            transactions=transactions,
            previous_hash=previous_block.hash
        )

        new_block.hash = calculate_block_hash(new_block.to_dict())

        # Save the new block before updating the in-memory chain.
        if self.storage is not None:
            self.storage.save_block(new_block)

        self.chain.append(new_block)

        return new_block

    def is_chain_valid(self):
        """
        Check every block's hash and previous-hash connection.
        Return True if the chain is valid, otherwise False.
        """

        if not self.chain:
            return False

        # Check the Genesis Block.
        genesis = self.chain[0]

        if genesis.index != 0 or genesis.previous_hash != "0":
            return False

        if genesis.hash != calculate_block_hash(genesis.to_dict()):
            return False

        # Check all following blocks.
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check the block's own hash.
            recalculated_hash = calculate_block_hash(
                current_block.to_dict()
            )

            if current_block.hash != recalculated_hash:
                return False

            # Check the connection to the previous block.
            if current_block.previous_hash != previous_block.hash:
                return False

            # Check the block sequence.
            if current_block.index != previous_block.index + 1:
                return False

        return True
