from wallet.transaction import Transaction


def create_transaction(amount=25):
    return Transaction(
        sender="Alice",
        receiver="Bob",
        amount=amount,
        nonce=1,
        timestamp="2026-11-12",
        algorithm="ECDSA",
        public_key="abcd",
        signature="efgh"
    )


def test_transaction_serialization_returns_bytes():
    transaction = create_transaction()

    assert isinstance(transaction.serialize(), bytes)


def test_transaction_serialization_is_consistent():
    first = create_transaction()
    second = create_transaction()

    assert first.serialize() == second.serialize()


def test_modified_amount_changes_serialized_message():
    original = create_transaction(25)
    modified = create_transaction(250)

    assert original.serialize() != modified.serialize()


def test_signature_and_public_key_are_not_serialized():
    transaction = create_transaction()

    serialized = transaction.serialize()

    assert b"abcd" not in serialized
    assert b"efgh" not in serialized