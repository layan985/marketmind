"""Cost sweeps, naive baselines, bootstrap checks, and Sharpe deflation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, norm, skew

from marketmind.backtest import WalkForwardEvaluator, performance_metrics


@dataclass(frozen=True)
class RealityCheckResult:
    """White-style bootstrap reality-check output."""

    observed_statistic: float
    pvalue: float
    bootstrap_statistics: np.ndarray


def naive_baselines(
    asset_returns: pd.Series,
    reference_signal: pd.Series,
    *,
    random_state: int = 0,
) -> pd.DataFrame:
    """Return buy-and-hold, cash, lag-momentum, and exposure-matched shuffle signals."""
    returns = pd.to_numeric(asset_returns, errors="coerce").sort_index()
    reference = pd.to_numeric(reference_signal, errors="coerce").reindex(returns.index).fillna(0.0)
    rng = np.random.default_rng(random_state)
    shuffled = reference.to_numpy(copy=True)
    rng.shuffle(shuffled)
    return pd.DataFrame(
        {
            "buy_and_hold": 1.0,
            "cash": 0.0,
            "lagged_sign": (returns > 0).astype(float),
            "exposure_matched_shuffle": shuffled,
        },
        index=returns.index,
    )


def transaction_cost_sweep(
    asset_returns: pd.Series,
    signals: pd.DataFrame,
    costs_bps: Iterable[float] = (0.0, 5.0, 10.0, 25.0),
) -> pd.DataFrame:
    """Re-evaluate signals across proportional transaction-cost assumptions."""
    records: list[dict[str, object]] = []
    for cost in costs_bps:
        result = WalkForwardEvaluator(cost_bps=float(cost)).evaluate(asset_returns, signals)
        overall = result.summary.xs("all", level="regime")
        for signal, row in overall.iterrows():
            records.append(
                {
                    "cost_bps": float(cost),
                    "signal": signal,
                    "sharpe": float(row["sharpe"]),
                    "total_return": float(row["total_return"]),
                    "max_drawdown": float(row["max_drawdown"]),
                }
            )
    return pd.DataFrame.from_records(records).set_index(["cost_bps", "signal"])


def block_bootstrap_interval(
    returns: pd.Series,
    *,
    statistic: str = "sharpe",
    block_size: int = 20,
    n_bootstrap: int = 1_000,
    confidence: float = 0.95,
    random_state: int = 0,
) -> tuple[float, float]:
    """Moving-block bootstrap interval for a performance statistic."""
    values = pd.to_numeric(returns, errors="coerce").dropna().to_numpy()
    if not 1 <= block_size <= len(values):
        raise ValueError("block_size must be between one and the sample length")
    if n_bootstrap < 100 or not 0 < confidence < 1:
        raise ValueError("n_bootstrap must be >=100 and confidence must lie in (0,1)")
    rng = np.random.default_rng(random_state)
    starts = np.arange(len(values) - block_size + 1)
    estimates = np.empty(n_bootstrap)
    needed = int(np.ceil(len(values) / block_size))
    for iteration in range(n_bootstrap):
        chosen = rng.choice(starts, size=needed, replace=True)
        sample = np.concatenate([values[start : start + block_size] for start in chosen])[: len(values)]
        metrics = performance_metrics(pd.Series(sample))
        if statistic not in metrics:
            raise ValueError(f"unknown performance statistic: {statistic}")
        estimates[iteration] = metrics[statistic]
    alpha = (1.0 - confidence) / 2.0
    return float(np.nanquantile(estimates, alpha)), float(np.nanquantile(estimates, 1.0 - alpha))


def white_reality_check(
    strategy_returns: pd.DataFrame,
    *,
    block_size: int = 20,
    n_bootstrap: int = 1_000,
    random_state: int = 0,
) -> RealityCheckResult:
    """Bootstrap whether the best tested strategy beats a zero-return benchmark."""
    frame = strategy_returns.apply(pd.to_numeric, errors="coerce").dropna(how="any")
    if frame.empty or len(frame) < block_size:
        raise ValueError("insufficient complete strategy-return observations")
    values = frame.to_numpy()
    n = len(values)
    observed = float(np.sqrt(n) * np.max(np.mean(values, axis=0)))
    centered = values - np.mean(values, axis=0, keepdims=True)
    starts = np.arange(n - block_size + 1)
    blocks_needed = int(np.ceil(n / block_size))
    rng = np.random.default_rng(random_state)
    statistics = np.empty(n_bootstrap)
    for iteration in range(n_bootstrap):
        chosen = rng.choice(starts, size=blocks_needed, replace=True)
        sample = np.concatenate([centered[start : start + block_size] for start in chosen], axis=0)[:n]
        statistics[iteration] = np.sqrt(n) * np.max(np.mean(sample, axis=0))
    pvalue = float((1 + np.sum(statistics >= observed)) / (n_bootstrap + 1))
    return RealityCheckResult(observed, pvalue, statistics)


def deflated_sharpe_probability(
    returns: pd.Series,
    *,
    n_trials: int,
    annualization: int = 252,
) -> float:
    """Approximate probability that Sharpe exceeds the multiple-testing benchmark."""
    values = pd.to_numeric(returns, errors="coerce").dropna().to_numpy()
    if len(values) < 3 or n_trials < 1:
        raise ValueError("at least three returns and one trial are required")
    daily_std = float(np.std(values, ddof=1))
    if daily_std == 0:
        return 0.0
    observed = float(np.mean(values) / daily_std)
    euler_gamma = 0.5772156649015329
    variance_sr = 1.0 / max(2, len(values) - 1)
    if n_trials == 1:
        expected_max = 0.0
    else:
        expected_max = np.sqrt(variance_sr) * (
            (1 - euler_gamma) * norm.ppf(1 - 1 / n_trials)
            + euler_gamma * norm.ppf(1 - 1 / (n_trials * np.e))
        )
    skewness = float(skew(values, bias=False))
    kurt = float(kurtosis(values, fisher=False, bias=False))
    denominator = np.sqrt(
        max(1e-12, 1.0 - skewness * observed + (kurt - 1.0) * observed**2 / 4.0)
    )
    statistic = (observed - expected_max) * np.sqrt(len(values) - 1) / denominator
    # Annualization cancels because both observed and benchmark are daily, retained for API clarity.
    _ = annualization
    return float(norm.cdf(statistic))

