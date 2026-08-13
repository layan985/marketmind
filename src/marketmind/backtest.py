"""Walk-forward, cost-aware evaluation of technical indicators."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from marketmind.indicators import INDICATOR_CATEGORIES


@dataclass(frozen=True)
class EvaluationResult:
    """Regime-conditional summary plus daily audit trails."""

    summary: pd.DataFrame
    net_returns: pd.DataFrame
    positions: pd.DataFrame
    turnover: pd.DataFrame


def performance_metrics(returns: pd.Series, *, annualization: int = 252) -> dict[str, float]:
    """Compute paper-aligned return, risk, and trade-day statistics."""
    values = pd.to_numeric(returns, errors="coerce").dropna()
    if values.empty:
        return {
            name: float("nan")
            for name in (
                "average_return",
                "median_return",
                "hit_rate",
                "sharpe",
                "max_drawdown",
                "profit_factor",
                "total_return",
                "annualized_return",
                "annualized_volatility",
            )
        } | {"observations": 0.0}
    mean = float(values.mean())
    volatility = float(values.std(ddof=1))
    sharpe = mean / volatility * np.sqrt(annualization) if volatility > 0 else float("nan")
    equity = (1.0 + values).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    gains = float(values[values > 0].sum())
    losses = float(-values[values < 0].sum())
    total_return = float(equity.iloc[-1] - 1.0)
    years = len(values) / annualization
    annualized_return = (
        float((1.0 + total_return) ** (1.0 / years) - 1.0)
        if years > 0 and total_return > -1
        else -1.0
    )
    return {
        "average_return": mean,
        "median_return": float(values.median()),
        "hit_rate": float((values > 0).mean()),
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown.min()),
        "profit_factor": gains / losses if losses > 0 else float("inf"),
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": volatility * np.sqrt(annualization),
        "observations": float(len(values)),
    }


def cost_adjusted_returns(
    asset_returns: pd.Series,
    signal: pd.Series,
    *,
    cost_bps: float = 5.0,
    slippage_bps: float = 0.0,
    execution_lag: int = 1,
) -> pd.DataFrame:
    """Apply an execution lag and proportional costs to a long-only position."""
    if cost_bps < 0 or slippage_bps < 0:
        raise ValueError("cost and slippage assumptions must be non-negative")
    if execution_lag < 1:
        raise ValueError("execution_lag must be at least one session")
    returns = pd.to_numeric(asset_returns, errors="coerce").sort_index()
    observed = (
        pd.to_numeric(signal, errors="coerce").reindex(returns.index).fillna(0.0).clip(0.0, 1.0)
    )
    position = observed.shift(execution_lag).fillna(0.0)
    turnover = position.diff().abs().fillna(position.abs())
    gross = position * returns
    cost_rate = (cost_bps + slippage_bps) / 10_000.0
    net = gross - cost_rate * turnover
    return pd.DataFrame(
        {
            "asset_return": returns,
            "position": position,
            "turnover": turnover,
            "gross": gross,
            "net": net,
        }
    )


class WalkForwardEvaluator:
    """Evaluate pre-specified signals with one-step execution and rolling regimes."""

    def __init__(
        self,
        *,
        cost_bps: float = 5.0,
        slippage_bps: float = 0.0,
        execution_lag: int = 1,
        annualization: int = 252,
    ) -> None:
        self.cost_bps = cost_bps
        self.slippage_bps = slippage_bps
        self.execution_lag = execution_lag
        self.annualization = annualization

    def evaluate(
        self,
        asset_returns: pd.Series,
        signals: pd.DataFrame,
        *,
        regimes: pd.Series | None = None,
    ) -> EvaluationResult:
        """Evaluate every signal overall and within known-at-decision-time regimes."""
        if not isinstance(signals, pd.DataFrame) or signals.empty:
            raise ValueError("signals must be a non-empty DataFrame")
        returns = pd.to_numeric(asset_returns, errors="coerce").sort_index()
        net_returns = pd.DataFrame(index=returns.index)
        positions = pd.DataFrame(index=returns.index)
        turnover = pd.DataFrame(index=returns.index)
        records: list[dict[str, object]] = []

        if regimes is not None:
            known_regime = regimes.reindex(returns.index).shift(self.execution_lag)
        else:
            known_regime = pd.Series("all", index=returns.index, dtype="object")

        for name in signals.columns:
            audit = cost_adjusted_returns(
                returns,
                signals[name],
                cost_bps=self.cost_bps,
                slippage_bps=self.slippage_bps,
                execution_lag=self.execution_lag,
            )
            net_returns[name] = audit["net"]
            positions[name] = audit["position"]
            turnover[name] = audit["turnover"]
            labels = ["all"]
            if regimes is not None:
                labels.extend(str(value) for value in pd.unique(known_regime.dropna()))
            for label in labels:
                mask = (
                    pd.Series(True, index=returns.index)
                    if label == "all"
                    else known_regime.astype("string") == label
                )
                # Preserve flat days so daily Sharpe and drawdown are not inflated by
                # conditioning on the strategy being active.
                selected = audit.loc[mask, "net"]
                metrics = performance_metrics(selected, annualization=self.annualization)
                records.append(
                    {
                        "signal": name,
                        "category": INDICATOR_CATEGORIES.get(name, "custom"),
                        "regime": label,
                        "trades": float((audit.loc[mask, "position"].diff() > 0).sum()),
                        "exposure": float(audit.loc[mask, "position"].mean()),
                        **metrics,
                    }
                )
        summary = pd.DataFrame.from_records(records).set_index(["signal", "regime"]).sort_index()
        return EvaluationResult(summary, net_returns, positions, turnover)
