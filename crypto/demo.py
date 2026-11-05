
from crypto.signer import get_signer

message = b"Alice pays Bob 5 credits"

for algorithm in ["ECDSA", "ML-DSA-44"]:
    print("\n========================")
    print("Testing:", algorithm)
    print("========================")

    try:
        signer = get_signer(algorithm)

        public_key, private_key = signer.generate_keypair()

        signature = signer.sign(private_key, message)

        valid = signer.verify(
            public_key,
            message,
            signature
        )

        tampered = signer.verify(
            public_key,
            b"Alice pays Bob 500 credits",
            signature
        )

        print("Public key size:", len(public_key), "bytes")
        print("Private key size:", len(private_key), "bytes")
        print("Signature size:", len(signature), "bytes")
        print("Original transaction valid:", valid)
        print("Tampered transaction valid:", tampered)

    except RuntimeError as error:
        print("Algorithm unavailable:", error)
