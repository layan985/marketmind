# MarketMind Research Terminal

**AWARD-WINNING THEORY. OPEN IMPLEMENTATION. FROZEN PROSPECTIVE TEST.**

MarketMind is the research implementation of Layan Oraidi's 2026 Charles H. Dow Award paper, *The Emergent Market Mind*. It treats markets as adaptive information networks and estimates changing structural coherence through memory, information flow and connectivity.

The public terminal is not a trading-signal showroom. It is an evidence system: choose a market and window, inspect memory, information flow, connectivity, network structure, regime state, uncertainty, validation and reproducibility, then export the evidence trail.

## Evidence console

| Evidence card | Result | Badge | What it proves | What it does **not** prove |
| --- | ---: | --- | --- | --- |
| Earlier regime rows changed after future-only perturbation | **0 / 350** | `SYNTHETIC` | The controlled perturbation did not alter earlier regime assignments | Exhaustive absence of every possible leakage mechanism |
| Known directional-information separation | **+1.218 nats** | `SYNTHETIC` | The known source→target direction separates from the reverse direction in the controlled test | Predictive profitability in real markets |
| Hash-verified result artifacts | **4 / 4** | implementation evidence | Frozen result files match their recorded hashes | External validity |
| Controlled research audit | **7 / 7 checks passed** | implementation evidence | The current controlled audit suite passes | Independent reproduction |
| CI source tests | **29 passing** | implementation evidence | Current tested implementation passes the repository test suite | Economic truth |
| Branch-aware test coverage | **83.06%** | implementation evidence | Current branch-aware coverage under the documented environment | Complete behavioral coverage |
| Prospective holdout result | **SEALED** | `PENDING VALIDATION` | Interim outcome is deliberately unavailable under the registered design | Any claim about prospective performance |

The prospective holdout began **10 August 2026** and is registered to end **6 August 2027**. No interim performance result should appear here before the registered end condition.

## Research terminal modules

The public research terminal is organized around these report objects:

- **Market Regime Report** — regime state, persistence, transition context and uncertainty.
- **Memory Diagnostics** — DFA Hurst, Higuchi dimension and volatility-memory decay.
- **Information Flow Report** — entropy, mutual information and directional transfer-entropy diagnostics.
- **Connectivity Report** — coherence/connectivity measures and their stability.
- **Network Structure Report** — threshold networks, weighted clustering and MST structure.
- **Regime Transition Report** — transition timing, persistence and boundary sensitivity.
- **Signal-Family Diagnostics** — pre-specified indicator-family behavior by regime.
- **Walk-Forward Validation Report** — next-session execution, train/test separation and rolling evaluation.
- **Transaction-Cost Stress Test** — cost/slippage sweeps and break-even sensitivity.
- **Benchmark Comparison** — naive and pre-specified baselines.
- **Perturbation Audit** — future-only perturbations and earlier-output invariance.
- **Data Leakage Audit** — feature timing, scaler timing, regime timing and artifact checks.
- **Timing Audit** — same-session versus next-session execution contract.
- **Prospective Validation Status** — preregistration, frozen configuration, start/end dates and sealed-result status.
- **Replication Status** — outside reruns only; internal reruns do not count.
- **Research Use Registry** — documented outside research uses only.

## Analytical path

**choose market → choose window → memory → information flow → connectivity → network → regime → uncertainty → diagnostics → validation → export report**

Every chart should expose **SOURCE / N / WINDOW / FILTER / STATUS / LIMITATION / DOWNLOAD DATA**. Public proxies are labeled as public proxies; controlled synthetic tests are not marketed as real-market results; and the prospective holdout remains visibly sealed.

## What would falsify or materially weaken MarketMind?

A serious falsification standard is part of the product. Evidence would weaken the implementation or theory if, for example:

1. a clean rerun cannot reproduce a frozen controlled result under the documented configuration;
2. future-only perturbations alter earlier features, regimes or confirmatory positions in a way not permitted by the study contract;
3. known-direction information-flow tests fail to recover the disclosed direction under pre-specified conditions;
4. benchmark or cost-stress results eliminate any claimed incremental value under the exact comparison contract;
5. prospective results fail the registered evaluation criteria once the holdout is legitimately opened;
6. an independent reproduction identifies a material methodological or implementation error.

A failed test is not hidden; it becomes part of the release record.

## Design principles

- **Causal by construction.** Rolling features, scalers, regimes and orders use no future data.
- **Scientifically explicit.** Ambiguities become named configuration choices.
- **Auditable.** Pipeline runs retain metrics, configuration and input/artifact hashes.
- **Data-source honest.** Public proxies are not presented as licensed-vendor reproductions.
- **Hard to fool.** Costs, naive baselines, resampling and multiple-testing corrections are first-class APIs.
- **Validation-aware.** Controlled implementation evidence, external review, independent reproduction and prospective evidence are kept distinct.

## Core capabilities

| Layer | Package support |
| --- | --- |
| Memory | DFA Hurst, Higuchi dimension, volatility-memory decay |
| Information | Shannon entropy, KSG mutual information, conditional-MI transfer entropy |
| Networks | Threshold graphs, weighted clustering, correlation-distance Prim MST |
| Regimes | Causal monthly rolling terciles |
| Strategies | Nine fixed indicators, next-session execution, costs and slippage |
| Robustness | Cost sweeps, naive baselines, block bootstrap, reality check, deflated Sharpe |
| Delivery | CLI, notebooks, Streamlit dashboard, CI, PyPI and Zenodo metadata |

Start with the [quickstart](quickstart.md), inspect the [methodology](methodology.md), read the [controlled research audit](research-audit.md), then inspect [validation](validation.md) and the [dashboard](dashboard.md).

!!! warning
    MarketMind is research software. It does not place trades and is not investment advice.
