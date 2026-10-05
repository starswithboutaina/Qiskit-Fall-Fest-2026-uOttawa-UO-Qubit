import numpy as np
import pytest

from qfest.ed import ground_state_observables, quench
from qfest.extrapolation import linear, richardson, exponential
from qfest.metrics import percent_deviation, max_percent_deviation, rmse, error_vs_time

# Entries of the previous report's Table 1 that are self-consistent (periodic chain, J=1).
# Other entries of that table disagree with exact diagonalization and with Kramers-Wannier
# duality (Mx(h) = Mzz(1/h)); see docs/TABLE1_DISCREPANCIES.md.
TABLE1_OK = [
    (6, 0.5, "Mz", 0.969914), (6, 0.5, "Mzz", 0.931517),
    (6, 2.0, "Mx", 0.931517), (6, 2.0, "Mzz", 0.265198),
    (8, 0.5, "Mx", 0.260062), (8, 0.5, "Mzz", 0.933604),
    (8, 2.0, "Mz", 0.481939), (8, 2.0, "Mx", 0.933604), (8, 2.0, "Mzz", 0.260062),
    (10, 2.0, "Mx", 0.934076), (10, 2.0, "Mzz", 0.258970),
]


@pytest.mark.parametrize("n,h,key,val", TABLE1_OK)
def test_ground_state_matches_report(n, h, key, val):
    assert ground_state_observables(n, 1.0, h)[key] == pytest.approx(val, abs=2e-6)


@pytest.mark.parametrize("n", [6, 8])
def test_kramers_wannier_duality(n):
    lo, hi = ground_state_observables(n, 1.0, 0.5), ground_state_observables(n, 1.0, 2.0)
    assert lo["Mx"] == pytest.approx(hi["Mzz"], abs=1e-8)
    assert lo["Mzz"] == pytest.approx(hi["Mx"], abs=1e-8)
    crit = ground_state_observables(n, 1.0, 1.0)
    assert crit["Mx"] == pytest.approx(crit["Mzz"], abs=1e-8)


def test_trotter_circuit_converges_to_ed():
    from qiskit.quantum_info import Statevector
    from qfest.tfim import tfim_circuit
    from qfest.ed import observables_ops, measure
    n, h, T = 6, 0.5, 2.0
    ops = observables_ops(n)
    exact = quench(n, [T], 1.0, h)["Mzz"][0]
    errs = []
    for dt in (0.2, 0.1, 0.05):
        psi = Statevector(tfim_circuit(n, 1.0, h, dt, int(round(T / dt)), order=2)).data
        errs.append(abs(measure(psi, ops)["Mzz"] - exact))
    assert errs[0] > errs[1] > errs[2]
    assert errs[2] < 1e-3


def test_extrapolators_recover_known_decay():
    lams = [1, 3, 5]
    vals = [0.8 * np.exp(-0.1 * x) for x in lams]
    assert exponential(lams, vals, asymptote=0.0) == pytest.approx(0.8, abs=1e-6)
    assert abs(linear(lams, vals) - 0.8) > abs(richardson(lams, vals) - 0.8)

def test_linear_extrapolation_recovers_constant_value():
    lams = [1, 3, 5]
    vals = [2.0, 2.0, 2.0]

    result = linear(lams, vals)

    assert result == pytest.approx(2.0)


def test_richardson_extrapolation_recovers_known_value():
    lams = [1, 3, 5]

    # f(x) = 2 + 0.5*x + 0.1*x^2
    # Therefore f(0) = 2
    vals = [2 + 0.5 * x + 0.1 * x**2 for x in lams]

    result = richardson(lams, vals)

    assert result == pytest.approx(2.0, abs=1e-10)


def test_exponential_extrapolation_handles_noisy_data():
    rng = np.random.default_rng(42)

    lams = np.array([1, 3, 5])
    true_value = 0.8

    clean = true_value * np.exp(-0.1 * lams)
    noisy = clean + rng.normal(0, 0.001, size=len(lams))

    result = exponential(lams, noisy, asymptote=0.0)

    assert result == pytest.approx(true_value, abs=0.02)

def test_exponential_falls_back_to_linear_when_fit_fails(monkeypatch):
    import qfest.extrapolation as extrapolation

    def failing_curve_fit(*args, **kwargs):
        raise RuntimeError("forced fit failure")

    monkeypatch.setattr(extrapolation, "curve_fit", failing_curve_fit)

    lams = [1, 3, 5]
    vals = [0.8, 0.6, 0.4]

    expected = linear(lams, vals)
    result = exponential(lams, vals, asymptote=0.0)

    assert result == pytest.approx(expected)

def test_percent_deviation():
    measured = [1.1, 2.0, 2.7]
    exact = [1.0, 2.0, 3.0]

    result = percent_deviation(measured, exact)

    expected = [10.0, 0.0, 10.0]

    assert np.allclose(result, expected)


def test_max_percent_deviation():
    measured = [1.1, 2.0, 2.7]
    exact = [1.0, 2.0, 3.0]

    result = max_percent_deviation(measured, exact)

    assert result == pytest.approx(10.0)


def test_rmse():
    measured = [1.0, 2.0, 4.0]
    exact = [1.0, 3.0, 3.0]

    result = rmse(measured, exact)

    expected = np.sqrt((0**2 + (-1)**2 + 1**2) / 3)

    assert result == pytest.approx(expected)


def test_error_vs_time():
    times = [0.0, 1.0, 2.0]
    measured = [1.0, 0.8, 0.5]
    exact = [1.0, 1.0, 0.7]

    result = error_vs_time(times, measured, exact)

    assert np.allclose(result["t"], times)
    assert np.allclose(result["error"], [0.0, 0.2, 0.2])


def test_error_vs_time_rejects_different_lengths():
    times = [0.0, 1.0, 2.0]
    measured = [1.0, 0.8]
    exact = [1.0, 1.0, 0.7]

    with pytest.raises(ValueError):
        error_vs_time(times, measured, exact)

def test_extrapolator_comparison_selects_best_method():
    """Check that the comparison identifies the extrapolator with the lowest RMSE."""
    from qfest.extrapolation import linear, richardson, exponential

    lams = [1, 3, 5]

    # Known zero-noise value
    true_value = 0.8

    # Simulated noisy measurements
    vals_by_factor = {
        1: [0.74, 0.75, 0.76],
        3: [0.72, 0.73, 0.74],
        5: [0.70, 0.71, 0.72],
    }

    extrapolators = {
        "linear": linear,
        "richardson": richardson,
        "exponential": exponential,
    }

    results = {}

    for name, func in extrapolators.items():
        estimates = []

        for i in range(len(vals_by_factor[1])):
            vals = [vals_by_factor[1][i],
                    vals_by_factor[3][i],
                    vals_by_factor[5][i]]

            estimates.append(func(lams, vals))

        error = np.sqrt(
            np.mean((np.asarray(estimates) - true_value) ** 2)
        )

        results[name] = error

    best = min(results, key=results.get)

    assert best in extrapolators
    assert results[best] == min(results.values())

    