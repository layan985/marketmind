"""Executable construction and inference for the preregistered prospective study."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
import pandas as pd

from marketmind.backtest import cost_adjusted_returns
from marketmind.indicators import INDICATOR_CATEGORIES

FAMILY_ORDER = ("trend", "breakout", "mean_reversion")
REGIME_TO_FAMILY = {"high": "trend", "medium": "breakout", "low": "mean_reversion"}


@dataclass(frozen=True)
class ConfirmatoryMarketResult:
    """Decision-time exposures and realized net returns for one market."""

    exposures: pd.DataFrame
    net_returns: pd.DataFrame
    positions: pd.DataFrame
    turnover: pd.DataFrame
    realized_regime: pd.Series


@dataclass(frozen=True)
class BootstrapComparison:
    """Study-level paired Sharpe comparison with a moving-block interval."""

    estimate: float
    lower: float
    upper: float
    pvalue: float
    confidence: float
    block_size: int
    n_bootstrap: int
    market_estimates: pd.Series
    bootstrap_estimates: np.ndarray

    @property
    def supported(self) -> bool:
        """Return whether the directional effect has a strictly positive interval."""
        return bool(self.estimate > 0.0 and self.lower > 0.0)


def family_exposures(signals: pd.DataFrame) -> pd.DataFrame:
    """Average the three fixed signals in each preregistered family.

    Rows remain missing until all three constituent signals in a family are available;
    partial warm-up rows are never silently treated as a complete family.
    """
    if not isinstance(signals, pd.DataFrame) or signals.empty:
        raise ValueError("signals must be a non-empty DataFrame")
    required = list(INDICATOR_CATEGORIES)
    missing = set(required) - set(signals.columns)
    if missing:
        raise ValueError(f"signals are missing preregistered definitions: {sorted(missing)}")
    numeric = signals[required].apply(pd.to_numeric, errors="coerce")
    result = pd.DataFrame(index=numeric.index)
    for family in FAMILY_ORDER:
        members = [name for name, category in INDICATOR_CATEGORIES.items() if category == family]
        result[family] = numeric[members].mean(axis=1, skipna=False)
    return result


def strategy_exposures(signals: pd.DataFrame, regimes: pd.Series) -> pd.DataFrame:
    """Construct the frozen regime-aware, unconditional, and family exposures."""
    families = family_exposures(signals)
    aligned_regimes = regimes.reindex(families.index).astype("string")
    regime_aware = pd.Series(np.nan, index=families.index, dtype=float)
    for regime, family in REGIME_TO_FAMILY.items():
        mask = aligned_regimes == regime
        regime_aware.loc[mask] = families.loc[mask, family]

    required = list(INDICATOR_CATEGORIES)
    unconditional = (
        signals[required].apply(pd.to_numeric, errors="coerce").mean(axis=1, skipna=False)
    )
    return families.assign(
        regime_aware=regime_aware,
        unconditional=unconditional,
        buy_and_hold=1.0,
    )


def confirmatory_market_returns(
    asset_returns: pd.Series,
    signals: pd.DataFrame,
    regimes: pd.Series,
    *,
    cost_bps: float = 5.0,
    slippage_bps: float = 0.0,
    execution_lag: int = 1,
) -> ConfirmatoryMarketResult:
    """Execute every frozen exposure for one market with identical timing and costs."""
    returns = pd.to_numeric(asset_returns, errors="coerce").sort_index()
    aligned_signals = signals.reindex(returns.index)
    exposures = strategy_exposures(aligned_signals, regimes.reindex(returns.index))
    net_returns = pd.DataFrame(index=returns.index)
    positions = pd.DataFrame(index=returns.index)
    turnover = pd.DataFrame(index=returns.index)
    for name in exposures:
        audit = cost_adjusted_returns(
            returns,
            exposures[name],
            cost_bps=cost_bps,
            slippage_bps=slippage_bps,
            execution_lag=execution_lag,
        )
        net_returns[name] = audit["net"]
        positions[name] = audit["position"]
        turnover[name] = audit["turnover"]
    realized_regime = regimes.reindex(returns.index).shift(execution_lag).astype("string")
    realized_regime.name = "realized_regime"
    return ConfirmatoryMarketResult(
        exposures=exposures,
        net_returns=net_returns,
        positions=positions,
        turnover=turnover,
        realized_regime=realized_regime,
    )


def _sharpe(values: np.ndarray, annualization: int) -> float:
    finite = values[np.isfinite(values)]
    if finite.size < 2:
        return float("nan")
    volatility = float(np.std(finite, ddof=1))
    if volatility <= 0:
        return float("nan")
    return float(np.mean(finite) / volatility * np.sqrt(annualization))


def _moving_block_indices(length: int, block_size: int, rng: np.random.Generator) -> np.ndarray:
    starts = np.arange(length - block_size + 1)
    blocks_needed = int(np.ceil(length / block_size))
    chosen = rng.choice(starts, size=blocks_needed, replace=True)
    return np.concatenate([np.arange(start, start + block_size) for start in chosen])[:length]


def paired_sharpe_block_bootstrap(
    results: Mapping[str, ConfirmatoryMarketResult],
    *,
    candidate: str = "regime_aware",
    comparator: str = "unconditional",
    block_size: int = 20,
    n_bootstrap: int = 10_000,
    confidence: float = 0.95,
    random_state: int = 20260807,
    annualization: int = 252,
) -> BootstrapComparison:
    """Estimate the preregistered average cross-market Sharpe difference.

    Candidate and comparator returns are resampled with identical block indices inside
    each market. Every draw then recomputes each market Sharpe and the study-level mean.
    """
    if not results:
        raise ValueError("at least one market result is required")
    if n_bootstrap < 100 or not 0 < confidence < 1:
        raise ValueError("n_bootstrap must be >=100 and confidence must lie in (0,1)")
    paired: dict[str, np.ndarray] = {}
    observed: dict[str, float] = {}
    for market, result in results.items():
        missing = {candidate, comparator} - set(result.net_returns.columns)
        if missing:
            raise ValueError(f"{market} is missing strategy returns: {sorted(missing)}")
        frame = result.net_returns[[candidate, comparator]].dropna()
        if len(frame) < block_size:
            raise ValueError(f"{market} has fewer complete rows than block_size")
        values = frame.to_numpy(dtype=float)
        paired[market] = values
        observed[market] = _sharpe(values[:, 0], annualization) - _sharpe(
            values[:, 1], annualization
        )
    market_estimates = pd.Series(observed, name="sharpe_difference", dtype=float)
    estimate = float(market_estimates.mean())
    rng = np.random.default_rng(random_state)
    draws = np.empty(n_bootstrap)
    for iteration in range(n_bootstrap):
        differences: list[float] = []
        for values in paired.values():
            indices = _moving_block_indices(len(values), block_size, rng)
            sample = values[indices]
            differences.append(
                _sharpe(sample[:, 0], annualization) - _sharpe(sample[:, 1], annualization)
            )
        draws[iteration] = float(np.nanmean(differences))
    alpha = (1.0 - confidence) / 2.0
    lower, upper = np.nanquantile(draws, [alpha, 1.0 - alpha])
    left = int(np.sum(draws <= 0.0))
    right = int(np.sum(draws >= 0.0))
    pvalue = float(min(1.0, 2.0 * (1 + min(left, right)) / (n_bootstrap + 1)))
    return BootstrapComparison(
        estimate=estimate,
        lower=float(lower),
        upper=float(upper),
        pvalue=pvalue,
        confidence=confidence,
        block_size=block_size,
        n_bootstrap=n_bootstrap,
        market_estimates=market_estimates,
        bootstrap_estimates=draws,
    )


def holm_adjust(pvalues: pd.Series) -> pd.Series:
    """Return Holm family-wise adjusted p-values with monotonicity enforced."""
    values = pd.to_numeric(pvalues, errors="raise").astype(float)
    if values.empty or values.isna().any() or not values.between(0.0, 1.0).all():
        raise ValueError("pvalues must be finite values in [0,1]")
    ordered = values.sort_values()
    running = 0.0
    total = len(ordered)
    adjusted_values: list[float] = []
    for rank, (name, value) in enumerate(ordered.items()):
        _ = name
        running = max(running, min(1.0, (total - rank) * float(value)))
        adjusted_values.append(running)
    adjusted_ordered = pd.Series(adjusted_values, index=ordered.index, dtype=float)
    return adjusted_ordered.reindex(values.index).rename("holm_pvalue")


def mechanism_block_bootstrap(
    results: Mapping[str, ConfirmatoryMarketResult],
    *,
    block_size: int = 20,
    n_bootstrap: int = 10_000,
    confidence: float = 0.95,
    random_state: int = 20260807,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Run H2a-H2c mean-return contrasts and Holm-corrected inference."""
    if not results:
        raise ValueError("at least one market result is required")
    specifications = {
        "H2a": ("trend", "high"),
        "H2b": ("breakout", "medium"),
        "H2c": ("mean_reversion", "low"),
    }
    frames: dict[str, pd.DataFrame] = {}
    for market, result in results.items():
        frame = result.net_returns[list(FAMILY_ORDER)].copy()
        frame["regime"] = result.realized_regime
        frame = frame.dropna()
        if len(frame) < block_size:
            raise ValueError(f"{market} has fewer complete rows than block_size")
        frames[market] = frame

    def contrasts(frame: pd.DataFrame) -> dict[str, float]:
        estimates: dict[str, float] = {}
        labels = frame["regime"].astype("string")
        for hypothesis, (family, target) in specifications.items():
            target_values = frame.loc[labels == target, family]
            other_values = frame.loc[labels != target, family]
            estimates[hypothesis] = (
                float(target_values.mean() - other_values.mean())
                if not target_values.empty and not other_values.empty
                else float("nan")
            )
        return estimates

    market_observed = pd.DataFrame({market: contrasts(frame) for market, frame in frames.items()})
    observed = market_observed.mean(axis=1)
    rng = np.random.default_rng(random_state)
    draws = pd.DataFrame(
        index=pd.RangeIndex(n_bootstrap), columns=list(specifications), dtype=float
    )
    for iteration in range(n_bootstrap):
        by_market: list[dict[str, float]] = []
        for frame in frames.values():
            indices = _moving_block_indices(len(frame), block_size, rng)
            by_market.append(contrasts(frame.iloc[indices]))
        draws.iloc[iteration] = pd.DataFrame(by_market).mean(axis=0)

    tail = (1.0 - confidence) / 2.0
    records: list[dict[str, object]] = []
    for hypothesis, (family, target) in specifications.items():
        values = draws[hypothesis].dropna()
        if values.empty:
            raise ValueError(f"bootstrap produced no valid {hypothesis} contrasts")
        lower, upper = values.quantile([tail, 1.0 - tail])
        left = int((values <= 0.0).sum())
        right = int((values >= 0.0).sum())
        pvalue = float(min(1.0, 2.0 * (1 + min(left, right)) / (len(values) + 1)))
        records.append(
            {
                "hypothesis": hypothesis,
                "family": family,
                "target_regime": target,
                "estimate": float(observed.loc[hypothesis]),
                "lower": float(lower),
                "upper": float(upper),
                "pvalue": pvalue,
            }
        )
    summary = pd.DataFrame.from_records(records).set_index("hypothesis")
    summary["holm_pvalue"] = holm_adjust(summary["pvalue"])
    summary["supported"] = (
        (summary["estimate"] > 0.0) & (summary["lower"] > 0.0) & (summary["holm_pvalue"] < alpha)
    )
    return summary
