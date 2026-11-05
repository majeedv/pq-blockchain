
import unittest

from crypto.signer import get_signer


class TestECDSA(unittest.TestCase):

    def setUp(self):
        self.signer = get_signer("ECDSA")
        self.public, self.private = self.signer.generate_keypair()

    def test_valid_signature(self):
        message = b"Hello blockchain"
        signature = self.signer.sign(self.private, message)

        self.assertTrue(
            self.signer.verify(self.public, message, signature)
        )

    def test_tampered_transaction(self):
        message = b"Alice pays Bob 5"
        signature = self.signer.sign(self.private, message)

        self.assertFalse(
            self.signer.verify(
                self.public,
                b"Alice pays Bob 500",
                signature
            )
        )

    def test_wrong_public_key(self):
        message = b"Test message"
        signature = self.signer.sign(self.private, message)

        other_public, _ = self.signer.generate_keypair()

        self.assertFalse(
            self.signer.verify(other_public, message, signature)
        )


class TestMLDSA(unittest.TestCase):

    def setUp(self):
        try:
            self.signer = get_signer("ML-DSA-44")
        except (RuntimeError, ImportError) as error:
            self.skipTest(str(error))

        self.public, self.private = self.signer.generate_keypair()

    def test_valid_signature(self):
        message = b"Hello blockchain"
        signature = self.signer.sign(self.private, message)

        self.assertTrue(
            self.signer.verify(self.public, message, signature)
        )

    def test_tampered_transaction(self):
        message = b"Alice pays Bob 5"
        signature = self.signer.sign(self.private, message)

        self.assertFalse(
            self.signer.verify(
                self.public,
                b"Alice pays Bob 500",
                signature
            )
        )


if __name__ == "__main__":
    unittest.main()
