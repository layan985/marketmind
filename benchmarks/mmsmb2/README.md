# MMSMB-2 / Market Twins

**Same market, different machine.**

MMSMB-2 asks a narrower question than ordinary regime benchmarks: can a detector distinguish a genuine change in the time-series propagation mechanism from a change in volatility or contemporaneous dependence?

The benchmark is synthetic and controlled. It is not evidence of trading profitability.

## Track A — Silent mechanism shift

A 9-variable stable VAR(1) switches from `A_pre` to `A_post` halfway through each 3,000-observation sample. The innovation covariance is chosen separately in each regime so that the exact stationary contemporaneous covariance is unchanged:

`Q_r = Sigma - A_r Sigma A_r^T`

The target covariance has unit variances and average pairwise correlation 0.30. The pre/post mechanism matrices differ by Frobenius distance 0.4132.

Across 200 replications, using 240-observation trailing windows:

| Score | Mean AUC |
| --- | ---: |
| Mean volatility | 0.505 |
| Average absolute correlation | 0.497 |
| PC1 concentration | 0.497 |
| VAR(1) coefficient shift | 0.797 |
| Lag-correlation matrix shift | 0.727 |

The point is not that the VAR baseline is universally correct. The point is that the ordinary contemporaneous summaries are deliberately deprived of the signal they normally exploit.

## Track B — Market mirage

The propagation matrix is held fixed while the stationary covariance scale increases by 2.25x.

Across 200 replications:

| Score | Mean AUC |
| --- | ---: |
| Mean volatility | 1.000 |
| Average absolute correlation | 0.509 |
| PC1 concentration | 0.509 |
| VAR(1) coefficient shift | 0.492 |
| Lag-correlation matrix shift | 0.500 |

This is the mirror image of Track A: a state statistic should react to the nuisance shift, while a mechanism-change score should remain quiet.

## Detection frontier

The benchmark also scales the post-break mechanism displacement while preserving the same target covariance. With 20 replications per level, mean VAR-shift AUC rises from 0.492 at 0.25x displacement to 0.549 at 0.50x, 0.803 at 1.00x, 0.965 at 1.50x and 0.997 at 2.00x.

This prevents the benchmark from being just one hand-picked easy break: it exposes a difficulty curve.

## Track C — Impossible orientation

A separate two-variable linear-Gaussian experiment constructs `X -> Y` and `Y -> X` structural equations that induce the same observational bivariate Gaussian distribution. A logistic classifier given sample moments through the fourth order reaches 0.516 mean 10-fold cross-validated accuracy across 800 generated datasets, essentially chance.

The correct target in this track is therefore abstention or equivalence-class reporting, not confident orientation.

## Reproduce

```bash
python benchmarks/mmsmb2/run_mmsmb2.py
```

The runner writes the matrices, a public Market Twin sample, window-level records and `mmsmb2_results.json`.

## Claim boundary

- controlled synthetic evidence only;
- no return-prediction or trading claim;
- VAR and lag-correlation distances are change-detection baselines, not causal-identification guarantees;
- the public result establishes a benchmark construction and baseline behavior, not universal superiority of one detector.
