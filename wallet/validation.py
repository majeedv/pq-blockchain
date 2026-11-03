def validate_transaction(sender, receiver, transaction):
    # Check that the amount is positive
    if transaction.amount <= 0:
        return False, "Transaction amount must be greater than zero."

    # Check that the sender has enough balance
    if transaction.amount > sender.balance:
        return False, "Insufficient balance."

    # Check that the nonce is correct
    expected_nonce = sender.nonce + 1

    if transaction.nonce != expected_nonce:
        return False, "Invalid or repeated nonce."

    # All checks passed
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

 # only for testing purpose
 