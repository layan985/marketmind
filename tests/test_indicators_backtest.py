import numpy as np
import pandas as pd
import pytest

from marketmind.backtest import WalkForwardEvaluator, cost_adjusted_returns, performance_metrics
from marketmind.indicators import INDICATOR_CATEGORIES, all_signals, rsi
from marketmind.statistics import regime_tests


def price_series(rows: int = 500) -> pd.Series:
    rng = np.random.default_rng(20)
    returns = 0.0003 + rng.normal(scale=0.01, size=rows)
    return pd.Series(
        100 * np.exp(np.cumsum(returns)),
        index=pd.bdate_range("2020-01-01", periods=rows),
        name="close",
    )


def test_all_nine_signals_are_available() -> None:
    close = price_series()
    signals = all_signals(close)
    assert set(signals.columns) == set(INDICATOR_CATEGORIES)
    assert signals.shape == (len(close), 9)
    assert rsi(close).dropna().between(0, 100).all()


def test_costs_and_execution_lag() -> None:
    returns = pd.Series([0.0, 0.10, -0.05, 0.02])
    signal = pd.Series([1.0, 1.0, 0.0, 0.0])
    audit = cost_adjusted_returns(returns, signal, cost_bps=10)
    assert audit.loc[0, "position"] == 0
    assert audit.loc[1, "position"] == 1
    assert audit.loc[1, "net"] == pytest.approx(0.099)
    assert audit.loc[3, "position"] == 0
    with pytest.raises(ValueError):
        cost_adjusted_returns(returns, signal, execution_lag=0)


def test_walk_forward_evaluator_and_metrics() -> None:
    close = price_series()
    returns = close.pct_change()
    signals = all_signals(close).iloc[:, :3]
    regimes = pd.Series(
        np.resize(["low", "medium", "high"], len(close)), index=close.index, dtype="object"
    )
    result = WalkForwardEvaluator(cost_bps=5).evaluate(returns, signals, regimes=regimes)
    assert set(result.summary.index.get_level_values("regime")) == {"all", "low", "medium", "high"}
    assert result.net_returns.shape[1] == 3
    metrics = performance_metrics(result.net_returns.iloc[:, 0])
    assert "sharpe" in metrics and metrics["observations"] > 0


def test_regime_statistical_tests() -> None:
    rng = np.random.default_rng(21)
    returns = pd.Series(np.r_[rng.normal(-1, 1, 80), rng.normal(0, 1, 80), rng.normal(1, 1, 80)])
    regimes = pd.Series(np.repeat(["low", "medium", "high"], 80))
    tests = regime_tests(returns, regimes)
    assert tests["kruskal_pvalue"] < 0.01

