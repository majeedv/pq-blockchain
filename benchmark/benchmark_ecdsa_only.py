"""Run independently of oqs: python -m benchmark.benchmark_ecdsa_only"""
import csv
import platform
import statistics
import time
from pathlib import Path
from crypto.signer import get_signer

WARMUP = 20
RUNS = 1000
OUT = Path("data/ecdsa_benchmark_results.csv")
MESSAGE = b"Post quantum blockchain benchmark test"

def main():
    signer = get_signer("ECDSA")
    rows = []
    times = {"keygen": [], "signing": [], "verification": []}
    for i in range(WARMUP + RUNS):
        t = time.perf_counter_ns()
        public, private = signer.generate_keypair()
        keygen_ns = time.perf_counter_ns() - t
        t = time.perf_counter_ns()
        sig = signer.sign(private, MESSAGE)
        signing_ns = time.perf_counter_ns() - t
        t = time.perf_counter_ns()
        ok = signer.verify(public, MESSAGE, sig)
        verification_ns = time.perf_counter_ns() - t
        if not ok:
            raise RuntimeError("ECDSA verification failed")
        if i < WARMUP:
            continue
        for operation, elapsed in (("keygen", keygen_ns), ("signing", signing_ns), ("verification", verification_ns)):
            times[operation].append(elapsed)
            rows.append({"algorithm":"ECDSA","operation":operation,"run_id":i-WARMUP+1,"time_ns":elapsed,"pub_key_bytes":len(public),"priv_key_bytes":len(private),"sig_bytes":len(sig),"machine":platform.platform(),"library_version":"cryptography"})
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    print("Saved",len(rows),"rows to",OUT)
    for operation, values in times.items():
        print(operation,"median_ns",statistics.median(values))
    print("NOTE: Compare ECDSA and ML-DSA only when measured under matched conditions.")

if __name__ == "__main__":
    main()
