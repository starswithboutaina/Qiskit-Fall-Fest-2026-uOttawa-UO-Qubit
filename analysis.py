import json
import matplotlib.pyplot as plt
from pathlib import Path


def load_results(filename="tfim_results.json"):
    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(f"Could not find result file: {filename}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_results(data):
    required_keys = [
        "transpilation",
        "exact_magnetization",
        "aer_expectations",
        "zne_aer",
        "aer_counts_mag",
        "analysis",
    ]

    missing = [key for key in required_keys if key not in data]

    if missing:
        raise ValueError(
            f"Missing required result fields: {', '.join(missing)}"
        )

def summarize_results(data):
    exact = data["exact_magnetization"]
    aer = data["aer_expectations"]
    zne = data["zne_aer"]["mitigated"]
    counts_mag = data["aer_counts_mag"]

    print("\nMagnetization summary")
    print("---------------------")
    print(f"Exact magnetization: {exact:.6f}")

    for level, value in aer.items():
        error = abs(exact - value)
        print(
            f"Aer level {level}: {value:.6f} "
            f"(absolute error = {error:.6f})"
        )

    zne_error = abs(exact - zne)
    print(
        f"ZNE mitigated: {zne:.6f} "
        f"(absolute error = {zne_error:.6f})"
    )

    counts_error = abs(exact - counts_mag)
    print(
        f"Counts magnetization: {counts_mag:.6f} "
        f"(absolute error = {counts_error:.6f})"
    )

def plot_magnetization_comparison(data):
    exact = data["exact_magnetization"]
    aer = data["aer_expectations"]
    zne = data["zne_aer"]["mitigated"]
    counts_mag = data["aer_counts_mag"]

    labels = []
    values = []

    for level, value in aer.items():
        labels.append(f"Aer L{level}")
        values.append(value)

    labels.append("ZNE")
    values.append(zne)

    labels.append("Counts")
    values.append(counts_mag)

    plt.figure()

    plt.bar(labels, values)

    plt.axhline(
        exact,
        linestyle="--",
        label=f"Exact = {exact:.4f}"
    )

    plt.ylabel("Magnetization")
    plt.title("Magnetization Comparison")

    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        "results/magnetization_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

if __name__ == "__main__":
    results = load_results()
    validate_results(results)

    print("Result file loaded successfully.")
    print("Top-level keys:")

    for key in results:
        print(f" - {key}")

    summarize_results(results)
    plot_magnetization_comparison(results)