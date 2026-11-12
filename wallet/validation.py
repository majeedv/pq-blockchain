from crypto.signer import get_signer


def validate_transaction(sender, receiver, transaction):

    # Check that the sender and receiver match the wallets
    if transaction.sender != sender.wallet_id:
        return False, "Sender identity does not match."

    if transaction.receiver != receiver.wallet_id:
        return False, "Receiver identity does not match."

    # Check that the amount is a positive integer
    if isinstance(transaction.amount, bool) or not isinstance(transaction.amount, int):
        return False, "Transaction amount must be a whole number."

    if transaction.amount <= 0:
        return False, "Transaction amount must be greater than zero."

    # Check that the sender has enough balance
    if transaction.amount > sender.balance:
        return False, "Insufficient balance."

    # Check that the nonce is correct
    expected_nonce = sender.nonce + 1

    if transaction.nonce != expected_nonce:
        return False, "Invalid or repeated nonce."

    # Check that the algorithm is supported
    try:
        signer = get_signer(transaction.algorithm)
    except (ValueError, RuntimeError):
        return False, "Unsupported signature algorithm."

    # Check that the public key belongs to the sender
    try:
        public_key = bytes.fromhex(transaction.public_key)
        signature = bytes.fromhex(transaction.signature)

        registered_key = sender.keys[transaction.algorithm]["public_key"]

        if public_key != registered_key:
            return False, "Public key does not belong to the sender."

    except (ValueError, TypeError, KeyError):
        return False, "Invalid public key or signature format."

    # Verify the transaction signature
    if not signer.verify(public_key, transaction.serialize(), signature):
        return False, "Signature verification failed."

    return True, "Transaction is valid."


def process_transaction(sender, receiver, transaction):

    is_valid, message = validate_transaction(
        sender, receiver, transaction
    )

    if not is_valid:
        return False, message

    # Transfer the amount
    sender.balance -= transaction.amount
    receiver.balance += transaction.amount

    # Update the sender's nonce
    sender.nonce = transaction.nonce

    return True, "Transaction successful."