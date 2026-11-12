import oqs

algorithms = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]

message = b"Benchmark test for post-quantum blockchain"

for algorithm in algorithms:
    print(f"\nTesting {algorithm}")

    if algorithm not in oqs.get_enabled_sig_mechanisms():
        print(f"{algorithm} is not available.")
        continue

    signer = oqs.Signature(algorithm)
    public_key = signer.generate_keypair()

    signature = signer.sign(message)

    verifier = oqs.Signature(algorithm)
    verified = verifier.verify(message, signature, public_key)

    print("Verification:", verified)
    print("Public key:", len(public_key), "bytes")
    print("Signature:", len(signature), "bytes")

    signer.free()
    verifier.free()

print("\nAll tests completed!")