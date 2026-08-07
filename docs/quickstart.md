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
