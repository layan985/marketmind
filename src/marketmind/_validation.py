"""Shared input validation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray


def clean_1d(values: ArrayLike, *, minimum: int = 4, name: str = "series") -> NDArray[np.float64]:
    """Return a finite one-dimensional float array or raise a useful error."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    array = array[np.isfinite(array)]
    if array.size < minimum:
        raise ValueError(f"{name} must contain at least {minimum} finite observations")
    if np.all(array == array[0]):
        raise ValueError(f"{name} must not be constant")
    return array.astype(np.float64, copy=False)


def aligned_pair(
    x: ArrayLike, y: ArrayLike, *, minimum: int = 8
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Drop pairwise non-finite observations from two equally sized vectors."""
    x_array = np.asarray(x, dtype=float)
    y_array = np.asarray(y, dtype=float)
    if x_array.ndim != 1 or y_array.ndim != 1:
        raise ValueError("x and y must be one-dimensional")
    if x_array.size != y_array.size:
        raise ValueError("x and y must have equal length")
    mask = np.isfinite(x_array) & np.isfinite(y_array)
    x_clean, y_clean = x_array[mask], y_array[mask]
    if x_clean.size < minimum:
        raise ValueError(f"x and y must have at least {minimum} aligned observations")
    return x_clean.astype(float), y_clean.astype(float)


def validate_frame(frame: pd.DataFrame, *, minimum_columns: int = 1) -> pd.DataFrame:
    """Validate and sort a numeric, unique-indexed time-series frame."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if frame.shape[1] < minimum_columns:
        raise ValueError(f"data must contain at least {minimum_columns} columns")
    if frame.index.has_duplicates:
        raise ValueError("data index must not contain duplicate timestamps")
    result = frame.sort_index().apply(pd.to_numeric, errors="coerce")
    if result.dropna(how="all").empty:
        raise ValueError("data contains no numeric observations")
    return result.astype(float)

