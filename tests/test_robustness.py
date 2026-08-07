import numpy as np
import pandas as pd

from marketmind.robustness import (
    block_bootstrap_interval,
    deflated_sharpe_probability,
    naive_baselines,
    transaction_cost_sweep,
    white_reality_check,
)


def test_baselines_cost_sweep_and_bootstrap() -> None:
    rng = np.random.default_rng(40)
    index = pd.bdate_range("2020-01-01", periods=400)
    returns = pd.Series(rng.normal(0.0004, 0.01, 400), index=index)
    signal = pd.Series((rng.random(400) > 0.5).astype(float), index=index)
    baselines = naive_baselines(returns, signal)
    assert list(baselines) == ["buy_and_hold", "cash", "lagged_sign", "exposure_matched_shuffle"]
    sweep = transaction_cost_sweep(returns, baselines[["buy_and_hold", "lagged_sign"]], [0, 10])
    assert len(sweep) == 4
    lower, upper = block_bootstrap_interval(returns, n_bootstrap=100, block_size=10)
    assert lower <= upper


def test_reality_check_and_deflated_sharpe() -> None:
    rng = np.random.default_rng(41)
    returns = pd.DataFrame(
        {
            "noise": rng.normal(0, 0.01, 300),
            "edge": rng.normal(0.001, 0.01, 300),
        }
    )
    result = white_reality_check(returns, n_bootstrap=100, block_size=10)
    assert 0 <= result.pvalue <= 1
    assert len(result.bootstrap_statistics) == 100
    probability = deflated_sharpe_probability(returns["edge"], n_trials=9)
    assert 0 <= probability <= 1

