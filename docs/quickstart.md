# Quickstart

## Install

```bash
pip install marketmind
```

## Estimate MII without external data

```python
from marketmind import MarketMind, MarketMindConfig
from marketmind.synthetic import synthetic_market

prices = synthetic_market(periods=1500, assets=8, seed=42)
model = MarketMind(MarketMindConfig(window=252, step=21))
result = model.fit_transform(
    prices[["SPX", "NDX", "SX5E", "ES"]],
    network_data=prices,
)

result.to_frame().tail()
```

`MIIResult` retains every transformation layer:

```python
result.raw_metrics          # physical/raw estimator outputs
result.normalized_metrics   # [0,1] submetrics
result.components           # memory, information, connectivity
result.mii                  # weighted composite
result.regimes              # thresholds and low/medium/high labels
result.metadata()           # serializable configuration
```

## Use a CSV

The wide schema has a `date` column followed by positive close-price columns:

```bash
marketmind run prices.csv --output artifacts/run
```

For a paper-style frozen development scaler:

```bash
marketmind run prices.csv \
  --output artifacts/paper \
  --development-end 2014-12-31
```

## Evaluate the nine indicators

```python
from marketmind.backtest import WalkForwardEvaluator
from marketmind.indicators import all_signals

signals = all_signals(prices["SPX"])
report = WalkForwardEvaluator(cost_bps=5, slippage_bps=1).evaluate(
    prices["SPX"].pct_change(),
    signals,
    regimes=result.regimes["regime"],
)

report.summary.xs("high", level="regime")
```

Signals are observed at a close and applied no earlier than the next session. Reported
returns therefore respect an explicit execution lag.

## Execute the preregistered strategy contract

```python
from marketmind import confirmatory_market_returns

study_market = confirmatory_market_returns(
    prices["SPX"].pct_change(),
    signals,
    result.regimes["regime"],
    cost_bps=5,
    execution_lag=1,
)

study_market.net_returns[["regime_aware", "unconditional", "buy_and_hold"]]
```

Use `paired_sharpe_block_bootstrap` on a mapping of market names to
`ConfirmatoryMarketResult` objects for the preregistered H1/H3 study-level comparison.
Use `mechanism_block_bootstrap` for H2a–H2c and Holm-corrected family-wise inference.

## Run the controlled audit

```bash
marketmind audit --output artifacts/research-audit
```

The audit is a controlled implementation test, not a performance backtest. It writes
human- and machine-readable results plus hash manifests and fails closed when an
acceptance rule is violated.
