# MM-BENCH-005 — MII Component Ablation

## Question

Does each Market Intelligence Index component add stable information after ablation, and do the displayed weights materially affect the inferred state map?

## Arms

- memory only;
- information only;
- connectivity only;
- memory + information;
- memory + connectivity;
- information + connectivity;
- equal weighting;
- current weighting (0.35 memory, 0.40 information, 0.25 connectivity);
- PCA-derived combination;
- rank aggregation;
- random plausible weight simplex.

## Evaluation

Regime stability, classification agreement, state persistence, future-volatility separation, cross-market consistency, transition-date stability and perturbation sensitivity.

## Interpretation rule

If a simpler combination reproduces the classifications and stability of the full MII, the added complexity has not earned its place. A null ablation result is publishable evidence.
