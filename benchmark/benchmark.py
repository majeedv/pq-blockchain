
import oqs
import time
import csv
import platform
import statistics
import os

from crypto.signer import get_signer

# Algorithms to benchmark
ALGORITHMS = ["ECDSA", "ML-DSA-44"]

# Benchmark settings
WARMUP_RUNS = 20
BENCHMARK_RUNS = 1000

MESSAGE = b"Post quantum blockchain benchmark test"

RESULTS_FOLDER = "data"
RESULTS_FILE = os.path.join(
    RESULTS_FOLDER, "benchmark_results.csv"
)


def benchmark_algorithm(algorithm):

    print(f"\nBenchmarking {algorithm}...")

    signer = get_signer(algorithm)

    keygen_times = []
    signing_times = []
    verification_times = []

    public_key_size = 0
    private_key_size = 0
    signature_size = 0

    for run in range(WARMUP_RUNS + BENCHMARK_RUNS):

        # Measure key generation
        start = time.perf_counter_ns()
        public_key, private_key = signer.generate_keypair()
        keygen_time = time.perf_counter_ns() - start

        # Measure signing
        start = time.perf_counter_ns()
        signature = signer.sign(private_key, MESSAGE)
        signing_time = time.perf_counter_ns() - start

        # Measure verification
        start = time.perf_counter_ns()
        valid = signer.verify(
            public_key, MESSAGE, signature
        )
        verification_time = time.perf_counter_ns() - start

        if not valid:
            raise RuntimeError(
                f"Signature verification failed: {algorithm}"
            )

        # Ignore warm-up measurements
        if run >= WARMUP_RUNS:

            keygen_times.append(keygen_time)
            signing_times.append(signing_time)
            verification_times.append(verification_time)

            public_key_size = len(public_key)
            private_key_size = len(private_key)
            signature_size = len(signature)

    return {
        "algorithm": algorithm,
        "keygen_times": keygen_times,
        "signing_times": signing_times,
        "verification_times": verification_times,
        "public_key_bytes": public_key_size,
        "private_key_bytes": private_key_size,
        "signature_bytes": signature_size
    }


def save_results(results):

    os.makedirs(RESULTS_FOLDER, exist_ok=True)

    with open(RESULTS_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "algorithm",
            "operation",
            "run_id",
            "time_ns",
            "pub_key_bytes",
            "priv_key_bytes",
            "sig_bytes",
            "machine",
            "library_version"
        ])

        for result in results:

            for operation in [
                "keygen",
                "signing",
                "verification"
            ]:

                times = result[f"{operation}_times"]

                for run_id, elapsed in enumerate(times, start=1):

                    writer.writerow([
                        result["algorithm"],
                        operation,
                        run_id,
                        elapsed,
                        result["public_key_bytes"],
                        result["private_key_bytes"],
                        result["signature_bytes"],
                        platform.platform(),
                        oqs.oqs_python_version()
                    ])

    print(f"\nResults saved to {RESULTS_FILE}")


def print_summary(results):

    print("\n========== BENCHMARK SUMMARY ==========")

    for result in results:

        print(f"\n{result['algorithm']}")

        for operation in [
            "keygen",
            "signing",
            "verification"
        ]:

            values = result[f"{operation}_times"]

            quartiles = statistics.quantiles(values, n=4)

            print(f"{operation}:")
            print("  Median:", statistics.median(values), "ns")
            print("  IQR:", quartiles[2] - quartiles[0], "ns")

        print("  Public key:", result["public_key_bytes"], "bytes")
        print("  Private key:", result["private_key_bytes"], "bytes")
        print("  Signature:", result["signature_bytes"], "bytes")


def main():

    print("ECDSA vs POST-QUANTUM SIGNATURE BENCHMARK")
    print("Warm-up runs:", WARMUP_RUNS)
    print("Measured runs:", BENCHMARK_RUNS)

    results = []

    for algorithm in ALGORITHMS:

        result = benchmark_algorithm(algorithm)
        results.append(result)

    save_results(results)
    print_summary(results)

    print("\nBenchmark completed!")


if __name__ == "__main__":
    main()
