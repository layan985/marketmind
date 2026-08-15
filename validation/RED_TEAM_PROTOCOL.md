# MarketMind Red Team Protocol

A release is challenged as if a skeptical researcher is trying to break its claims.

## Required attack classes

| Attack | Question |
| --- | --- |
| Look-ahead leakage | Can any future observation change an earlier feature, metric, state, or position? |
| Timestamp leakage | Is a value used before its real availability time? |
| Normalization leakage | Do bounds or moments use evaluation-period information? |
| Label instability | Do modest defensible choices radically relabel regimes? |
| Metric redundancy | Are complex metrics duplicating simpler quantities? |
| Short-sample instability | Where do estimators stop behaving reliably? |
| Outlier sensitivity | Can one extreme observation dominate a state? |
| Missing-data sensitivity | Do fill/intersection rules alter conclusions? |
| Parameter sensitivity | Does the claim live on a narrow hyperparameter point? |
| Universe sensitivity | Does dropping/adding one asset change the result? |
| Survivorship assumptions | Could selection of surviving assets create the pattern? |
| Transaction-cost sensitivity | Does an applied result disappear under prespecified cost sweeps? |
| Execution timing | Is same-session information earning same-session return? |
| Frequency sensitivity | Does the result depend on one arbitrary sampling frequency? |
| Market selection | Is a claim driven by one selected market? |
| Random-seed sensitivity | Does stochastic estimation materially change the conclusion? |

## Severity

- **Critical:** invalidates causal timing, artifact integrity, or the primary claim.
- **High:** materially changes a headline result or reproducibility.
- **Moderate:** narrows the operating range or interpretation.
- **Low:** documentation, ergonomics, or non-material numerical difference.

## Release artifact

Every red-team report records release, commit, environment, attack configuration, expected invariant, observed behavior, severity, disposition, unresolved issues, and links to reproducing code/data.

Passing ordinary unit tests is not equivalent to passing this protocol.
