# MarketMind publication roadmap

This document converts MarketMind from an alpha research package into citable, independently auditable research software.

## Publication gates

MarketMind should not be submitted as a software paper until all of the following are true:

- [ ] Public development history is long enough for meaningful external review.
- [ ] Core estimators have unit tests against analytic or independently computed reference cases.
- [ ] Edge cases and missing-data behavior are documented and tested.
- [ ] The walk-forward framework has leakage tests.
- [ ] Transaction-cost accounting has reference tests.
- [ ] At least one end-to-end example reproduces a published or archived MarketMind result from raw inputs.
- [ ] API documentation builds without warnings.
- [ ] Continuous integration tests supported Python versions.
- [ ] A tagged release is archived with a DOI.
- [ ] The repository contains a software paper draft and bibliography.
- [ ] Known limitations and non-goals are explicit.
- [ ] At least one person other than the primary author has attempted installation and reproduction from the public instructions.

## Scientific validation track

### 1. Estimator validation

For each estimator, maintain a small suite of reference cases:

- Hurst / fractal measures: white noise, persistent synthetic process, anti-persistent synthetic process.
- Mutual information: independent variables and controlled dependent variables.
- Transfer entropy: no-direction null and simulated directional process.
- Networks: hand-computable adjacency / MST cases and permutation-invariant checks.
- Regimes: deterministic threshold fixtures and out-of-sample-only classification tests.
- Backtests: zero-signal, buy-and-hold, random-signal and deliberately leaking controls.

### 2. Reproducibility track

Every empirical claim intended for publication should map to:

1. a versioned configuration file,
2. an immutable raw-data manifest,
3. a deterministic command,
4. a machine-readable result table,
5. a figure/table generated from that result,
6. a software version and commit SHA.

### 3. Baselines

Every strategy comparison should include, where meaningful:

- buy-and-hold,
- cash / zero-exposure,
- naive equal-weight signal ensemble,
- simple trend baseline,
- random or permutation baseline,
- regime-agnostic version of the same strategy.

### 4. Robustness

Pre-specify robustness dimensions rather than selecting them after results are known:

- alternative lookback windows,
- alternative discretizations,
- alternative transaction costs,
- market-by-market exclusion,
- crisis-period exclusion,
- different rebalance frequencies,
- alternative regime boundaries,
- multiple-testing correction where many variants are compared.

## Release sequence

### v0.1.x — alpha hardening
- close correctness gaps,
- add reference tests,
- improve documentation,
- freeze public API where possible.

### v0.2.0 — reproducible research release
- publish a complete end-to-end example,
- archive release and data manifest,
- record DOI,
- publish benchmark outputs.

### v0.3.0 — external audit release
- incorporate outside reproduction findings,
- document resolved and unresolved audit items,
- add contributor credits.

### v1.0.0 — stable research API
- stable documented public interfaces,
- comprehensive tests,
- DOI-backed release,
- publication-ready software paper.

## Evidence policy

Do not claim predictive superiority, profitability, robustness, external adoption, or independent validation unless the corresponding evidence is public and linked. Null and adverse findings belong in the public record.
