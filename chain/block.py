
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Block:
    index: int
    timestamp: str
    transactions: list[dict[str, Any]] = field(default_factory=list)
    previous_hash: str = "0"
    hash: str = ""

    def to_dict(self) -> dict:
        """Convert the block into a dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }
