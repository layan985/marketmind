# MM-RN-003 — How Much Alpha Can Look-Ahead Bias Manufacture?

**MarketMind Research Note · 18 August 2026**  
**Version:** 1.0  
**Status:** PUBLIC · REPRODUCIBLE  
**Evidence class:** controlled synthetic experiment

## Abstract

How large can apparent risk-adjusted performance become when a backtest is allowed to use information that did not exist at the decision time? We run 100 fixed-seed simulations of 4,000 IID Gaussian returns and compare a strictly causal trailing signal with two deliberate timing failures and two selection procedures. The causal control produces mean annualized Sharpe **0.019**. A centered rolling feature produces **2.796**, with every replication above 2, while same-session execution produces **21.017**. Selection among 50 independent noise signals raises the mean winning Sharpe to **0.555**. Because the data-generating process contains no predictive structure, the experiment isolates how invalid information sets and research selection can manufacture apparent evidence from noise.

## Experimental design

For replication j=1,…,100, draw `r_t ~ IID N(0, 0.01)`, t=1,…,4,000. Seeds are 1000–1099. Strategy returns equal `s_t * r_t`. Annualized Sharpe is `sqrt(252) * mean(strategy_return) / sample_sd(strategy_return)`.

1. **Causal trailing control** — sign of a 20-session rolling mean shifted one session.
2. **Centered rolling window** — sign of a 21-session centered rolling mean; future observations enter the value attached to t.
3. **Same-session execution** — signal is `sign(r_t)` and receives `r_t`; deliberately pathological.
4. **Retrospective threshold** — best of 17 cutoffs selected after observing the realized sample.
5. **Best of 50 noise signals** — best backtest retained from 50 independent noise signals.

## Corrected distribution results

| Arm | Mean | Median | P5 | P95 | Max | P(Sharpe>1) | P(Sharpe>2) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Causal trailing control | **0.019** | 0.007 | -0.334 | 0.395 | 0.567 | 0% | 0% |
| Centered rolling window | **2.796** | 2.791 | 2.359 | 3.118 | 3.462 | 100% | 100% |
| Same-session execution | **21.017** | 21.023 | 20.589 | 21.497 | 21.708 | 100% | 100% |
| Retrospective threshold | 0.191 | 0.168 | -0.153 | 0.523 | 0.716 | 0% | 0% |
| Best of 50 noise signals | 0.555 | 0.549 | 0.387 | 0.811 | 1.014 | 1% | 0% |

The causal control behaves as the known null requires. The centered-window error shifts the entire Sharpe distribution: its 5th percentile is 2.359 and all 100 runs exceed 2. Same-session execution is more destructive still.

## Reproducibility correction

An earlier committed summary preserved the correct five arm means but several secondary distribution statistics did not reproduce from the disclosed generator. Version 1.0 recomputes those statistics from the exact public code, publishes the full run-level CSV, and retains the earlier state in Git history. The headline means and central inference are unchanged. See `governance/CORRECTIONS_RETRACTIONS.md`.

## Interpretation boundary

This experiment does **not** imply that a specific reported strategy with Sharpe 2.8 contains a centered-window bug, nor that every timing error inflates performance. The same-session arm is intentionally unrealistic. Exact magnitudes depend on sample length, volatility, signal construction, turnover, estimator choice and the DGP. IID Gaussian returns omit serial dependence, volatility clustering, jumps, heavy tails, cross-sectional dependence and market microstructure. Transaction costs are omitted because the object is contamination magnitude rather than economic viability. No prospective MarketMind holdout is accessed, scored or summarized.

## Reproduction record

- Experiment: `LAB-002`
- Replications: 100
- Observations per replication: 4,000
- Seeds: 1000–1099
- Raw results: `experiments/records/LAB-002_runs.csv`
- Summary: `experiments/records/LAB-002_summary.csv`
- Figure: `experiments/records/LAB-002_chart.svg`
- Builder: `experiments/build_lab_records.py`
- Original generator: `experiments/run_lab_v0_1.py`
- Public page: https://marketmind-hazel.vercel.app/mm-rn-003
- Release reference: `MM-RN-003-v1.0`

**Interpretation boundary:** controlled synthetic evidence only; no real-market performance claim; prospective holdout untouched.
