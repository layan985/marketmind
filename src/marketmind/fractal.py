"""Memory and fractal measures used by the Market Intelligence Index."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from marketmind._validation import clean_1d


def dfa_hurst(
    values: ArrayLike,
    *,
    min_scale: int = 4,
    max_scale: int | None = None,
    n_scales: int = 12,
    order: int = 1,
) -> float:
    """Estimate the Hurst exponent with detrended fluctuation analysis (DFA).

    The function integrates the demeaned series, detrends non-overlapping segments at
    logarithmically spaced scales, and estimates ``H`` as the log-log slope of the
    fluctuation function. The default linear detrending matches Appendix A.1 of the
    paper.

    Parameters
    ----------
    values:
        One-dimensional return or increment series.
    min_scale, max_scale:
        Smallest and largest segment lengths. By default, the maximum is one quarter
        of the available sample.
    n_scales:
        Number of logarithmically spaced candidate scales.
    order:
        Polynomial detrending order. The paper uses ``1``.
    """
    x = clean_1d(values, minimum=max(16, min_scale * 4))
    if min_scale <= order + 1:
        raise ValueError("min_scale must be larger than order + 1")
    if n_scales < 2:
        raise ValueError("n_scales must be at least 2")

    upper = min(x.size // 4, max_scale or x.size // 4)
    if upper <= min_scale:
        raise ValueError("series is too short for the requested DFA scales")
    scales = np.unique(
        np.floor(np.geomspace(min_scale, upper, num=n_scales)).astype(int)
    )
    profile = np.cumsum(x - np.mean(x))
    fluctuations: list[float] = []
    valid_scales: list[int] = []

    for scale in scales:
        segments = x.size // scale
        if segments < 4:
            continue
        residual_variances: list[float] = []
        grid = np.arange(scale, dtype=float)
        # Use segments from both ends so the unused remainder is represented.
        for start in range(0, segments * scale, scale):
            segment = profile[start : start + scale]
            trend = np.polyval(np.polyfit(grid, segment, order), grid)
            residual_variances.append(float(np.mean((segment - trend) ** 2)))
        for end in range(x.size, x.size - segments * scale, -scale):
            segment = profile[end - scale : end]
            trend = np.polyval(np.polyfit(grid, segment, order), grid)
            residual_variances.append(float(np.mean((segment - trend) ** 2)))
        fluctuation = float(np.sqrt(np.mean(residual_variances)))
        if np.isfinite(fluctuation) and fluctuation > 0:
            valid_scales.append(int(scale))
            fluctuations.append(fluctuation)

    if len(valid_scales) < 2:
        raise ValueError("not enough valid scales to estimate the Hurst exponent")
    slope = np.polyfit(np.log(valid_scales), np.log(fluctuations), 1)[0]
    return float(slope)


def higuchi_fractal_dimension(values: ArrayLike, *, k_max: int = 20) -> float:
    """Estimate Higuchi's fractal dimension using ``k=1,...,k_max``.

    The curve-length normalization follows Equation A.5 of the paper. For a
    self-affine series, the Hurst-equivalent estimate is ``2 - D``.
    """
    x = clean_1d(values, minimum=max(16, 2 * k_max + 1))
    if k_max < 2:
        raise ValueError("k_max must be at least 2")
    if k_max >= x.size // 2:
        raise ValueError("k_max must be smaller than half the series length")

    lengths: list[float] = []
    inverse_scales: list[float] = []
    n = x.size
    for k in range(1, k_max + 1):
        subseries_lengths: list[float] = []
        for m in range(k):
            count = (n - m - 1) // k
            if count < 1:
                continue
            indices = m + np.arange(count + 1) * k
            path_length = float(np.abs(np.diff(x[indices])).sum())
            normalized = path_length * (n - 1) / (count * k * k)
            subseries_lengths.append(normalized)
        if subseries_lengths and np.mean(subseries_lengths) > 0:
            lengths.append(float(np.mean(subseries_lengths)))
            inverse_scales.append(1.0 / k)

    if len(lengths) < 2:
        raise ValueError("not enough valid scales to estimate fractal dimension")
    dimension = np.polyfit(np.log(inverse_scales), np.log(lengths), 1)[0]
    return float(dimension)


def absolute_return_acf_decay(values: ArrayLike, *, max_lag: int = 20) -> float:
    """Estimate exponential decay in the autocorrelation of absolute returns.

    Returns the non-negative rate ``lambda`` in ``acf(lag) ~= exp(-lambda*lag)``.
    Lower rates indicate more persistent volatility memory. Only positive empirical
    autocorrelations are used in the log-linear fit.
    """
    x = np.abs(clean_1d(values, minimum=max(20, 3 * max_lag)))
    if max_lag < 2 or max_lag >= x.size // 2:
        raise ValueError("max_lag must be between 2 and half the series length")
    centered = x - np.mean(x)
    variance = float(np.dot(centered, centered))
    if variance <= 0:
        return float("inf")
    lags = np.arange(1, max_lag + 1)
    acf = np.array(
        [np.dot(centered[:-lag], centered[lag:]) / variance for lag in lags],
        dtype=float,
    )
    mask = acf > np.finfo(float).eps
    if mask.sum() < 2:
        return float("inf")
    slope = np.polyfit(lags[mask], np.log(acf[mask]), 1)[0]
    return float(max(0.0, -slope))


def hurst_from_fractal_dimension(dimension: float) -> float:
    """Return the self-affine Hurst equivalent ``H = 2 - D``."""
    return float(2.0 - dimension)

