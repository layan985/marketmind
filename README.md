# MarketMind

[![CI](https://github.com/layan985/marketmind/actions/workflows/ci.yml/badge.svg)](https://github.com/layan985/marketmind/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/marketmind.svg)](https://pypi.org/project/marketmind/)
[![Python](https://img.shields.io/pypi/pyversions/marketmind.svg)](https://pypi.org/project/marketmind/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21844956.svg)](https://doi.org/10.5281/zenodo.21844956)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](LICENSE)

A market-regime test can look predictive when its normalization bounds, regime thresholds, or trading rules are chosen with knowledge of the evaluation period. MarketMind puts those choices into code so their timing can be inspected and the same rules can be run again.

The package implements the Market Intelligence Index (MII) from my 2026 Charles H. Dow Award paper, *The Emergent Market Mind*. The paper argues that market organization can be studied through changes in memory, information flow, and cross-market connectivity.

## Current status

As of 10 August 2026:

- version 0.1.0 is available from PyPI and archived at [Zenodo](https://doi.org/10.5281/zenodo.21844956);
- the estimators, rolling thresholds, signal rules, transaction costs, and synthetic examples are tested in CI;
- a prospective test began on 10 August 2026 and ends on 6 August 2027;
- no result from that holdout exists yet;
- the public-data pipeline is not a numerical reproduction of the paper because the Bloomberg and Refinitiv histories used in the paper cannot be redistributed;
- no independent reproduction or outside research use is recorded yet.

See [RESULTS.md](RESULTS.md) for the result status and [preregistration/DEVIATIONS.csv](preregistration/DEVIATIONS.csv) for changes made after registration.

## Method

MII combines three groups of measurements:

| Component | Measurements | Weight |
| --- | --- | ---: |
| Memory | DFA Hurst exponent, Higuchi fractal dimension, absolute-return ACF decay | 0.35 |
| Information flow | Shannon entropy, Kraskov mutual information, transfer entropy | 0.40 |
| Connectivity | Correlation strength, weighted clustering, correlation-distance MST | 0.25 |

Low, medium, and high states are defined by terciles estimated from the preceding three years and refreshed monthly. The expanding-normalization option also uses only observations available at the date being classified.

## Install and run

```bash
pip install marketmind
```

```python
from marketmind import MarketMind, MarketMindConfig
from marketmind.synthetic import synthetic_market

prices = synthetic_market(periods=1_500, assets=8, seed=42)
model = MarketMind(MarketMindConfig(window=252, step=21))
result = model.fit_transform(
    prices[["SPX", "NDX", "SX5E", "ES"]],
    network_data=prices,
)

print(result.to_frame().tail())
```

An offline example writes its inputs, configuration, raw metrics, MII states, and file hashes to one directory:

```bash
marketmind demo --output artifacts/demo
```

Install `marketmind[data]` for the public-data adapter or `marketmind[dashboard]` for the optional Streamlit interface.

## Prospective test

The registered hypothesis maps high MII to trend signals, medium MII to breakout or volatility-expansion signals, and low MII to mean-reversion signals. The test fixes the market panel, signal definitions, one-session execution lag, primary 5-basis-point cost assumption, inference, exclusions, and robustness checks before the holdout is observed.

- Registration: [OSF nyseh](https://osf.io/nyseh/overview)
- Written plan: [preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md](preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md)
- Executable configuration: [config/preregistered-validation-2026.yml](config/preregistered-validation-2026.yml)

The paper's award and development-sample results are not treated as confirmation of this prospective hypothesis.

## Data limitation

The paper used Bloomberg for SPX, NDX, VIX, and continuous ES; Refinitiv for SX5E; Yahoo Finance for sector ETFs; and FRED for ancillary checks. The first two sources cannot be redistributed here.

[config/paper-public.yml](config/paper-public.yml) substitutes public proxies. It can test whether the code runs and whether conclusions are sensitive to accessible data, but it cannot recover the paper's exact input histories. The 2015–2024 period is a validation sample from the paper, not a new untouched test set.

## Development

```bash
git clone https://github.com/layan985/marketmind.git
cd marketmind
python -m pip install -e ".[all]"
pytest
```

Method details are in [docs/methodology.md](docs/methodology.md). Data and timing conventions are in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Citation and license

> Oraidi, L. (2026). *MarketMind: Multiscale Market Intelligence Research Software* (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.21844956

BSD 3-Clause. MarketMind is research software, not an execution engine or investment recommendation.
