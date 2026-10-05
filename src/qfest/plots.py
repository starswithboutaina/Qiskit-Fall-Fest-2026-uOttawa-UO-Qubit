"""Plotting from results/*.json.  (Owner: Toto)

TODO: error-vs-time (log scale), ED vs methods, discard-rate vs depth,
SWAP overhead (all-to-all vs heavy-hex), summary table vs the previous report.
Colour-blind-safe palette; label axes with units; one function per figure; save PNGs to results/figs/.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from qfest.results import load

FIG_DIR = Path("results/figs")
FIG_DIR.mkdir(parents=True, exist_ok=True)


def plot_observable_vs_time(
    times,
    series,
    observable_name="Mzz",
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

    return save_path


def plot_error_vs_time(
    times,
    error_series,
    observable_name="Mzz",
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

    return save_path

def load_observable_series(result_names, observable_name="Mzz"):
    """
    Load multiple result JSON files and extract one observable from each.

    Parameters
    ----------
    result_names : sequence
        Result file names without the .json extension.
    observable_name : str
        Observable to extract, such as "Mz", "Mx", or "Mzz".

    Returns
    -------
    times : list
        Shared time points.
    series : dict
        Mapping from result name to observable values.
    """

    series = {}
    times = None

    for name in result_names:
        result = load(name)

        if times is None:
            times = result["t"]

        series[name] = result["observables"][observable_name]

    return times, series