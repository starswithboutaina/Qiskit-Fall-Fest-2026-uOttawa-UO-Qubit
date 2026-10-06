"""ZNE extrapolators.  (Owner: Ririsha)

All take noise factors `lams` (e.g. [1, 3, 5]) and measured values `vals` and
return the zero-noise estimate. The previous report used `linear` only.
"""

import warnings

import numpy as np
from scipy.optimize import OptimizeWarning, curve_fit


def linear(lams, vals):
    """Linear extrapolation to the zero-noise limit."""
    return float(np.polyval(np.polyfit(lams, vals, 1), 0.0))


def richardson(lams, vals):
    """Polynomial of degree len(lams)-1 through all points, evaluated at 0."""
    return float(
        np.polyval(
            np.polyfit(lams, vals, len(lams) - 1),
            0.0,
        )
    )


def exponential(lams, vals, asymptote=None):
    """Exponential extrapolation to the zero-noise limit.

    If the exponential fit fails, fall back to linear extrapolation.
    OptimizeWarning is suppressed because small ZNE datasets can make
    covariance estimation unreliable even when the fitted value is valid.
    """
    lams = np.asarray(lams, dtype=float)
    vals = np.asarray(vals, dtype=float)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)

            if asymptote is None:
                def model(x, a, b, c):
                    return a * np.exp(-b * x) + c

                p0 = [
                    vals[0] - vals[-1],
                    0.3,
                    vals[-1],
                ]

                params, _ = curve_fit(
                    model,
                    lams,
                    vals,
                    p0=p0,
                    maxfev=10000,
                )

                return float(model(0.0, *params))

            def model(x, a, b):
                return a * np.exp(-b * x) + asymptote

            p0 = [
                vals[0] - asymptote,
                0.3,
            ]

            params, _ = curve_fit(
                model,
                lams,
                vals,
                p0=p0,
                maxfev=10000,
            )

            return float(model(0.0, *params))

    except (RuntimeError, ValueError, TypeError):
        return linear(lams, vals)


EXTRAPOLATORS = {
    "linear": linear,
    "richardson": richardson,
    "exponential": exponential,
}