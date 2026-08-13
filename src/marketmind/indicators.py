"""Fixed, classical indicator definitions from the paper's Figure 13."""

from __future__ import annotations

import numpy as np
import pandas as pd

INDICATOR_CATEGORIES: dict[str, str] = {
    "sma_50_200": "trend",
    "ma_100_slope": "trend",
    "price_above_ema_100": "trend",
    "rsi_14_reversion": "mean_reversion",
    "bollinger_reversal": "mean_reversion",
    "three_day_reversal": "mean_reversion",
    "breakout_20": "breakout",
    "donchian_20": "breakout",
    "atr_expansion": "breakout",
}


def _series(values: pd.Series, name: str = "close") -> pd.Series:
    if not isinstance(values, pd.Series):
        raise TypeError(f"{name} must be a pandas Series")
    result = pd.to_numeric(values, errors="coerce").sort_index()
    if result.dropna().empty:
        raise ValueError(f"{name} contains no numeric observations")
    return result.astype(float)


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder-style relative strength index."""
    price = _series(close)
    delta = price.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    relative_strength = gain / loss.replace(0.0, np.nan)
    result = 100.0 - 100.0 / (1.0 + relative_strength)
    return result.where(loss != 0, 100.0).rename("rsi")


def _entry_exit_position(entry: pd.Series, exit_: pd.Series) -> pd.Series:
    state = 0.0
    values: list[float] = []
    for enter, leave in zip(entry.fillna(False), exit_.fillna(False), strict=True):
        if state == 0.0 and bool(enter):
            state = 1.0
        elif state == 1.0 and bool(leave):
            state = 0.0
        values.append(state)
    return pd.Series(values, index=entry.index, dtype=float)


def sma_crossover(close: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    """Long while the fast simple moving average exceeds the slow average."""
    price = _series(close)
    fast_ma = price.rolling(fast).mean()
    slow_ma = price.rolling(slow).mean()
    return (fast_ma > slow_ma).astype(float).where(slow_ma.notna()).rename("sma_50_200")


def moving_average_slope(close: pd.Series, window: int = 100, lag: int = 5) -> pd.Series:
    """Long while the 100-day moving-average slope is positive."""
    average = _series(close).rolling(window).mean()
    return (average.diff(lag) > 0).astype(float).where(average.notna()).rename("ma_100_slope")


def price_above_ema(close: pd.Series, span: int = 100) -> pd.Series:
    """Long while the close exceeds EMA(100)."""
    price = _series(close)
    average = price.ewm(span=span, adjust=False, min_periods=span).mean()
    return (price > average).astype(float).where(average.notna()).rename("price_above_ema_100")


def rsi_reversion(close: pd.Series, period: int = 14) -> pd.Series:
    """Enter below RSI 30 and exit above RSI 50."""
    oscillator = rsi(close, period)
    return (
        _entry_exit_position(oscillator < 30, oscillator > 50)
        .where(oscillator.notna())
        .rename("rsi_14_reversion")
    )


def bollinger_reversal(close: pd.Series, window: int = 20, deviations: float = 2.0) -> pd.Series:
    """Enter at the lower two-sigma band and exit at the center line."""
    price = _series(close)
    center = price.rolling(window).mean()
    width = price.rolling(window).std(ddof=1)
    position = _entry_exit_position(price <= center - deviations * width, price >= center)
    return position.where(center.notna()).rename("bollinger_reversal")


def three_day_reversal(close: pd.Series) -> pd.Series:
    """Emit a one-session long signal after three consecutive down closes."""
    down = _series(close).diff() < 0
    trigger = down & down.shift(1, fill_value=False) & down.shift(2, fill_value=False)
    return trigger.astype(float).rename("three_day_reversal")


def breakout(close: pd.Series, window: int = 20) -> pd.Series:
    """Emit a one-session long signal when price exceeds the prior 20-day high."""
    price = _series(close)
    prior_high = price.shift(1).rolling(window).max()
    return (price > prior_high).astype(float).where(prior_high.notna()).rename("breakout_20")


def donchian(close: pd.Series, window: int = 20) -> pd.Series:
    """Enter above the prior Donchian high and exit below the prior Donchian low."""
    price = _series(close)
    upper = price.shift(1).rolling(window).max()
    lower = price.shift(1).rolling(window).min()
    position = _entry_exit_position(price > upper, price < lower)
    return position.where(upper.notna()).rename("donchian_20")


def average_true_range(
    close: pd.Series,
    high: pd.Series | None = None,
    low: pd.Series | None = None,
    period: int = 14,
) -> pd.Series:
    """Compute Wilder ATR, with absolute close changes as a documented fallback."""
    price = _series(close)
    if high is None or low is None:
        true_range = price.diff().abs()
    else:
        high_values = _series(high, "high").reindex(price.index)
        low_values = _series(low, "low").reindex(price.index)
        previous = price.shift(1)
        true_range = pd.concat(
            [
                high_values - low_values,
                (high_values - previous).abs(),
                (low_values - previous).abs(),
            ],
            axis=1,
        ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean().rename("atr")


def atr_expansion(
    close: pd.Series,
    high: pd.Series | None = None,
    low: pd.Series | None = None,
    *,
    period: int = 14,
    average_window: int = 20,
    multiple: float = 1.5,
) -> pd.Series:
    """Long when ATR(14) exceeds 1.5 times its 20-day average."""
    atr = average_true_range(close, high, low, period)
    average = atr.rolling(average_window).mean()
    return (atr > multiple * average).astype(float).where(average.notna()).rename("atr_expansion")


def all_signals(
    close: pd.Series, *, high: pd.Series | None = None, low: pd.Series | None = None
) -> pd.DataFrame:
    """Return all nine fixed, long-only indicator positions."""
    signals = [
        sma_crossover(close),
        moving_average_slope(close),
        price_above_ema(close),
        rsi_reversion(close),
        bollinger_reversal(close),
        three_day_reversal(close),
        breakout(close),
        donchian(close),
        atr_expansion(close, high, low),
    ]
    return pd.concat(signals, axis=1)
