# MM-BENCH-006 — Universe Stability

## Question

How stable are MarketMind regime labels under small, disclosed changes in the asset universe?

## Perturbations

- remove the largest or most central asset;
- remove one random asset;
- remove 20% of the universe;
- repeat across seeds and universes;
- compare transition-date drift and state agreement.

## Evaluation

Metric correlation, regime-label disagreement, Jaccard overlap, transition-date drift, persistence, future-volatility separation and component sensitivity.

## Interpretation rule

A high correlation between metric series does not establish classification invariance. If small universe changes move a scientifically meaningful fraction of state labels, that sensitivity must be disclosed and may require a stability rule or narrower interpretation.
