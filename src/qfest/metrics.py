"""Error metrics vs the ED reference.  (Owner: Ririsha)"""
import numpy as np

def percent_deviation(measured, exact):
    """Max-relative-style deviation in %, as in the report's Table 2 (guards tiny denominators)."""
    measured, exact = np.asarray(measured, float), np.asarray(exact, float)
    return 100.0 * np.abs(measured - exact) / np.maximum(np.abs(exact), 1e-12)

def max_percent_deviation(measured, exact):
    return float(np.max(percent_deviation(measured, exact)))

def rmse(measured, exact):
    d = np.asarray(measured, float) - np.asarray(exact, float)
    return float(np.sqrt(np.mean(d ** 2)))

def error_vs_time(times, measured, exact):
    """Return the absolute error between measured and exact curves at each time."""
    times = np.asarray(times, float)
    measured = np.asarray(measured, float)
    exact = np.asarray(exact, float)

    if times.shape != measured.shape or measured.shape != exact.shape:
        raise ValueError("times, measured, and exact must have the same shape")

    return {
        "t": times,
        "error": np.abs(measured - exact)
    }