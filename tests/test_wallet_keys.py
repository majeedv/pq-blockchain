from wallet.wallet import Wallet
from crypto.signer import get_signer


def test_wallet_generates_both_keypairs():
    wallet = Wallet("Alice", 100)

    assert "ECDSA" in wallet.keys
    assert "ML-DSA-44" in wallet.keys


def test_wallet_keys_are_bytes():
    wallet = Wallet("Alice", 100)

    for algorithm in wallet.keys:
        assert isinstance(wallet.keys[algorithm]["public_key"], bytes)
        assert isinstance(wallet.keys[algorithm]["private_key"], bytes)


def test_wallet_keypairs_can_sign_and_verify():
    wallet = Wallet("Alice", 100)
    message = b"Wallet ownership test"

    for algorithm, keys in wallet.keys.items():
        signer = get_signer(algorithm)

        signature = signer.sign(keys["private_key"], message)

        assert signer.verify(
            keys["public_key"],
            message,
            signature
        )


def test_wallets_have_different_public_keys():
    alice = Wallet("Alice", 100)
    bob = Wallet("Bob", 100)

    for algorithm in alice.keys:
        assert (
            alice.keys[algorithm]["public_key"]
            != bob.keys[algorithm]["public_key"]
        )