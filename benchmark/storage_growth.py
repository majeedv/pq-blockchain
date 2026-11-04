import csv
import platform
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from chain.blockchain import Blockchain
from chain.storage import BlockchainStorage


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
RESULTS_FILE = PROJECT_FOLDER / "data" / "storage_growth_results.csv"

TEST_SIZES = [100, 500, 1000, 5000]
TRANSACTIONS_PER_BLOCK = 10
ALGORITHMS = ["ECDSA", "ML-DSA-44"]


def create_sample_transactions(number, algorithm):
    """Create placeholder transactions for storage testing."""
    return [
        {
            "sender": f"Sender_{i}",
            "receiver": f"Receiver_{i}",
            "amount": 5,
            "nonce": 1,
            "timestamp": "storage-test",
            "algorithm": algorithm,
            "public_key": "sample-public-key",
            "signature": "sample-signature",
        }
        for i in range(number)
    ]


def run_storage_test(number_of_transactions, algorithm):
    """Measure SQLite file size for a fresh chain and validate it."""
    blockchain = Blockchain()
    transactions = create_sample_transactions(
        number_of_transactions, algorithm
    )

    for start in range(
        0, number_of_transactions, TRANSACTIONS_PER_BLOCK
    ):
        batch = transactions[start:start + TRANSACTIONS_PER_BLOCK]
        blockchain.add_block(batch)

    with tempfile.TemporaryDirectory() as temp_folder:
        database_path = Path(temp_folder) / "blockchain.db"
        storage = BlockchainStorage(database_path)
        storage.save_chain(blockchain.chain)

        loaded_chain = storage.load_chain()

        restored_blockchain = Blockchain()
        restored_blockchain.chain = loaded_chain

        is_valid = restored_blockchain.is_chain_valid()
        if not is_valid:
            raise RuntimeError(
                "Blockchain validation failed during storage test."
            )

        size_bytes = storage.get_database_size_bytes()

        return {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "algorithm": algorithm,
            "transaction_count": number_of_transactions,
            "block_count": len(loaded_chain),
            "database_size_bytes": size_bytes,
            "database_size_kb": round(size_bytes / 1024, 3),
            "python_version": platform.python_version(),
            "operating_system": platform.platform(),
            "processor": platform.processor(),
            "chain_valid": is_valid,
        }


def main():
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    results = []

    for algorithm in ALGORITHMS:
        for size in TEST_SIZES:
            result = run_storage_test(size, algorithm)
            results.append(result)

            print(
                f"{algorithm}: {size} transactions -> "
                f"{result['database_size_bytes']} bytes; "
                f"valid={result['chain_valid']}"
            )

    fieldnames = list(results[0].keys())

    with RESULTS_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()