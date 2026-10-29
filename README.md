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
