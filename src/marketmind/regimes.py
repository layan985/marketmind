"""Causal Market Intelligence Index regime classification."""

from __future__ import annotations

import numpy as np
import pandas as pd


REGIME_ORDER = ("low", "medium", "high")


def classify_regimes(
    mii: pd.Series,
    *,
    lookback: int = 756,
    lower_quantile: float = 1 / 3,
    upper_quantile: float = 2 / 3,
    min_history: int = 252,
    monthly: bool = True,
) -> pd.DataFrame:
    """Classify low/medium/high regimes using trailing rolling terciles.

    Thresholds are learned only from observations strictly before the classified
    date. With ``monthly=True``, they are refreshed on the first observation of each
    calendar month and held fixed until the next refresh, matching the paper's
    three-year, monthly-recalibrated protocol.
    """
    if not isinstance(mii, pd.Series):
        raise TypeError("mii must be a pandas Series")
    if lookback < min_history or min_history < 2:
        raise ValueError("lookback must be at least min_history >= 2")
    if not 0 < lower_quantile < upper_quantile < 1:
        raise ValueError("quantiles must satisfy 0 < lower < upper < 1")
    values = pd.to_numeric(mii, errors="coerce").sort_index()
    output = pd.DataFrame(index=values.index, columns=["mii", "lower", "upper", "regime"])
    output["mii"] = values

    lower = upper = np.nan
    previous_month: tuple[int, int] | None = None
    for position, (date, value) in enumerate(values.items()):
        month = (date.year, date.month) if hasattr(date, "year") else None
        refresh = not monthly or month != previous_month
        if refresh:
            history = values.iloc[max(0, position - lookback) : position].dropna()
            if len(history) >= min_history:
                lower = float(history.quantile(lower_quantile))
                upper = float(history.quantile(upper_quantile))
            previous_month = month
        output.at[date, "lower"] = lower
        output.at[date, "upper"] = upper
        if not np.isfinite(value) or not np.isfinite(lower) or not np.isfinite(upper):
            regime: object = pd.NA
        elif value < lower:
            regime = "low"
        elif value > upper:
            regime = "high"
        else:
            regime = "medium"
        output.at[date, "regime"] = regime

    output[["mii", "lower", "upper"]] = output[["mii", "lower", "upper"]].astype(float)
    output["regime"] = pd.Categorical(output["regime"], categories=REGIME_ORDER, ordered=True)
    return output

