# Reproducibility protocol

MarketMind separates **data provenance**, **feature estimation**, and **strategy
evaluation**. Every run can therefore be audited without trusting a notebook's hidden
state.

## 1. Environment

Use a clean Python 3.10–3.13 environment and install the locked release tag:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "marketmind[data]==0.1.0"
```

For source replication, install the exact Git tag and retain `pip freeze` with the run.

## 2. Data

The paper's provider mapping is:

| Series | Paper source | Public pipeline proxy |
| --- | --- | --- |
| SPX, NDX, VIX, continuous ES | Bloomberg | Yahoo Finance tickers |
| SX5E | Refinitiv | Yahoo Finance ticker |
| XLK, XLF, XLV, XLE | Yahoo Finance | Same family of public histories |
| Ancillary macro series | FRED | Add through a project-specific adapter |

The public pipeline is run with:

```bash
marketmind fetch --config config/paper-public.yml --output data/raw/paper-public
```

It writes `prices.csv` and `manifest.json`. The manifest records the request, date range,
row count, missingness, and a content fingerprint. Vendor revisions can change a later
download, so archive both files with every empirical result.

Licensed Bloomberg and Refinitiv exports should use the same wide schema:

```text
date,SPX,NDX,SX5E,ES,VIX,XLK,XLF,XLV,XLE
2003-01-02,...
```

Do not commit or redistribute data unless the license permits it.

## 3. MII estimation

```bash
marketmind run data/raw/paper-public/prices.csv \
  --output artifacts/paper-public \
  --window 252 \
  --step 21 \
  --development-end 2014-12-31
```

The output directory contains:

- `raw_metrics.csv`: nine unscaled submetrics;
- `normalized_metrics.csv`: `[0,1]` values using frozen development bounds;
- `mii_regimes.csv`: components, MII, rolling thresholds, and state;
- `run_metadata.json`: version, configuration, and input SHA-256.

## 4. Anti-leakage rules

1. Every feature window ends at the current observation.
2. Development scaling freezes at the declared boundary.
3. Regime thresholds use only preceding MII values.
4. Monthly thresholds are held fixed within the month.
5. Signals observed at close execute no earlier than the next session.
6. Transaction costs are charged on every position change.
7. Parameter and strategy trials are counted in multiple-testing corrections.

## 5. Expected differences from the paper

Public proxies will differ because of vendor adjustments, time-zone alignment, holiday
calendars, continuous-futures rolls, and historical revisions. MII component paths should
be compared structurally; matching every printed number requires the original raw
snapshots and exact roll conventions.

The package's explicit normalization policy resolves a method detail left implicit in the
manuscript. Results should always report which policy was used.

