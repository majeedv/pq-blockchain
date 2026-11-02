"""
backend.py  (Azraf: frontend)

This file is the ONLY place where the screens talk to the "real system".
Right now every function uses FAKE signing so the interface works on its own.
Later, replace the fake parts with calls to your teammates' modules:

    crypto/    (Majeed)  -> generate_keypair(), sign(), verify()
    chain/     (Nikita)  -> blocks, hashing, SQLite
    wallet/    (Naima)   -> wallets, validation rules

The screens in main.py never change, because they only call the functions below.
"""

import hashlib
import json
import os
import time

ALGORITHMS = ["ECDSA", "ML-DSA-44"]

# Reference byte sizes from the proposal (slide 3).
# ECDSA secp256k1: compressed public key 33 B, signature about 71 B.
# ML-DSA-44 (FIPS 204): public key 1,312 B, signature 2,420 B.
SIZES = {
    "ECDSA": {"public_key": 33, "signature": 71},
    "ML-DSA-44": {"public_key": 1312, "signature": 2420},
}


# ---------------------------------------------------------------- helpers
def _sha256(obj) -> str:
    """Real SHA-256 of any JSON-friendly object (used for block hashes)."""
    data = json.dumps(obj, sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()


def _fake_signature(message: str, size: int) -> str:
    """FAKE signature of the right length. Replace with crypto.sign()."""
    digest = hashlib.sha256(message.encode()).hexdigest()
    return (digest * (size * 2 // len(digest) + 1))[: size * 2]


def _block_hash(block: dict) -> str:
    body = {k: block[k] for k in ("index", "timestamp", "transactions", "previous_hash")}
    return _sha256(body)


def _make_block(index: int, previous_hash: str, transactions: list) -> dict:
    block = {
        "index": index,
        "timestamp": time.time(),
        "transactions": transactions,
        "previous_hash": previous_hash,
    }
    block["hash"] = _block_hash(block)
    return block


# ------------------------------------------------------------------ state
def new_state() -> dict:
    """A fresh, empty system: no wallets, and a chain with only the first block."""
    return {
        "wallets": {},
        "nonces": {},       # last nonce used by each sender
        "rejected": 0,
        "chain": [_make_block(0, "0" * 64, [])],
    }


# ----------------------------------------------------------------- wallets
def create_wallet(state: dict, name: str, balance: int = 1000) -> dict:
    """TODO (Naima + Majeed): use crypto.generate_keypair() for both algorithms."""
    name = name.strip()
    if not name:
        return {"ok": False, "message": "Please enter a name."}
    if name in state["wallets"]:
        return {"ok": False, "message": f"A wallet called {name} already exists."}

    # Each wallet holds one key pair per algorithm, so the user can choose
    # the algorithm for every transaction (as the proposal describes).
    public_keys = {a: os.urandom(SIZES[a]["public_key"]).hex() for a in ALGORITHMS}
    state["wallets"][name] = {"name": name, "balance": balance, "public_keys": public_keys}
    state["nonces"][name] = 0
    return {"ok": True, "message": f"Wallet {name} created with {balance} credits."}


def create_sample_wallets(state: dict) -> None:
    for name in ("Alice", "Bob", "Charlie"):
        if name not in state["wallets"]:
            create_wallet(state, name)


# ------------------------------------------------------------ transactions
def send_transaction(state: dict, sender: str, receiver: str, amount: float, algorithm: str) -> dict:
    """
    Runs the whole path: create -> sign -> validate -> add to chain.
    TODO: swap in crypto.sign(), crypto.verify(), wallet validation and chain.add_block().
    """
    def reject(reason: str) -> dict:
        state["rejected"] += 1
        return {"ok": False, "message": reason}

    wallets = state["wallets"]
    if sender not in wallets or receiver not in wallets:
        return reject("Unknown sender or receiver.")
    if sender == receiver:
        return reject("Sender and receiver must be different.")
    if not amount or amount <= 0:
        return reject("Amount must be greater than zero.")
    if wallets[sender]["balance"] < amount:
        return reject("Insufficient balance.")

    nonce = state["nonces"][sender] + 1
    tx = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "nonce": nonce,
        "timestamp": time.time(),
        "algorithm": algorithm,
        "public_key": wallets[sender]["public_keys"][algorithm],
    }
    message = json.dumps(tx, sort_keys=True)

    t0 = time.perf_counter()
    tx["signature"] = _fake_signature(message, SIZES[algorithm]["signature"])
    sign_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    signature_ok = len(tx["signature"]) == SIZES[algorithm]["signature"] * 2   # fake check
    verify_ms = (time.perf_counter() - t0) * 1000
    if not signature_ok:
        return reject("Signature verification failed.")

    # Commit: add block, update balances, remember the nonce.
    previous = state["chain"][-1]
    block = _make_block(previous["index"] + 1, previous["hash"], [tx])
    state["chain"].append(block)
    wallets[sender]["balance"] -= amount
    wallets[receiver]["balance"] += amount
    state["nonces"][sender] = nonce

    return {
        "ok": True,
        "message": f"Transaction accepted and added to block #{block['index']}.",
        "transaction": tx,
        "block": block,
        "sign_ms": sign_ms,
        "verify_ms": verify_ms,
        "signature_bytes": SIZES[algorithm]["signature"],
        "public_key_bytes": SIZES[algorithm]["public_key"],
    }


# ------------------------------------------------------------------- chain
def get_chain(state: dict) -> list:
    return state["chain"]


def verify_chain(state: dict) -> list:
    """Returns a list of problems found. Empty list means the chain is intact."""
    problems = []
    chain = state["chain"]
    for i, block in enumerate(chain):
        if _block_hash(block) != block["hash"]:
            problems.append(f"Block #{block['index']}: contents were changed.")
        if i > 0 and block["previous_hash"] != chain[i - 1]["hash"]:
            problems.append(f"Block #{block['index']}: link to the previous block is broken.")
    return problems


# ------------------------------------------------------------- performance
def get_benchmark_results() -> list:
    """
    FAKE placeholder numbers so the dashboard layout can be built.
    TODO (Capstone 2): read Orin's results CSV from data/ instead.
    Expected columns follow the architecture diagram:
    algorithm, operation, median_ms, public_key_bytes, signature_bytes.
    """
    fake_ms = {
        ("ECDSA", "Key generation"): 0.04,
        ("ECDSA", "Signing"): 0.06,
        ("ECDSA", "Verification"): 0.15,
        ("ML-DSA-44", "Key generation"): 0.10,
        ("ML-DSA-44", "Signing"): 0.35,
        ("ML-DSA-44", "Verification"): 0.12,
    }
    return [
        {
            "algorithm": a,
            "operation": op,
            "median_ms": ms,
            "public_key_bytes": SIZES[a]["public_key"],
            "signature_bytes": SIZES[a]["signature"],
        }
        for (a, op), ms in fake_ms.items()
    ]
