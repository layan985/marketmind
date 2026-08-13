import numpy as np
import pandas as pd
import pytest

from marketmind.indicators import INDICATOR_CATEGORIES
from marketmind.study import (
    ConfirmatoryMarketResult,
    confirmatory_market_returns,
    family_exposures,
    holm_adjust,
    mechanism_block_bootstrap,
    paired_sharpe_block_bootstrap,
    strategy_exposures,
)


def fixed_signals(index: pd.Index) -> pd.DataFrame:
    values = {
        "trend": (1.0, 1.0, 1.0),
        "breakout": (1.0, 0.0, 0.0),
        "mean_reversion": (0.0, 0.0, 0.0),
    }
    offsets = {family: 0 for family in values}
    signals = pd.DataFrame(index=index)
    for name, family in INDICATOR_CATEGORIES.items():
        signals[name] = values[family][offsets[family]]
        offsets[family] += 1
    return signals


def result_from_returns(
    net_returns: pd.DataFrame, regimes: pd.Series | None = None
) -> ConfirmatoryMarketResult:
    index = net_returns.index
    return ConfirmatoryMarketResult(
        exposures=pd.DataFrame(index=index),
        net_returns=net_returns,
        positions=pd.DataFrame(index=index),
        turnover=pd.DataFrame(index=index),
        realized_regime=(
            regimes if regimes is not None else pd.Series("high", index=index, dtype="string")
        ),
    )


def test_family_and_strategy_exposure_contract() -> None:
    index = pd.bdate_range("2024-01-01", periods=12)
    signals = fixed_signals(index)
    regimes = pd.Series(np.resize(["high", "medium", "low"], len(index)), index=index)
    families = family_exposures(signals)
    assert families.iloc[0].to_dict() == pytest.approx(
        {"trend": 1.0, "breakout": 1 / 3, "mean_reversion": 0.0}
    )
    exposures = strategy_exposures(signals, regimes)
    expected = regimes.map({"high": 1.0, "medium": 1 / 3, "low": 0.0})
    pd.testing.assert_series_equal(
        exposures["regime_aware"], expected.astype(float), check_names=False
    )
    with pytest.raises(ValueError):
        family_exposures(signals.drop(columns="sma_50_200"))


def test_confirmatory_market_returns_applies_one_shared_lag() -> None:
    index = pd.bdate_range("2024-01-01", periods=30)
    signals = fixed_signals(index)
    regimes = pd.Series("high", index=index)
    returns = pd.Series(0.01, index=index)
    result = confirmatory_market_returns(returns, signals, regimes, cost_bps=10)
    assert result.positions.loc[index[0], "regime_aware"] == 0.0
    assert result.positions.loc[index[1], "regime_aware"] == 1.0
    assert result.net_returns.loc[index[1], "regime_aware"] == pytest.approx(0.009)
    assert result.realized_regime.iloc[0] is pd.NA


def test_paired_study_bootstrap_detects_positive_sharpe_difference() -> None:
    rng = np.random.default_rng(90)
    index = pd.bdate_range("2024-01-01", periods=600)
    results: dict[str, ConfirmatoryMarketResult] = {}
    for number in range(4):
        noise = rng.normal(0.0, 0.01, len(index))
        frame = pd.DataFrame({"regime_aware": noise + 0.0015, "unconditional": noise}, index=index)
        results[f"market_{number}"] = result_from_returns(frame)
    comparison = paired_sharpe_block_bootstrap(
        results, n_bootstrap=200, block_size=20, random_state=91
    )
    assert comparison.estimate > 0
    assert comparison.lower > 0
    assert comparison.supported
    assert list(comparison.market_estimates.index) == [f"market_{number}" for number in range(4)]


def test_mechanism_bootstrap_and_holm_correction() -> None:
    rng = np.random.default_rng(92)
    index = pd.bdate_range("2024-01-01", periods=900)
    labels = pd.Series(
        np.resize(["high", "medium", "low"], len(index)), index=index, dtype="string"
    )
    results: dict[str, ConfirmatoryMarketResult] = {}
    for number in range(4):
        frame = pd.DataFrame(index=index)
        for family, target in (
            ("trend", "high"),
            ("breakout", "medium"),
            ("mean_reversion", "low"),
        ):
            frame[family] = rng.normal(0.0, 0.001, len(index)) + np.where(
                labels == target, 0.004, -0.001
            )
        results[f"market_{number}"] = result_from_returns(frame, labels)
    summary = mechanism_block_bootstrap(results, n_bootstrap=200, block_size=20, random_state=93)
    assert summary["supported"].all()
    assert (summary["holm_pvalue"] >= summary["pvalue"]).all()
    adjusted = holm_adjust(pd.Series({"a": 0.01, "b": 0.03, "c": 0.20}))
    assert adjusted.between(0, 1).all()
