
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


class ECDSASigner:
    name = "ECDSA"

    def generate_keypair(self):
        private_key = ec.generate_private_key(ec.SECP256K1())

        public = private_key.public_key().public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.CompressedPoint
        )

        private = private_key.private_numbers().private_value.to_bytes(
            32, "big"
        )

        return public, private

    def sign(self, private_key, message):
        key = ec.derive_private_key(
            int.from_bytes(private_key, "big"),
            ec.SECP256K1()
        )

        return key.sign(
            message,
            ec.ECDSA(hashes.SHA256())
        )

    def verify(self, public_key, message, signature):
        try:
            key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(),
                public_key
            )

            key.verify(
                signature,
                message,
                ec.ECDSA(hashes.SHA256())
            )

            return True

        except (InvalidSignature, ValueError, TypeError):
            return False


class MLDSASigner:
    name = "ML-DSA-44"

    def __init__(self):
        try:
            import oqs
        except ImportError as exc:
            raise RuntimeError(
                "Install liboqs and its Python bindings first"
            ) from exc

        self.oqs = oqs

        if "ML-DSA-44" not in oqs.get_enabled_sig_mechanisms():
            raise RuntimeError("ML-DSA-44 is unavailable in liboqs")

    def generate_keypair(self):
        with self.oqs.Signature("ML-DSA-44") as signer:
            public = signer.generate_keypair()
            private = signer.export_secret_key()

        return bytes(public), bytes(private)

    def sign(self, private_key, message):
        with self.oqs.Signature(
            "ML-DSA-44",
            secret_key=private_key
        ) as signer:
            return bytes(signer.sign(message))

    def verify(self, public_key, message, signature):
        try:
            with self.oqs.Signature("ML-DSA-44") as signer:
                return bool(
                    signer.verify(message, signature, public_key)
                )
        except (ValueError, RuntimeError):
            return False


def get_signer(algorithm):
    name = algorithm.upper().replace("_", "-")

    if name == "ECDSA":
        return ECDSASigner()

    if name in ("ML-DSA", "ML-DSA-44"):
        return MLDSASigner()

    raise ValueError(f"Unknown algorithm: {algorithm}")
