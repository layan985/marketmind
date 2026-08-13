"""Deterministic synthetic data for examples, tests, and offline demos."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SyntheticScenario:
    """Synthetic prices plus the latent process used to generate them."""

    prices: pd.DataFrame
    latent: pd.DataFrame
    seed: int


def synthetic_market_scenario(
    *,
    periods: int = 1_500,
    assets: int = 8,
    start: str = "2018-01-02",
    seed: int = 42,
) -> SyntheticScenario:
    """Generate prices and disclosed latent states for controlled validation.

    The generator is not a calibrated market simulator. It deliberately alternates
    between coherent, transitional, and disordered states so every package component
    can be exercised without proprietary data. ``latent`` exposes the exact coherence,
    volatility, drift, and persistence paths; this supports construct-validity checks
    without pretending that synthetic performance is market evidence.
    """
    if periods < 100 or assets < 2:
        raise ValueError("periods must be >=100 and assets must be >=2")
    rng = np.random.default_rng(seed)
    index = pd.bdate_range(start, periods=periods)
    cycle = np.arange(periods) % 600
    coherence = np.where(cycle < 250, 0.80, np.where(cycle < 400, 0.45, 0.15))
    volatility = np.where(cycle < 250, 0.007, np.where(cycle < 400, 0.011, 0.020))
    drift = np.where(cycle < 250, 0.00035, np.where(cycle < 400, 0.00005, -0.00010))
    persistence_path = np.where(coherence > 0.6, 0.12, np.where(coherence < 0.2, -0.08, 0.0))
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
            returns[row, column] += persistence_path[row] * returns[row - 1, column]
    prices = 100.0 * np.exp(np.cumsum(returns, axis=0))
    names = ["SPX", "NDX", "SX5E", "ES", "XLK", "XLF", "XLV", "XLE"][:assets]
    if assets > len(names):
        names.extend(f"ASSET_{number:02d}" for number in range(len(names) + 1, assets + 1))
    price_frame = pd.DataFrame(prices, index=index, columns=names).rename_axis("date")
    phase = np.where(cycle < 250, "coherent", np.where(cycle < 400, "transitional", "disordered"))
    latent = pd.DataFrame(
        {
            "phase": phase,
            "coherence": coherence,
            "volatility": volatility,
            "drift": drift,
            "return_persistence": persistence_path,
        },
        index=index,
    ).rename_axis("date")
    return SyntheticScenario(prices=price_frame, latent=latent, seed=seed)


def synthetic_market(
    *,
    periods: int = 1_500,
    assets: int = 8,
    start: str = "2018-01-02",
    seed: int = 42,
) -> pd.DataFrame:
    """Return the deterministic synthetic price panel used by demos and tests."""
    return synthetic_market_scenario(
        periods=periods,
        assets=assets,
        start=start,
        seed=seed,
    ).prices
