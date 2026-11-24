from wallet.wallet import Wallet
from wallet.transaction import Transaction
from wallet.validation import process_transaction


def create_transaction(sender, receiver, amount, nonce):
    transaction = Transaction(
        sender=sender.wallet_id,
        receiver=receiver.wallet_id,
        amount=amount,
        nonce=nonce,
        timestamp="2026-11-24",
        algorithm="ECDSA",
        public_key="",
        signature=""
    )

    return sender.sign_transaction(transaction)


def test_overspending():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 50)

    transaction = create_transaction(alice, bob, 150, 1)

    success, message = process_transaction(alice, bob, transaction)

    assert success is False
    assert alice.balance == 100
    assert bob.balance == 50


def test_repeated_nonce():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 50)

    first = create_transaction(alice, bob, 20, 1)
    process_transaction(alice, bob, first)

    second = create_transaction(alice, bob, 10, 1)
    success, message = process_transaction(alice, bob, second)

    assert success is False
    assert alice.nonce == 1
    assert alice.balance == 80
    assert bob.balance == 70


def test_zero_amount():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 50)

    transaction = create_transaction(alice, bob, 0, 1)

    success, message = process_transaction(alice, bob, transaction)

    assert success is False
    assert alice.balance == 100
    assert bob.balance == 50


def test_valid_transaction():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 50)

    transaction = create_transaction(alice, bob, 30, 1)

    success, message = process_transaction(alice, bob, transaction)

    assert success is True
    assert alice.balance == 70
    assert bob.balance == 80
    assert alice.nonce == 1

def test_tampered_transaction_is_rejected():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 50)

    transaction = create_transaction(alice, bob, 30, 1)

    # Change the amount after signing
    transaction.amount = 60

    success, message = process_transaction(alice, bob, transaction)

    assert success is False
    assert message == "Signature verification failed."
    assert alice.balance == 100
    assert bob.balance == 50
    assert alice.nonce == 0


def test_wrong_public_key_is_rejected():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 50)

    transaction = create_transaction(alice, bob, 30, 1)

    # Replace Alice's public key with Bob's public key
    transaction.public_key = bob.keys["ECDSA"]["public_key"].hex()

    success, message = process_transaction(alice, bob, transaction)

    assert success is False
    assert message == "Public key does not belong to the sender."
    assert alice.balance == 100
    assert bob.balance == 50
    assert alice.nonce == 0


def test_replay_attack_is_rejected():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 50)

    # Create and sign one transaction
    transaction = create_transaction(alice, bob, 30, 1)

    # First submission should succeed
    first_success, _ = process_transaction(alice, bob, transaction)

    # Submit the exact same signed transaction again
    second_success, message = process_transaction(alice, bob, transaction)

    assert first_success is True
    assert second_success is False
    assert message == "Invalid or repeated nonce."

    # Ensure balances were changed only once
    assert alice.balance == 70
    assert bob.balance == 80
    assert alice.nonce == 1