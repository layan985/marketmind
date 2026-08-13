# Interactive Research Terminal

Install and launch:

```bash
pip install "marketmind[dashboard]"
marketmind-dashboard
```

The terminal can use deterministic synthetic data or a user-supplied wide CSV. It exposes MII and its three component paths, the latest causal regime, rolling parameter and cost controls, all nine regime-conditional indicator reports, and downloadable MII, thresholds, and regime labels.

## Evidence console

| Evidence card | Result | Label | Interpretation boundary |
| --- | ---: | --- | --- |
| Earlier regime rows changed after future-only perturbation | **0 / 350** | `SYNTHETIC` | Controlled perturbation only; not exhaustive proof against every leakage mechanism |
| Known directional-information separation | **+1.218 nats** | `SYNTHETIC` | Known-structure recovery; not real-market predictive evidence |
| Controlled research audit | **7 / 7 checks passed** | `PENDING VALIDATION` | Internal controlled audit; not independent review |
| Hash-verified result artifacts | **4 / 4** | `PENDING VALIDATION` | Integrity evidence; not external validity |
| CI source tests | **29 passing** | `PENDING VALIDATION` | Implementation evidence; not economic validation |
| Branch-aware test coverage | **83.06%** | `PENDING VALIDATION` | Coverage does not imply model truth |
| Prospective holdout | **SEALED** | `PENDING VALIDATION` | No interim performance result is available or permitted |

## Public terminal modules

The intended public terminal contains these report surfaces:

- **Market Regime Report** — regime state, persistence, transition context and uncertainty.
- **Memory Diagnostics** — DFA Hurst, Higuchi dimension and volatility-memory decay.
- **Information Flow Report** — entropy, mutual information and directional transfer-entropy diagnostics.
- **Connectivity Report** — structural coherence and stability measures.
- **Network Structure Report** — threshold graphs, weighted clustering and minimum-spanning-tree structure.
- **Regime Transition Report** — transition timing, persistence and sensitivity.
- **Signal-Family Diagnostics** — pre-specified indicator-family behavior by regime.
- **Walk-Forward Validation Report** — train/test separation, rolling-origin evaluation and next-session execution.
- **Transaction-Cost Stress Test** — cost/slippage sweeps and break-even sensitivity.
- **Benchmark Comparison** — naive and pre-specified baselines.
- **Perturbation Audit** — future-only perturbations and earlier-output invariance.
- **Data Leakage Audit** — feature, scaler, threshold and regime timing.
- **Timing Audit** — same-session versus next-session execution contract.
- **Prospective Validation Status** — registration, frozen release, start/end dates and sealed-result status.
- **Replication Status** — documented outside reruns only.
- **Research Use Registry** — documented outside research uses only.

## Public-display contract

Every important visual should expose:

**SOURCE / N / WINDOW / FILTER / LABEL / STATUS / LIMITATION / DOWNLOAD DATA / CODE VERSION**

Internal audit results must not be promoted to `EXTERNAL REVIEW` or `INDEPENDENT REPRODUCTION` until documented outside evidence exists. The prospective holdout must remain visually and technically sealed until its registered end condition.

## What would falsify or materially weaken MarketMind?

1. A clean rerun cannot reproduce a frozen controlled result under the documented configuration.
2. Future-only perturbations alter earlier features, thresholds, regimes or confirmatory positions beyond the declared tolerance.
3. Known-structure directional-information tests fail to recover the disclosed direction under the frozen audit design.
4. Result files do not match their declared hashes or byte counts.
5. The prospective holdout violates the preregistered timing, selection, cost or evaluation contract.
6. Independent reproductions repeatedly fail under equivalent inputs and configuration.

Uploaded data remains in the running Streamlit process. Any institutional deployment should add appropriate access controls and data-retention policies before accepting licensed or confidential histories.