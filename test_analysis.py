import pytest

from analysis import validate_results


def make_valid_result():
    return {
        "transpilation": [],
        "exact_magnetization": 0.95,
        "aer_expectations": {"0": 0.94},
        "zne_aer": {
            "mitigated": 0.945
        },
        "aer_counts_mag": 0.96,
        "analysis": {}
    }


def test_validate_results_accepts_valid_data():
    data = make_valid_result()

    validate_results(data)


def test_validate_results_rejects_missing_field():
    data = make_valid_result()
    del data["zne_aer"]

    with pytest.raises(ValueError):
        validate_results(data)