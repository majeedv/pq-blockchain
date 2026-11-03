# PQ Blockchain: ECDSA vs ML-DSA

Capstone project (Group 67). Compares ECDSA and ML-DSA in a simple blockchain wallet app.

## Folders
- crypto/     signing module, ECDSA + ML-DSA behind one interface (Majeed)
- chain/      blocks, hashing, SQLite, tamper check (Nikita)
- wallet/     wallets, transactions, validation rules (Naima)
- app/        clickable prototype and dashboard (Azraf)
- benchmark/  benchmarks and statistics (Orin)
- data/       results files
- tests/      tests

## Shared formats
Transaction: sender, receiver, amount, nonce, timestamp, algorithm, public_key, signature

Signer interface:
- generate_keypair() -> (public_key, private_key)
- sign(private_key, message) -> signature
- verify(public_key, message, signature) -> True/False

## Setup
python -m venv .venv
source .venv/bin/activate      (Windows: .venv\Scripts\activate)
pip install -r requirements.txt





## Blockchain backend methods

The blockchain backend provides block creation, SHA-256 hashing, chain validation, and SQLite storage.

- `Block.to_dict()` — returns a block as a dictionary.
- `calculate_block_hash(block_data)` — calculates the block's SHA-256 hash.
- `Blockchain.create_genesis_block()` — creates the first block.
- `Blockchain.get_latest_block()` — returns the latest block.
- `Blockchain.add_block(transactions)` — adds a hash-linked block.
- `Blockchain.is_chain_valid()` — checks block hashes and previous-hash links.
- `BlockchainStorage.save_block(block)` — saves a block and its transactions.
- `BlockchainStorage.save_chain(chain)` — saves a chain.
- `BlockchainStorage.load_chain()` — loads the saved chain.
- `BlockchainStorage.get_database_size_bytes()` — returns SQLite file size in bytes.
- `BlockchainStorage.get_database_size_kb()` — returns SQLite file size in KB.
