
"""Utilities for comparing ZNE extrapolators against reference data."""

import numpy as np

from qfest.extrapolation import EXTRAPOLATORS
from qfest.metrics import percent_deviation, rmse
from qfest.results import load


def compare_canonical_tfim(canonical_file):
    """Compare ZNE extrapolators against the exact canonical TFIM endpoint.

    The canonical TFIM file contains a single endpoint measurement of the
    signed magnetization at t = steps * dt.
    """

    data = load(canonical_file)

    exact = float(data["exact_magnetization"])

    zne = data["zne_aer"]

    noise_factors = np.asarray(
        zne["noise_factors"],
        dtype=float,
    )

    raw_values = np.asarray(
        zne["raw"],
        dtype=float,
    )

    if len(noise_factors) != len(raw_values):
        raise ValueError(
            "noise_factors and raw must have the same length"
        )

    params = data["meta"]["params"]

    final_time = (
        float(params["dt"])
        * int(params["steps"])
    )

    comparison = {
        "experiment": "canonical_tfim_extrapolator_comparison",
        "backend": params.get("backend", "unknown"),
        "params": params,
        "method": "linear_vs_richardson_vs_exponential",
        "t": final_time,
        "observables": {
            "signed_magnetization": {
                "exact": exact,
                "raw": raw_values,
                "noise_factors": noise_factors,
            }
        },
        "extra": {
            "source_file": canonical_file,
            "comparison_type": "single_endpoint",
            "noise_factors": noise_factors,
            "raw_value": raw_values,
            "exact_value": exact,
            "estimates": {},
            "absolute_error": {},
            "percent_deviation": {},
            "rmse": {},
            "best_extrapolator": None,
        },
    }

    for name, extrapolator in EXTRAPOLATORS.items():

        estimate = float(
            extrapolator(
                noise_factors,
                raw_values,
            )
        )

        absolute_error = abs(
            estimate - exact
        )

        error_rmse = rmse(
            [estimate],
            [exact],
        )

        deviation = percent_deviation(
            [estimate],
            [exact],
        )[0]

        comparison["extra"]["estimates"][name] = estimate

        comparison["extra"]["absolute_error"][name] = float(
            absolute_error
        )

        comparison["extra"]["percent_deviation"][name] = float(
            deviation
        )

        comparison["extra"]["rmse"][name] = float(
            error_rmse
        )

        comparison["observables"]["signed_magnetization"][name] = (
            estimate
        )

    comparison["extra"]["best_extrapolator"] = min(
        comparison["extra"]["rmse"],
        key=comparison["extra"]["rmse"].get,
    )

    if "mitigated" in zne:
        comparison["extra"]["reference_linear_result"] = float(
            zne["mitigated"]
        )

    return comparison