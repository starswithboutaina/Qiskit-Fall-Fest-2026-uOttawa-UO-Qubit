"""Plotting utilities for canonical TFIM and Iceberg results.

Canonical TFIM plots currently include:
- circuit depth vs optimization level
- absolute error vs optimization level
- ZNE comparison

Iceberg observables must remain separately labeled until the team
agrees on a shared magnetization convention.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

FIG_DIR = Path("results/figs")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def plot_observable_vs_time(
    times,
    series,
    observable_name="M_zz",
    filename=None,
):
    """
    Plot one observable versus time for multiple simulation methods.
    """

    plt.figure()

    for label, values in series.items():
        plt.plot(times, values, marker="o", label=label)

    plt.xlabel("Time")
    plt.ylabel(observable_name)
    plt.title(f"{observable_name} vs Time")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if filename is None:
        filename = f"{observable_name}_vs_time.png"

    save_path = FIG_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

    return save_path


def plot_error_vs_time(
    times,
    error_series,
    observable_name="M_zz",
    filename=None,
):
    """
    Plot absolute error versus time for multiple methods on a log scale.
    """

    plt.figure()

    for label, values in error_series.items():
        safe_values = [max(value, 1e-12) for value in values]
        plt.semilogy(times, safe_values, marker="o", label=label)

    plt.xlabel("Time")
    plt.ylabel(f"Absolute Error in {observable_name}")
    plt.title(f"{observable_name} Error vs Time")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if filename is None:
        filename = f"{observable_name}_error_vs_time.png"

    save_path = FIG_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

    return save_path

def plot_discard_rate_vs_depth(
    depths,
    discard_rates,
    filename="discard_rate_vs_depth.png",
):
    """
    Plot Iceberg discard rate versus circuit depth.
    """

    plt.figure()

    plt.plot(
        depths,
        discard_rates,
        marker="o",
    )

    plt.xlabel("Circuit Depth")
    plt.ylabel("Discard Rate")
    plt.title("Iceberg Discard Rate vs Circuit Depth")

    plt.grid(True)
    plt.tight_layout()

    save_path = FIG_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

    return save_path

def plot_swap_overhead(
    labels,
    all_to_all_swaps,
    heavy_hex_swaps,
    filename="swap_overhead.png",
):
    """
    Compare SWAP counts for all-to-all and heavy-hex connectivity.
    """

    plt.figure()

    x = range(len(labels))
    width = 0.35

    left_positions = [i - width / 2 for i in x]
    right_positions = [i + width / 2 for i in x]

    plt.bar(
        left_positions,
        all_to_all_swaps,
        width=width,
        label="All-to-All",
    )

    plt.bar(
        right_positions,
        heavy_hex_swaps,
        width=width,
        label="Heavy-Hex",
    )

    plt.xticks(list(x), labels)

    plt.xlabel("Circuit")
    plt.ylabel("SWAP Count")
    plt.title("SWAP Overhead: All-to-All vs Heavy-Hex")

    plt.legend()
    plt.grid(axis="y")
    plt.tight_layout()

    save_path = FIG_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

    return save_path

def load_canonical_results(filename="results_canonical/tfim_results.json"):
    """
    Load the canonical TFIM results JSON file.
    """

    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def plot_depth_vs_optimization(
    data,
    filename="depth_vs_optimization.png",
):
    """
    Plot circuit depth versus Qiskit optimization level.
    """

    rows = data["transpilation"]

    levels = [row["optimization_level"] for row in rows]
    depths = [row["depth"] for row in rows]

    plt.figure()

    plt.plot(
        levels,
        depths,
        marker="o",
    )

    plt.xlabel("Optimization Level")
    plt.ylabel("Circuit Depth")
    plt.title("Circuit Depth vs Optimization Level")

    plt.xticks(levels)
    plt.grid(True)
    plt.tight_layout()

    save_path = FIG_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

    return save_path

def plot_error_vs_optimization(
    data,
    filename="error_vs_optimization.png",
):
    """
    Plot absolute error versus Qiskit optimization level.
    """

    rows = [
        row
        for row in data["analysis"]["table"]
        if isinstance(row["optimization_level"], int)
    ]

    levels = [row["optimization_level"] for row in rows]
    errors = [row["abs_error"] for row in rows]

    plt.figure()

    plt.plot(
        levels,
        errors,
        marker="o",
    )

    plt.xlabel("Optimization Level")
    plt.ylabel("Absolute Error")
    plt.title("Absolute Error vs Optimization Level")

    plt.xticks(levels)
    plt.grid(True)
    plt.tight_layout()

    save_path = FIG_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

    return save_path

def plot_zne_comparison(
    data,
    filename="zne_comparison.png",
):
    """
    Plot noisy ZNE samples together with mitigated and exact values.
    """

    zne = data["zne_aer"]

    noise_factors = zne["noise_factors"]
    raw_values = zne["raw"]
    mitigated = zne["mitigated"]
    exact = data["exact_magnetization"]

    plt.figure()

    plt.plot(
        noise_factors,
        raw_values,
        marker="o",
        label="Raw",
    )

    plt.axhline(
        mitigated,
        linestyle="--",
        label="ZNE Mitigated",
    )

    plt.axhline(
        exact,
        linestyle=":",
        label="Exact",
    )

    plt.xlabel("Noise Factor")
    plt.ylabel("Signed M_z")
    plt.title("Zero-Noise Extrapolation Comparison")

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    save_path = FIG_DIR / filename
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

    return save_path

if __name__ == "__main__":
    data = load_canonical_results()

    plot_depth_vs_optimization(data)
    plot_error_vs_optimization(data)
    plot_zne_comparison(data)