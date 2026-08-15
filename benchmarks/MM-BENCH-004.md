# MM-BENCH-004 — Directional Information Validation

## Question

When does transfer-entropy-style directional information estimation recover known structure, and when does it fail?

## Synthetic systems

- source → target with known lag;
- target → source reverse control;
- no interaction;
- bidirectional coupling;
- common-driver confounding;
- nonlinear coupling;
- time-varying coupling;
- unequal sample sizes;
- multiple noise regimes.

## Outputs

Direction sign, effect magnitude, estimator dispersion, false-direction rate, null false-positive rate, sample-size sensitivity, noise sensitivity, and computational cost.

The existing controlled source→target test is an implementation check. This benchmark is broader: it maps the estimator's operating envelope and failure modes.
