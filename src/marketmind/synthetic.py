"""Deterministic synthetic data for examples, tests, and offline demos."""

from __future__ import annotations

import numpy as np
import pandas as pd


def synthetic_market(
    *,
    periods: int = 1_500,
    assets: int = 8,
    start: str = "2018-01-02",
    seed: int = 42,
) -> pd.DataFrame:
    """Generate a reproducible multi-asset price panel with changing coherence.

    The generator is not a calibrated market simulator. It deliberately alternates
    between coherent, transitional, and disordered states so every package component
    can be demonstrated without proprietary data.
    """
    if periods < 100 or assets < 2:
        raise ValueError("periods must be >=100 and assets must be >=2")
    rng = np.random.default_rng(seed)
    index = pd.bdate_range(start, periods=periods)
    cycle = np.arange(periods) % 600
    coherence = np.where(cycle < 250, 0.80, np.where(cycle < 400, 0.45, 0.15))
    volatility = np.where(cycle < 250, 0.007, np.where(cycle < 400, 0.011, 0.020))
    drift = np.where(cycle < 250, 0.00035, np.where(cycle < 400, 0.00005, -0.00010))
    factor = rng.normal(size=periods)
    innovations = rng.normal(size=(periods, assets))
    returns = np.empty_like(innovations)
    for column in range(assets):
        loading = 0.8 + 0.15 * rng.random()
        common = np.sqrt(coherence) * loading * factor
        idiosyncratic = np.sqrt(1.0 - coherence) * innovations[:, column]
        returns[:, column] = drift + volatility * (common + idiosyncratic)
        # Add mild state-dependent persistence without using future data.
        for row in range(1, periods):
            persistence = 0.12 if coherence[row] > 0.6 else (-0.08 if coherence[row] < 0.2 else 0.0)
            returns[row, column] += persistence * returns[row - 1, column]
    prices = 100.0 * np.exp(np.cumsum(returns, axis=0))
    names = ["SPX", "NDX", "SX5E", "ES", "XLK", "XLF", "XLV", "XLE"][:assets]
    if assets > len(names):
        names.extend(f"ASSET_{number:02d}" for number in range(len(names) + 1, assets + 1))
    return pd.DataFrame(prices, index=index, columns=names).rename_axis("date")

