
import hashlib
import json


def calculate_block_hash(block_data: dict) -> str:
    """
    Calculate a consistent SHA-256 hash for a block.

    The stored hash is excluded because a block's hash
    must be calculated from its contents, not itself.
    """

    block_contents = {
        "index": block_data["index"],
        "timestamp": block_data["timestamp"],
        "transactions": block_data["transactions"],
        "previous_hash": block_data["previous_hash"]
    }

    # Convert the block into consistent JSON.
    block_string = json.dumps(
        block_contents,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    # Generate SHA-256 hash.
    return hashlib.sha256(
        block_string.encode("utf-8")
    ).hexdigest()
