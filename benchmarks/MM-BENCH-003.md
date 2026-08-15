# MM-BENCH-003 — Network Metric Stability and Redundancy

## Question

Do correlation strength, weighted clustering, MST structure, eigenvalue concentration, and selected centrality summaries provide materially distinct information?

## Tests

- rank and linear dependence among metrics;
- rolling stability;
- sensitivity to missing assets;
- sensitivity to one extreme asset;
- universe perturbation;
- frequency changes;
- known synthetic network structures;
- regime-boundary sensitivity after ablation.

## Interpretation rule

Redundancy is a legitimate result. A complex network component may be removed or down-weighted if a simpler quantity captures the same stable information.
