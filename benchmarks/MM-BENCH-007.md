# MM-BENCH-007 — Sampling Frequency Stability

## Question

Does daily versus weekly sampling materially change the inferred MarketMind state after windows are aligned to comparable calendar horizons?

## Comparisons

- daily sampling;
- weekly sampling;
- calendar-horizon-equivalent rolling windows;
- alternate weekly endpoints where relevant.

## Evaluation

State agreement, transition-date drift, component rank stability, persistence, future-volatility separation, missing-data sensitivity and perturbation stability.

## Interpretation rule

A state definition that changes materially under a modest and defensible change in sampling frequency must be interpreted as frequency-dependent rather than as a universal market state.
