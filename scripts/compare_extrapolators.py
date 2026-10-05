import argparse
from pathlib import Path

import numpy as np

from qfest.extrapolation import EXTRAPOLATORS
from qfest.metrics import rmse
from qfest.results import load, save


OBSERVABLES = ("Mz", "Mx", "Mzz")
NOISE_FACTORS = [1, 3, 5]


def find_matching_ed_file(noisy):
    """Find the ED reference filename matching the noisy simulation parameters."""
    n = noisy["params"]["n"]
    h = noisy["params"]["h"]

    h_name = str(h).replace(".", "p")
    return f"ed_n{n}_h{h_name}"


def compare_extrapolators(noisy_file, ed_file=None):
    """Compare extrapolators against the matching ED reference."""
    noisy = load(noisy_file)

    if ed_file is None:
        ed_file = find_matching_ed_file(noisy)

    ed = load(ed_file)

    noisy_times = np.asarray(noisy["t"], dtype=float)
    ed_times = np.asarray(ed["t"], dtype=float)

    # Find the ED values at the same times as the noisy simulation.
    ed_indices = []

    for t in noisy_times:
        matches = np.where(np.isclose(ed_times, t))[0]

        if len(matches) == 0:
            raise ValueError(f"No matching ED time found for t={t}")

        ed_indices.append(matches[0])

    values_by_factor = noisy["extra"]["observables_by_noise_factor"]

    comparison = {
        "experiment": "extrapolator_comparison",
        "backend": noisy["backend"],
        "params": noisy["params"],
        "method": "linear_vs_richardson_vs_exponential",
        "t": noisy_times,
        "observables": {},
        "extra": {
            "source_noisy": noisy_file,
            "source_ed": ed_file,
            "noise_factors": NOISE_FACTORS,
            "rmse_by_observable": {},
            "overall_rmse": {},
            "best_extrapolator": None,
        },
    }

    total_squared_errors = {
        name: []
        for name in EXTRAPOLATORS
    }

    for observable in OBSERVABLES:
        comparison["observables"][observable] = {}
        comparison["extra"]["rmse_by_observable"][observable] = {}

        exact = np.asarray(
            ed["observables"][observable],
            dtype=float
        )[ed_indices]

        for name, extrapolator in EXTRAPOLATORS.items():
            extrapolated = []

            for i in range(len(noisy_times)):
                vals = [
                    values_by_factor[str(factor)][observable][i]
                    for factor in NOISE_FACTORS
                ]

                estimate = extrapolator(NOISE_FACTORS, vals)
                extrapolated.append(estimate)

            extrapolated = np.asarray(extrapolated, dtype=float)

            comparison["observables"][observable][name] = extrapolated

            comparison["extra"]["rmse_by_observable"][observable][name] = (
                rmse(extrapolated, exact)
            )

            squared_errors = (extrapolated - exact) ** 2
            total_squared_errors[name].extend(squared_errors.tolist())

    # Calculate one overall RMSE across all observables and times.
    for name, errors in total_squared_errors.items():
        comparison["extra"]["overall_rmse"][name] = float(
            np.sqrt(np.mean(errors))
        )

    comparison["extra"]["best_extrapolator"] = min(
        comparison["extra"]["overall_rmse"],
        key=comparison["extra"]["overall_rmse"].get,
    )

    return comparison


def main():
    parser = argparse.ArgumentParser(
        description="Compare ZNE extrapolators against an ED reference."
    )

    parser.add_argument(
        "noisy_file",
        help="Name of the noisy JSON result without the .json extension."
    )

    parser.add_argument(
        "--ed-file",
        default=None,
        help="Optional ED result filename without .json. "
             "If omitted, it is inferred from the noisy result parameters."
    )

    args = parser.parse_args()

    result = compare_extrapolators(
        args.noisy_file,
        args.ed_file,
    )

    noisy_path = Path(args.noisy_file)
    output_name = f"extrapolator_comparison_{noisy_path.stem}"

    path = save(result, output_name)

    print(f"Saved comparison to: {path}")
    print("\nRMSE by extrapolator:")

    for name, value in result["extra"]["overall_rmse"].items():
        print(f"  {name}: {value:.6f}")

    print(
        f"\nBest extrapolator: "
        f"{result['extra']['best_extrapolator']}"
    )


if __name__ == "__main__":
    main()