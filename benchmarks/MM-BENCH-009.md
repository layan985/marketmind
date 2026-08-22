# MM-BENCH-009 — Mechanism Identifiability / Market Twins

**Status:** COMPLETE — controlled synthetic result available  
**Benchmark:** MMSMB-2 / Market Twins  
**Run date:** 2026-08-22  
**Primary question:** can a detector distinguish a change in temporal market mechanism from a change in observable market state?

## Frozen construction

A stable nine-variable VAR(1) is used as a controlled market process. In the **silent mechanism shift**, the transition matrix changes but the stationary contemporaneous covariance is held fixed by setting

`Q_r = Sigma - A_r Sigma A_r^T`.

In the **market mirage**, the transition matrix is held fixed while the stationary covariance scale increases 2.25x.

A separate **impossible orientation** track presents two linear-Gaussian structural directions that induce the same observational law.

## Primary results

Across 200 core replications:

| Track / score | Mean AUC |
| --- | ---: |
| Silent shift — mean volatility | 0.505 |
| Silent shift — average absolute correlation | 0.497 |
| Silent shift — PC1 concentration | 0.497 |
| Silent shift — VAR coefficient shift | **0.797** |
| Silent shift — lag-correlation shift | **0.727** |
| Mirage — mean volatility | **1.000** |
| Mirage — VAR coefficient shift | 0.492 |
| Mirage — lag-correlation shift | 0.500 |

The exact stationary covariance difference in the silent track is 2.7e-15 at numerical precision.

## Detection frontier

Holding Sigma fixed, mean VAR-shift AUC as mechanism displacement increases:

- 0.25x: 0.492
- 0.50x: 0.549
- 1.00x: 0.803
- 1.50x: 0.965
- 2.00x: 0.997

This is retained as a difficulty curve, not merely a single favorable break.

## Impossible orientation

Across 800 generated bivariate datasets, a classifier attempting to infer whether the data came from the `X -> Y` or `Y -> X` linear-Gaussian representation reaches 0.516 mean 10-fold CV accuracy. Both representations induce the same observational Gaussian distribution; extra assumptions or interventions are required for orientation.

## Interpretation

The benchmark separates two notions that are often collapsed:

- **state regime:** observable marginal/dependence conditions change;
- **mechanism regime:** the temporal propagation law changes.

A method should be evaluated on both structural sensitivity and nuisance invariance. It should also be permitted to abstain when the target is not identified by the information supplied.

## Claim boundary

Controlled synthetic measurement evidence only. VAR and lag-correlation distances are baselines for change detection, not causal-identification guarantees. No return-prediction, execution, or trading-profit claim is made.

Reproduction materials: `benchmarks/mmsmb2/`.
