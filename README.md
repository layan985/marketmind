# MarketMind

> **Portfolio case study:** [Contribution, public proof, claim boundaries and the next external-validation gate](docs/PORTFOLIO_CASE_STUDY.md).


[![CI](https://github.com/layan985/marketmind/actions/workflows/ci.yml/badge.svg)](https://github.com/layan985/marketmind/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/marketmind.svg)](https://pypi.org/project/marketmind/)
[![Python](https://img.shields.io/pypi/pyversions/marketmind.svg)](https://pypi.org/project/marketmind/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21844956.svg)](https://doi.org/10.5281/zenodo.21844956)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](LICENSE)

**Research software for measuring the market as a changing information network.**

MarketMind turns the methodology of Layan Oraidi's 2026 Charles H. Dow Award paper,
*The Emergent Market Mind: Detecting Self-Organizing Intelligence in Financial Markets
Through Multiscale Information Networks*, into a tested Python package.

**Author ORCID:** https://orcid.org/0009-0005-0202-2582

**Archived software release v0.1.0:** https://doi.org/10.5281/zenodo.21844956

It combines three dimensions into the Market Intelligence Index (MII):

| Dimension | Measures | MII weight |
| --- | --- | ---: |
| Memory | DFA Hurst exponent, Higuchi fractal dimension, absolute-return ACF decay | 0.35 |
| Information flow | 20-bin Shannon entropy, Kraskov mutual information and transfer entropy | 0.40 |
| Connectivity | Correlation strength, weighted clustering, correlation-distance MST | 0.25 |

MII is then classified into low, medium, and high states using lower and upper terciles
learned from the preceding three years and refreshed monthly. Every estimator and
classification decision uses information available at that date only.

## Prospective preregistered validation

A prospective out-of-sample validation of the paper's regime-to-signal mapping is frozen in
[`preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md`](preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md).
The confirmatory holdout runs from **10 August 2026 through 6 August 2027** and tests the
precommitted mapping **High MII → trend, Medium MII → breakout/volatility expansion,
Low MII → mean reversion**. The design freezes MarketMind 0.1.0, the primary market panel,
signal definitions, one-session execution lag, 5-bps primary transaction-cost assumption,
bootstrap inference, exclusions, and robustness checks before the holdout begins.

**OSF preregistration:** https://osf.io/nyseh/overview (`nyseh`)

**Associated OSF project:** https://osf.io/649gj (`649gj`)

The OSF registration URL is now linked publicly. A DOI will be added only if and when OSF
exposes one for the registration; no DOI is being inferred or fabricated from the OSF ID.

The executable data request is frozen in
[`config/preregistered-validation-2026.yml`](config/preregistered-validation-2026.yml), and
all deviations are recorded in [`preregistration/DEVIATIONS.csv`](preregistration/DEVIATIONS.csv).
OSF submission metadata and the field-by-field registration record are in
[`preregistration/OSF_SUBMISSION_METADATA.md`](preregistration/OSF_SUBMISSION_METADATA.md) and
[`preregistration/OSF_COPY_PASTE_FORM.md`](preregistration/OSF_COPY_PASTE_FORM.md).

## Installation

```bash
pip install marketmind
```

Optional capabilities are isolated so the research core stays lightweight:

```bash
pip install "marketmind[data]"       # public yfinance adapter
pip install "marketmind[dashboard]"  # Streamlit + Plotly
pip install "marketmind[all]"        # development, docs, data, dashboard
```

## Sixty-second example

```python
from marketmind import MarketMind, MarketMindConfig
from marketmind.synthetic import synthetic_market

prices = synthetic_market(periods=1_500, assets=8, seed=42)

model = MarketMind(
    MarketMindConfig(
        window=252,
        step=21,
        entropy_bins=20,
        knn_k=3,
    )
)
result = model.fit_transform(
    prices[["SPX", "NDX", "SX5E", "ES"]],
    network_data=prices,
)

print(result.to_frame().tail())
```

To run a completely offline, deterministic end-to-end example:

```bash
marketmind demo --output artifacts/demo
```

The command writes the input data, SHA-256 provenance manifest, raw metrics,
normalized metrics, MII states, and exact run configuration.

## Walk-forward indicator evaluation

```python
from marketmind.backtest import WalkForwardEvaluator
from marketmind.indicators import all_signals

asset = "SPX"
signals = all_signals(prices[asset])
evaluation = WalkForwardEvaluator(cost_bps=5).evaluate(
    prices[asset].pct_change(),
    signals,
    regimes=result.regimes["regime"],
)

print(evaluation.summary[["sharpe", "max_drawdown", "trades"]])
```

The included signal library implements the paper's nine fixed, long-only definitions:
three trend, three mean-reversion, and three breakout/volatility-expansion signals.
Orders execute with a one-session lag. Turnover costs and slippage are charged explicitly.

## What is included

- Paper-aligned fractal and information-theoretic estimators
- Dependency-free dynamic weighted graphs and Prim MSTs
- Causal MII normalization and rolling regime thresholds
- Nine classical technical signals with fixed parameters
- Cost-aware walk-forward evaluation and regime comparison tests
- Buy-and-hold, cash, lag-sign, and exposure-matched shuffled baselines
- Moving-block intervals, White-style reality check, and deflated Sharpe probability
- YAML-driven public-data adapter, checksums, manifests, and complete run artifacts
- Streamlit dashboard, command-line interface, notebooks, MkDocs site, and typed API
- CI across Python 3.10–3.13 and OIDC-based PyPI release automation
- `CITATION.cff`, CodeMeta, and Zenodo metadata for software citation

## Reproducing the paper responsibly

The paper used Bloomberg for SPX, NDX, VIX, and continuous ES; Refinitiv for SX5E;
Yahoo Finance for sector ETFs; and FRED for ancillary robustness data. Bloomberg and
Refinitiv snapshots cannot be redistributed in this repository.

`config/paper-public.yml` provides a transparent public proxy pipeline through yfinance.
It is useful for methodological replication, but it should not be represented as a
bit-for-bit reproduction of the paper's licensed data. Exact numerical replication requires
the original vendor histories and continuous-futures construction.

The primary panel drives memory and information flow; the optional broader
`network_data` panel drives connectivity. This preserves the paper's distinction between
the four primary markets and the sector-ETF network universe.

The manuscript also states that submetrics are normalized to `[0, 1]` without publishing
the scaler details. MarketMind makes this choice auditable:

- `normalization="expanding"` uses causal expanding min/max bounds;
- `normalization="development"` freezes bounds at a declared `development_end`.

For the paper split, set `development_end="2014-12-31"`; the 2015–2024 period remains
a validation sample, not an untouched third test set.

## Dashboard

```bash
marketmind-dashboard
# or
marketmind dashboard
```

Upload a wide price CSV or use the deterministic demo, inspect component histories and
regimes, change window/cost assumptions, compare indicator performance, and export the
resulting MII series.

## Documentation and development

```bash
git clone https://github.com/layan985/marketmind.git
cd marketmind
python -m pip install -e ".[all]"
pytest
mkdocs serve
```

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the exact data and analysis workflow.
The example notebooks are in [`examples/notebooks`](examples/notebooks).

## Citation

The first archived software release is:

> Oraidi, L. (2026). *MarketMind: Multiscale Market Intelligence Research Software* (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.21844956

Use the repository's [`CITATION.cff`](CITATION.cff) for machine-readable citation metadata.
Author ORCID: https://orcid.org/0009-0005-0202-2582. The prospective validation is
preregistered at https://osf.io/nyseh/overview and the associated OSF project is
https://osf.io/649gj.

## Scope

MarketMind is research software, not an execution engine or investment recommendation.
Results depend on data provenance, timing conventions, transaction costs, and estimator
choices. Users are responsible for independent validation before any real-world use.

## License

BSD 3-Clause. Copyright © 2026 Layan Oraidi.
