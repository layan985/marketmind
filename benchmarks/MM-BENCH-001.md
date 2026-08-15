# MM-BENCH-001 — Multiscale Regime Discrimination

## Question

Does multiscale structural measurement improve regime discrimination beyond volatility alone or other conventional state models?

## Comparators

- MarketMind MII state classification.
- realized-volatility state classification.
- trend × volatility rule.
- k-means-style clustering.
- Gaussian mixture model.
- hidden Markov model where implementation and convergence are documented.

## Primary evaluation dimensions

State persistence, turnover, future-volatility separation, cross-sectional dispersion, perturbation stability, threshold sensitivity, and computational cost.

Trading performance is not required for the primary benchmark. This keeps the first comparison focused on measurement behavior.

## Freeze requirements

Before result interpretation: data version, universe, date range, feature construction, number of states, hyperparameter-selection rule, random seeds, missing-data treatment, state-alignment rule, and all evaluation metrics must be frozen.
