"""Information-theoretic estimators for financial time series."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.spatial import cKDTree
from scipy.special import digamma

from marketmind._validation import aligned_pair


def shannon_entropy(values: ArrayLike, *, bins: int = 20, normalize: bool = False) -> float:
    """Estimate histogram-based Shannon entropy in bits.

    The baseline uses 20 equal-width bins within the supplied window, matching
    Equation A.7. Set ``normalize=True`` to divide by ``log2(bins)``.
    """
    x = np.asarray(values, dtype=float)
    if x.ndim != 1:
        raise ValueError("values must be one-dimensional")
    x = x[np.isfinite(x)]
    if x.size < 2:
        raise ValueError("values must contain at least two finite observations")
    if bins < 2:
        raise ValueError("bins must be at least 2")
    if np.all(x == x[0]):
        return 0.0
    counts, _ = np.histogram(x, bins=bins)
    probabilities = counts[counts > 0] / counts.sum()
    entropy = float(-np.sum(probabilities * np.log2(probabilities)))
    if normalize:
        entropy /= float(np.log2(bins))
    return entropy


def _matrix(values: ArrayLike) -> NDArray[np.float64]:
    array = np.asarray(values, dtype=float)
    if array.ndim == 1:
        array = array[:, None]
    if array.ndim != 2:
        raise ValueError("estimator inputs must be one- or two-dimensional")
    return array


def _prepare_knn(*arrays: NDArray[np.float64]) -> tuple[NDArray[np.float64], ...]:
    if len({array.shape[0] for array in arrays}) != 1:
        raise ValueError("all estimator inputs must have equal row counts")
    combined = np.column_stack(arrays)
    mask = np.isfinite(combined).all(axis=1)
    cleaned = combined[mask]
    if cleaned.shape[0] < 8:
        raise ValueError("at least eight complete observations are required")
    scale = np.std(cleaned, axis=0, ddof=1)
    scale[~np.isfinite(scale) | (scale == 0)] = 1.0
    standardized = (cleaned - np.mean(cleaned, axis=0)) / scale
    # Deterministic micro-jitter resolves distance ties without affecting scale.
    rng = np.random.default_rng(0)
    standardized += rng.normal(0.0, 1e-10, standardized.shape)
    widths = [array.shape[1] for array in arrays]
    split_at = np.cumsum(widths)[:-1]
    return tuple(np.split(standardized, split_at, axis=1))


def _neighbor_counts(points: NDArray[np.float64], radii: NDArray[np.float64]) -> NDArray[np.int64]:
    tree = cKDTree(points)
    counts = tree.query_ball_point(points, radii, p=np.inf, return_length=True)
    return np.asarray(counts, dtype=np.int64) - 1


def mutual_information(x: ArrayLike, y: ArrayLike, *, k: int = 3) -> float:
    """Estimate continuous mutual information with the Kraskov KSG estimator.

    The result is in nats. ``x`` and ``y`` may each be univariate or multivariate.
    """
    x_array, y_array = _prepare_knn(_matrix(x), _matrix(y))
    n = x_array.shape[0]
    if not 1 <= k < n:
        raise ValueError("k must be positive and smaller than the sample size")
    joint = np.column_stack([x_array, y_array])
    distances = cKDTree(joint).query(joint, k=k + 1, p=np.inf)[0][:, k]
    radii = np.nextafter(distances, 0.0)
    nx = _neighbor_counts(x_array, radii)
    ny = _neighbor_counts(y_array, radii)
    estimate = digamma(k) + digamma(n) - np.mean(digamma(nx + 1) + digamma(ny + 1))
    return float(max(0.0, estimate))


def conditional_mutual_information(
    x: ArrayLike, y: ArrayLike, z: ArrayLike, *, k: int = 3
) -> float:
    """Estimate ``I(X;Y|Z)`` with a nearest-neighbor estimator in nats."""
    x_array, y_array, z_array = _prepare_knn(_matrix(x), _matrix(y), _matrix(z))
    n = x_array.shape[0]
    if not 1 <= k < n:
        raise ValueError("k must be positive and smaller than the sample size")
    xyz = np.column_stack([x_array, y_array, z_array])
    distances = cKDTree(xyz).query(xyz, k=k + 1, p=np.inf)[0][:, k]
    radii = np.nextafter(distances, 0.0)
    nxz = _neighbor_counts(np.column_stack([x_array, z_array]), radii)
    nyz = _neighbor_counts(np.column_stack([y_array, z_array]), radii)
    nz = _neighbor_counts(z_array, radii)
    estimate = digamma(k) + np.mean(digamma(nz + 1) - digamma(nxz + 1) - digamma(nyz + 1))
    return float(max(0.0, estimate))


def transfer_entropy(
    source: ArrayLike,
    target: ArrayLike,
    *,
    k: int = 3,
    source_history: int = 1,
    target_history: int = 1,
    source_lag: int = 1,
) -> float:
    """Estimate directional transfer entropy ``source -> target`` in nats.

    Transfer entropy is implemented as conditional mutual information between the
    source history and the next target observation, conditional on the target's own
    history. The paper's baseline is ``k=3``; ``k=3..5`` is used for sensitivity.
    """
    x, y = aligned_pair(source, target, minimum=12)
    if min(source_history, target_history, source_lag) < 1:
        raise ValueError("history lengths and source_lag must be positive")
    start = max(source_lag + source_history - 1, target_history)
    if x.size - start < max(8, k + 2):
        raise ValueError("series is too short for the requested embedding")

    target_future = y[start:, None]
    source_past = np.column_stack(
        [
            x[start - source_lag - offset : x.size - source_lag - offset]
            for offset in range(source_history)
        ]
    )
    target_past = np.column_stack(
        [y[start - offset : y.size - offset] for offset in range(1, target_history + 1)]
    )
    return conditional_mutual_information(source_past, target_future, target_past, k=k)
