
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from .block import Block


class BlockchainStorage:

    def __init__(self, db_path=None):

        if db_path is None:
            project_folder = Path(__file__).resolve().parent.parent
            db_path = project_folder / "data" / "blockchain.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.initialize_database()

    def initialize_database(self):
        """Create the blocks and transactions tables."""

        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute("PRAGMA foreign_keys = ON")

                connection.execute("""
                    CREATE TABLE IF NOT EXISTS blocks (
                        block_index INTEGER PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        previous_hash TEXT NOT NULL,
                        hash TEXT NOT NULL
                    )
                """)

                connection.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        block_index INTEGER NOT NULL,
                        position INTEGER NOT NULL,
                        transaction_data TEXT NOT NULL,

                        FOREIGN KEY (block_index)
                            REFERENCES blocks(block_index)
                            ON DELETE CASCADE,

                        UNIQUE (block_index, position)
                    )
                """)

    def save_block(self, block):
        """Save one block and its transactions."""

        with closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute("PRAGMA foreign_keys = ON")

                connection.execute("""
                    INSERT INTO blocks (
                        block_index, timestamp, previous_hash, hash
                    )
                    VALUES (?, ?, ?, ?)

                    ON CONFLICT(block_index) DO UPDATE SET
                        timestamp = excluded.timestamp,
                        previous_hash = excluded.previous_hash,
                        hash = excluded.hash
                """, (
                    block.index,
                    block.timestamp,
                    block.previous_hash,
                    block.hash
                ))

                connection.execute("""
                    DELETE FROM transactions
                    WHERE block_index = ?
                """, (block.index,))

                for position, transaction in enumerate(block.transactions):

                    transaction_json = json.dumps(
                        transaction,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False
                    )

                    connection.execute("""
                        INSERT INTO transactions (
                            block_index, position, transaction_data
                        )
                        VALUES (?, ?, ?)
                    """, (
                        block.index,
                        position,
                        transaction_json
                    ))

    def save_chain(self, chain):
        """Save all blocks in the blockchain."""

        for block in chain:
            self.save_block(block)

    def load_chain(self):
        """Load all blocks and transactions from SQLite."""

        loaded_chain = []

        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("PRAGMA foreign_keys = ON")

            blocks = connection.execute("""
                SELECT block_index, timestamp, previous_hash, hash
                FROM blocks
                ORDER BY block_index ASC
            """).fetchall()

            for block_row in blocks:

                block_index = block_row[0]

                transaction_rows = connection.execute("""
                    SELECT transaction_data
                    FROM transactions
                    WHERE block_index = ?
                    ORDER BY position ASC
                """, (block_index,)).fetchall()

                transactions = [
                    json.loads(row[0])
                    for row in transaction_rows
                ]

                block = Block(
                    index=block_row[0],
                    timestamp=block_row[1],
                    transactions=transactions,
                    previous_hash=block_row[2],
                    hash=block_row[3]
                )

                loaded_chain.append(block)

        return loaded_chain

    def get_database_size_bytes(self):
        """Return database file size in bytes."""

        if not self.db_path.exists():
            return 0

        return self.db_path.stat().st_size

    def get_database_size_kb(self):
        """Return database file size in kilobytes."""

        return self.get_database_size_bytes() / 1024
