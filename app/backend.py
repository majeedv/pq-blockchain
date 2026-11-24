"""
backend.py  (Azraf: frontend)

The screens (main.py) talk to the rest of the system only through this file.

Connected modules:
    wallet/     (Naima)   Wallet, Transaction and the validation rules
    crypto/     (Majeed)  get_signer(): generate_keypair(), sign(), verify()
    chain/      (Nikita)  Blockchain and BlockchainStorage (SQLite)
    data/       (Orin)    benchmark_results.csv for the Performance page

If a module cannot be loaded (for example the ML-DSA library is not installed),
that part falls back to a placeholder and the result message says so.
"""

import csv
import hashlib
import json
import os
import statistics
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Make the repository root importable, so we can use the wallet, crypto and chain folders.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from wallet.wallet import Wallet                                  # Naima
from wallet.transaction import Transaction                        # Naima
from wallet.validation import process_transaction                 # Naima
from chain.blockchain import Blockchain                           # Nikita
from chain.storage import BlockchainStorage                       # Nikita
from chain.hashing import calculate_block_hash                    # Nikita

try:
    from crypto.signer import get_signer                          # Majeed
except Exception as error:                                        # e.g. liboqs missing
    get_signer = None
    _SIGNER_IMPORT_ERROR = str(error)
else:
    _SIGNER_IMPORT_ERROR = ""

ALGORITHMS = ["ECDSA", "ML-DSA-44"]

# Reference sizes from the proposal. Only used if the real signer is unavailable.
SIZES = {
    "ECDSA": {"public_key": 33, "signature": 71},
    "ML-DSA-44": {"public_key": 1312, "signature": 2420},
}

BENCHMARK_FILE = ROOT / "data" / "benchmark_results.csv"

_signer_cache = {}


# ---------------------------------------------------------------- signing
def _get_signer(algorithm: str):
    """Return Majeed's signer for this algorithm, or None if it cannot be loaded."""
    if algorithm in _signer_cache:
        return _signer_cache[algorithm]
    signer = None
    if get_signer is not None:
        try:
            signer = get_signer(algorithm)
        except Exception:
            signer = None
    _signer_cache[algorithm] = signer
    return signer


def signing_status() -> dict:
    """Which algorithms use the real signer? Useful for a quick check."""
    return {a: _get_signer(a) is not None for a in ALGORITHMS}


