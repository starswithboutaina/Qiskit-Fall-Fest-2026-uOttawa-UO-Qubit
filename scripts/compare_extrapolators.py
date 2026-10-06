import argparse

from qfest.comparison import compare_canonical_tfim
from qfest.extrapolation import EXTRAPOLATORS
from qfest.results import save


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Compare ZNE extrapolators against "
            "the canonical TFIM reference."
        )
    )

    parser.add_argument(
        "canonical_file",
        help=(
            "Canonical JSON filename "
            "without the .json extension."
        ),
    )

    args = parser.parse_args()

    result = compare_canonical_tfim(
        args.canonical_file
    )

    output_name = (
        f"extrapolator_comparison_{args.canonical_file}"
    )

    path = save(
        result,
        output_name,
    )

    print(f"Saved comparison to: {path}")

    print("\nCanonical TFIM endpoint")
    print(f"  t = {result['t']:.6f}")

    print("\nExact signed magnetization:")
    print(
        f"  {result['extra']['exact_value']:.6f}"
    )

    print("\nRaw noisy measurements:")

    for factor, value in zip(
        result["extra"]["noise_factors"],
        result["extra"]["raw_value"],
    ):
        print(
            f"  {factor:.0f}x noise: {value:.6f}"
        )

    print("\nExtrapolator comparison:")

    for name in EXTRAPOLATORS:

        estimate = (
            result["extra"]["estimates"][name]
        )

        error = (
            result["extra"]["absolute_error"][name]
        )

        deviation = (
            result["extra"]["percent_deviation"][name]
        )

        print(
            f"  {name}: "
            f"estimate={estimate:.6f}, "
            f"absolute_error={error:.6f}, "
            f"deviation={deviation:.2f}%"
        )

    if "reference_linear_result" in result["extra"]:

        print("\nCanonical reference linear ZNE:")

        print(
            f"  "
            f"{result['extra']['reference_linear_result']:.6f}"
        )

    print(
        f"\nBest extrapolator: "
        f"{result['extra']['best_extrapolator']}"
    )


if __name__ == "__main__":
    main()