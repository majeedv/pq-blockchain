
import csv
import random
import statistics
from collections import defaultdict

try:
    from scipy.stats import mannwhitneyu
except ImportError:
    raise SystemExit("Install scipy using: pip install scipy")


CSV_FILE = "data/benchmark_results.csv"
BOOTSTRAP_SAMPLES = 10000
CONFIDENCE_LEVEL = 0.95

random.seed(42)


def load_results():

    results = defaultdict(list)

    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (row["algorithm"], row["operation"])
            results[key].append(float(row["time_ns"]))

    return results


def bootstrap_median_ci(values):

    medians = []

    for _ in range(BOOTSTRAP_SAMPLES):
        sample = random.choices(values, k=len(values))
        medians.append(statistics.median(sample))

    medians.sort()

    lower_index = int(0.025 * BOOTSTRAP_SAMPLES)
    upper_index = int(0.975 * BOOTSTRAP_SAMPLES)

    return medians[lower_index], medians[upper_index]


def main():

    results = load_results()

    algorithms = ["ECDSA", "ML-DSA-44"]
    operations = ["keygen", "signing", "verification"]

    print("\n======= STATISTICAL ANALYSIS =======")

    for operation in operations:

        ecdsa = results[(algorithms[0], operation)]
        mldsa = results[(algorithms[1], operation)]

        print(f"\nOperation: {operation}")

        for name, values in [
            ("ECDSA", ecdsa),
            ("ML-DSA-44", mldsa)
        ]:

            median = statistics.median(values)
            lower, upper = bootstrap_median_ci(values)

            print(f"\n{name}")
            print("Median:", median, "ns")
            print("95% Bootstrap CI:", lower, "-", upper, "ns")

        test = mannwhitneyu(
            ecdsa,
            mldsa,
            alternative="two-sided"
        )

        print("\nMann-Whitney U:", test.statistic)
        print("P-value:", test.pvalue)

        if test.pvalue < 0.05:
            print("Result: Statistically significant difference")
        else:
            print("Result: No statistically significant difference")


if __name__ == "__main__":
    main()
