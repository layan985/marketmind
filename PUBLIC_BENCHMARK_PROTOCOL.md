# MarketMind Public Benchmark Protocol

This protocol defines the historical public-data benchmark used to demonstrate the MarketMind delivery process without contaminating the sealed prospective validation stream.

## Purpose

The benchmark exists to answer a narrow institutional question:

**Can a client inspect a complete MarketMind analytical delivery from source metadata through assumptions, benchmarks, uncertainty, limitations and artifact hashes?**

It is not designed to maximize performance, discover a favorable historical period or preview the registered prospective holdout.

## Frozen universe

The default public benchmark contract is stored in `config/institutional-public-benchmark.yml`.

Reference asset:

- SPY

Cross-asset context:

- QQQ
- IWM
- EFA
- EEM
- TLT
- GLD
- XLK
- XLF
- XLE

Default historical window:

- 1 January 2010 through 1 January 2026 provider endpoint

The universe is intentionally simple, liquid and publicly retrievable. It is not claimed to reproduce the proprietary or licensed data used in the original paper.

## Frozen execution assumptions

- one-session execution lag;
- 5 bps proportional transaction cost per unit turnover;
- 1 bp proportional slippage per unit turnover;
- 252-session annualization;
- 20-session moving-block bootstrap;
- 1,000 bootstrap draws;
- fixed random seed `20260815`;
- cost sensitivity at 0, 5, 10, 25 and 50 bps.

Changing any of these values creates a different benchmark specification and must be recorded as such.

## Fixed strategy search set

The benchmark evaluates the nine public MarketMind signal definitions already in `marketmind.indicators`:

1. SMA 50/200 crossover;
2. 100-session moving-average slope;
3. price above EMA(100);
4. RSI(14) reversion;
5. Bollinger reversal;
6. three-session reversal;
7. 20-session breakout;
8. Donchian 20;
9. ATR expansion.

The search set is reported because the highest historical performer is a selected maximum rather than an independently specified single strategy.

## Required comparators

Every run includes:

- buy and hold;
- cash;
- lagged-sign reference;
- exposure-matched shuffled signal;
- transaction-cost sensitivity.

A signal result must never be presented without its comparator matrix.

## Required inference

Every run includes:

- moving-block bootstrap intervals for signal Sharpe estimates;
- a White-style reality check over the fixed nine-signal family;
- deflated-Sharpe diagnostics using the disclosed number of signal trials.

These procedures reduce overstatement risk. They do not prove that the strategy search is exhaustive or eliminate all selection bias.

## Required evidence bundle

`marketmind.benchmark.run_benchmark_bundle` writes:

- `benchmark_summary.csv`
- `baseline_summary.csv`
- `cost_sweep.csv`
- `inference.csv`
- `mii_regimes.csv`
- `signal_net_returns.csv`
- `baseline_net_returns.csv`
- `input_manifest.json`
- `run_metadata.json`
- `QA_REPORT.md`
- `LIMITATIONS.md`
- `DECISION_MEMO.md`
- `CLAIM_REGISTER.csv`
- `artifact_manifest.json`

A run is incomplete if any required artifact is missing.

## Evidence label

A run using a publicly accessible provider may be labeled `REAL PUBLIC DATA` only when the source metadata truthfully records that provider and the exact analytical frame is fingerprinted.

`REAL PUBLIC DATA` does not imply:

- `OFFICIAL SOURCE`;
- `PRODUCTION CLIENT DATA`;
- `EXTERNAL REVIEW`;
- `INDEPENDENT REPRODUCTION`;
- prospective confirmation.

Controlled CI fixtures must use `SYNTHETIC`.

## Negative-result rule

All fixed signals remain in the bundle whether favorable, null or adverse. A signal may not be dropped from the public benchmark because it weakens the narrative.

## Revisions

A benchmark specification change requires a dated change-log entry identifying:

- field changed;
- old value;
- new value;
- reason;
- whether historical outputs must be regenerated.

The sealed prospective protocol remains untouched by revisions to this historical public benchmark.