def _placeholder_signature(message: bytes, size: int) -> bytes:
    digest = hashlib.sha256(message).digest()
    return (digest * (size // len(digest) + 1))[:size]


# ---------------------------------------------------------------- helpers
def _block_to_dict(block) -> dict:
    """Nikita's Block -> a plain dict. The timestamp becomes a number for the screens."""
    data = block.to_dict()
    data["timestamp"] = datetime.fromisoformat(data["timestamp"]).timestamp()
    return data


def _sync(entry: dict) -> None:
    """Copy the balance from Naima's Wallet object so the screens always show the real one."""
    entry["balance"] = entry["obj"].balance


# ------------------------------------------------------------------ state
def new_state() -> dict:
    # Real SQLite storage, in a temporary file so every session starts clean.
    folder = tempfile.mkdtemp(prefix="pqchain_")
    storage = BlockchainStorage(Path(folder) / "blockchain.db")
    blockchain = Blockchain(storage=storage)
    return {
        "wallets": {},
        "rejected": 0,
        "blockchain": blockchain,
        "storage": storage,
        "chain": blockchain.chain,   # same list object, so len(state["chain"]) stays correct
    }


# ----------------------------------------------------------------- wallets
def create_wallet(state: dict, name: str, balance: int = 1000) -> dict:
    name = name.strip()
    if not name:
        return {"ok": False, "message": "Please enter a name."}
    if name in state["wallets"]:
        return {"ok": False, "message": f"A wallet called {name} already exists."}

    public_keys = {}
    private_keys = {}
    for algorithm in ALGORITHMS:
        signer = _get_signer(algorithm)
        if signer is not None:
            public_key, private_key = signer.generate_keypair()
        else:  # placeholder keys
            public_key = os.urandom(SIZES[algorithm]["public_key"])
            private_key = os.urandom(32)
        public_keys[algorithm] = public_key.hex()
        private_keys[algorithm] = private_key

    state["wallets"][name] = {
        "name": name,
        "balance": balance,
        "public_keys": public_keys,       # hex text, shown on screen
        "private_keys": private_keys,     # bytes, never shown
        "obj": Wallet(name, balance),     # Naima's wallet (balance and nonce live here)
    }
    return {"ok": True, "message": f"Wallet {name} created with {balance} credits."}


def create_sample_wallets(state: dict) -> None:
    for name in ("Alice", "Bob", "Charlie"):
        if name not in state["wallets"]:
            create_wallet(state, name)


# ------------------------------------------------------------ transactions
def send_transaction(state: dict, sender: str, receiver: str, amount: float, algorithm: str) -> dict:
    def reject(reason: str) -> dict:
        state["rejected"] += 1
        return {"ok": False, "message": reason}

    wallets = state["wallets"]
    if sender not in wallets or receiver not in wallets:
        return reject("Unknown sender or receiver.")
    if sender == receiver:
        return reject("Sender and receiver must be different.")

    sender_entry = wallets[sender]
    receiver_entry = wallets[receiver]
    sender_wallet = sender_entry["obj"]
    receiver_wallet = receiver_entry["obj"]

    # Naima's Transaction object. The nonce is the sender's next number.
    tx_obj = Transaction(
        sender=sender,
        receiver=receiver,
        amount=amount,
        nonce=sender_wallet.nonce + 1,
        timestamp=time.time(),
        algorithm=algorithm,
        public_key=sender_entry["public_keys"][algorithm],
        signature=None,
    )

    # The signed message: every field except the signature itself.
    message = json.dumps(
        {k: v for k, v in vars(tx_obj).items() if k != "signature"}, sort_keys=True
    ).encode("utf-8")

    public_key = bytes.fromhex(sender_entry["public_keys"][algorithm])
    private_key = sender_entry["private_keys"][algorithm]
    signer = _get_signer(algorithm)

    # Majeed's signing and verification, timed.
    t0 = time.perf_counter()
    if signer is not None:
        signature = signer.sign(private_key, message)
    else:
        signature = _placeholder_signature(message, SIZES[algorithm]["signature"])
    sign_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    if signer is not None:
        signature_ok = bool(signer.verify(public_key, message, signature))
    else:
        signature_ok = len(signature) == SIZES[algorithm]["signature"]
    verify_ms = (time.perf_counter() - t0) * 1000

    if not signature_ok:
        return reject("Signature verification failed.")
    tx_obj.signature = signature.hex()

    # Naima's rules: amount, balance and nonce. On success she also moves the credits.
    ok, reason = process_transaction(sender_wallet, receiver_wallet, tx_obj)
    if not ok:
        return reject(reason)

    _sync(sender_entry)
    _sync(receiver_entry)

    # Nikita's chain: add a block and save it to SQLite.
    tx = dict(vars(tx_obj))
    block = state["blockchain"].add_block([tx])

    note = "" if signer is not None else f" (placeholder signature: real {algorithm} signer not available)"
    return {
        "ok": True,
        "message": f"Transaction accepted and added to block #{block.index}.{note}",
        "transaction": tx,
        "block": _block_to_dict(block),
        "sign_ms": sign_ms,
        "verify_ms": verify_ms,
        "signature_bytes": len(signature),
        "public_key_bytes": len(public_key),
    }


# ------------------------------------------------------------------- chain
def get_chain(state: dict) -> list:
    return [_block_to_dict(b) for b in state["blockchain"].chain]


def verify_chain(state: dict) -> list:
    """Returns a list of problems found. An empty list means the chain is intact."""
    problems = []
    chain = state["blockchain"].chain
    for i, block in enumerate(chain):
        if block.hash != calculate_block_hash(block.to_dict()):
            problems.append(f"Block #{block.index}: contents were changed.")
        if i > 0 and block.previous_hash != chain[i - 1].hash:
            problems.append(f"Block #{block.index}: link to the previous block is broken.")
    if not problems and not state["blockchain"].is_chain_valid():
        problems.append("The chain failed Nikita's validation check.")
    return problems


def storage_size_bytes(state: dict) -> int:
    """Size of the SQLite file, in bytes (one of the project's measurements)."""
    return state["storage"].get_database_size_bytes()


# ------------------------------------------------------------- performance
_OPERATION_LABELS = {
    "keygen": "Key generation",
    "signing": "Signing",
    "verification": "Verification",
}


def get_benchmark_results() -> list:
    """Median time per operation and key and signature sizes, from Orin's results CSV."""
    if not BENCHMARK_FILE.exists():
        return []

    times = {}
    sizes = {}
    with open(BENCHMARK_FILE, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            key = (row["algorithm"], row["operation"])
            times.setdefault(key, []).append(float(row["time_ns"]))
            sizes[row["algorithm"]] = (int(row["pub_key_bytes"]), int(row["sig_bytes"]))

    results = []
    for (algorithm, operation), values in times.items():
        results.append(
            {
                "algorithm": algorithm,
                "operation": _OPERATION_LABELS.get(operation, operation),
                "median_ms": statistics.median(values) / 1_000_000,   # ns -> ms
                "public_key_bytes": sizes[algorithm][0],
                "signature_bytes": sizes[algorithm][1],
            }
        )
    return results