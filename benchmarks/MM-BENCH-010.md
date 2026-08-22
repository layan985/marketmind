# MM-BENCH-010 — Regime Claim Audit / Metamorphic Invariance

**Status:** COMPLETE — initial audit 2026-08-22  
**Parent benchmark:** MMSMB-2 / Market Twins  
**Evidence type:** controlled synthetic model-validation evidence

## Question

Can a score that detects a hidden mechanism switch survive a target-preserving change of representation?

## Motivation

MMSMB-2 found that a simple VAR(1) coefficient-distance score detects a silent propagation change while contemporaneous state summaries remain near chance. That is useful, but it leaves a prior validation question unanswered: is the score measuring the claimed mechanism change or partly measuring the arbitrary coordinate system in which the variables were expressed?

MM-BENCH-010 adds a metamorphic test to answer that question.

## Frozen design

- 9 variables
- 3,000 observations per replication
- break at t=1,500
- 240-observation rolling windows
- 60-observation step
- 600-observation reference period
- 200 replications
- target stationary equicorrelation covariance rho=0.30
- MMSMB-2 propagation matrices and innovation-covariance construction unchanged

### Track A — Silent mechanism shift

Change A_pre to A_post while choosing innovation covariance so the stationary contemporaneous covariance remains fixed.

### Track B — Market Mirage

Hold the propagation matrix fixed while increasing stationary covariance scale 2.25x.

### Track C — Positive diagonal reparameterization

For every Track-A dataset, draw one positive scale per variable and transform the entire series as

x'_t = D x_t,

where diagonal entries of D are log-uniform on [0.05, 20].

This changes units/coordinate scale but not the existence or time of the underlying mechanism switch.

### Sanity relation — Column permutation

Randomly permute variable order. All tested aggregate scores should be permutation invariant up to numerical tolerance.

## Scores

- mean volatility
- average absolute contemporaneous correlation
- PC1 concentration
- raw VAR(1) coefficient Frobenius distance
- **per-window standardized VAR(1) coefficient Frobenius distance**
- lag-correlation Frobenius distance

## Results

### Detection / nuisance behavior

| Score | Silent shift AUC | Mirage AUC |
|---|---:|---:|
| Mean volatility | 0.497 | 1.000 |
| Average absolute correlation | 0.508 | 0.501 |
| PC1 concentration | 0.508 | 0.502 |
| Raw VAR coefficient shift | **0.804** | 0.520 |
| Standardized VAR coefficient shift | **0.806** | 0.520 |
| Lag-correlation shift | 0.712 | 0.507 |

### Positive diagonal reparameterization

| Score | Mean score-rank rho | Mean absolute AUC change |
|---|---:|---:|
| Mean volatility | 0.705 | 0.120 |
| Average absolute correlation | 1.000 | 0.000 |
| PC1 concentration | 1.000 | 0.000 |
| Raw VAR coefficient shift | **0.328** | **0.220** |
| Standardized VAR coefficient shift | **1.000** | **0.000** |
| Lag-correlation shift | 1.000 | 0.000 |

All methods pass the column-permutation sanity test to numerical tolerance.

## Interpretation

The raw VAR score has useful power on the silent mechanism shift, but its magnitude and ranking are strongly coordinate-scale dependent. It therefore does not yet earn a coordinate-free mechanism-change claim.

A minimal correction — standardizing variables inside each estimation window before fitting VAR(1) — retains the detection result and nuisance behavior while making the score invariant to the tested positive diagonal reparameterization.

This is the intended behavior of the Regime Claim Audit: a successful benchmark result is not the end of validation. The claim is subsequently exposed to transformations that should preserve the target. If it fails, the failure remains part of the evidence record.

## Claim ceiling from this experiment

- Raw VAR score: useful **C2 candidate**, but fails the tested representation requirement as originally specified.
- Standardized VAR score: passes this C2 representation test, but **does not earn C3 causal orientation**.
- Lag-correlation score: representation invariant here, but materially weaker on the silent mechanism track.

## Reproduce

Run:

```bash
python benchmarks/claim_audit/run_rca1.py
```

Machine-readable results: `benchmarks/claim_audit/rca1_results.json`

## Claim boundary

Controlled synthetic evidence only. This benchmark does not establish causal identification in live financial markets, profitability, forecast value, regulatory fitness, or invariance to transformations not explicitly tested here.
