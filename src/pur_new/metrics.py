from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Sequence


def hold_stability_index(eta_t0: float, eta_t1: float) -> float:
    """Relative viscosity drift over a fixed hold window.

    SI = (eta_t1 - eta_t0) / eta_t0
    """
    if eta_t0 <= 0:
        raise ValueError("eta_t0 must be positive")
    return (eta_t1 - eta_t0) / eta_t0


def hold_loss(eta_t0: float, eta_t1: float) -> float:
    """Default design loss when both upward and downward drift are undesirable."""
    return abs(hold_stability_index(eta_t0, eta_t1))


def stability_gain(reference_si: float, candidate_si: float) -> float:
    """Descriptive flattening gain using absolute SI on a matched window."""
    candidate_loss = abs(candidate_si)
    if candidate_loss == 0:
        return math.inf
    return abs(reference_si) / candidate_loss


def coefficient_of_variation(values: Sequence[float], *, sample: bool = True) -> float:
    """Coefficient of variation for positive-valued replicate measurements.

    The default uses sample standard deviation. For very small n this is a
    descriptive summary only, not a population estimate.
    """
    if len(values) < 2:
        raise ValueError("at least two values are required")
    if any(v <= 0 for v in values):
        raise ValueError("all values must be positive")
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if sample else statistics.pstdev(values)
    return sd / mean


def log_max_min_spread(values: Sequence[float]) -> float:
    """Natural-log max/min spread for positive replicate values."""
    if len(values) < 2:
        raise ValueError("at least two values are required")
    if any(v <= 0 for v in values):
        raise ValueError("all values must be positive")
    return math.log(max(values) / min(values))


def max_min_ratio(values: Sequence[float]) -> float:
    """Max/min ratio for positive replicate values."""
    if len(values) < 2:
        raise ValueError("at least two values are required")
    if any(v <= 0 for v in values):
        raise ValueError("all values must be positive")
    return max(values) / min(values)


def mean_profile_si(start_values: Iterable[float], end_values: Iterable[float]) -> float:
    """SI computed from mean start and mean end values across matched repeats."""
    start = list(start_values)
    end = list(end_values)
    if not start or not end or len(start) != len(end):
        raise ValueError("matched non-empty start and end values are required")
    return hold_stability_index(statistics.fmean(start), statistics.fmean(end))


def andrade_fit(temperature_c: Sequence[float], viscosity: Sequence[float]) -> dict[str, float]:
    """Descriptive linear fit of ln(eta) against 1/T.

    Returns slope, intercept and R^2. The slope may be converted to an apparent
    activation-like parameter outside this function if scientifically justified.
    This helper deliberately does not label the slope as a molecular activation
    energy.
    """
    if len(temperature_c) != len(viscosity) or len(temperature_c) < 3:
        raise ValueError("matched temperature/viscosity sequences with n>=3 are required")
    if any(v <= 0 for v in viscosity):
        raise ValueError("viscosity values must be positive")

    x = [1.0 / (t + 273.15) for t in temperature_c]
    y = [math.log(v) for v in viscosity]
    x_bar = statistics.fmean(x)
    y_bar = statistics.fmean(y)
    sxx = sum((xi - x_bar) ** 2 for xi in x)
    if sxx == 0:
        raise ValueError("temperature values must vary")
    sxy = sum((xi - x_bar) * (yi - y_bar) for xi, yi in zip(x, y, strict=True))
    slope = sxy / sxx
    intercept = y_bar - slope * x_bar
    fitted = [intercept + slope * xi for xi in x]
    ss_res = sum((yi - fi) ** 2 for yi, fi in zip(y, fitted, strict=True))
    ss_tot = sum((yi - y_bar) ** 2 for yi in y)
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return {"slope_K": slope, "intercept": intercept, "r2": r2}
