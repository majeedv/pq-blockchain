from wallet.wallet import Wallet
from wallet.transaction import Transaction
from wallet.validation import process_transaction


def create_transaction(sender, receiver, amount, nonce):
    return Transaction(
        sender=sender.wallet_id,
        receiver=receiver.wallet_id,
        amount=amount,
        nonce=nonce,
        timestamp="2026-11-03",
        algorithm="ECDSA",
        public_key="abcd1234",
        signature="ef567890"
    )


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