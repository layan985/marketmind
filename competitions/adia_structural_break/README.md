# MarketMind × ADIA Structural Break Open Benchmark

This branch adapts MarketMind's regime-measurement ideas to the 2026 ADIA Lab / CrunchDAO Structural Break Open Benchmark.

## Why this entry exists

The benchmark requires deterministic code that scores whether a known boundary separates two different data-generating regimes. Quarterly prizes are $3,000 / $2,000 / $1,000, and reward eligibility also depends on originality: out-of-sample predictions cannot correlate above 95% with any fixed original top-10 reference model.

This implementation deliberately avoids cloning the published high-dimensional stacked ensembles from the original competition. Its first baseline uses a compact, inspectable feature contract built around five break mechanisms:

1. distribution shift;
2. scale shift;
3. local boundary discontinuity;
4. memory/trend reorganization;
5. spectral reorganization.

The model is a deterministic `HistGradientBoostingClassifier` on those features.

## Submission interface

`main.py` exposes the required CrunchDAO functions:

- `train(X_train, y_train, model_directory_path=...)`
- `infer(X_test, model_directory_path=...)`

The training artifact is written to `resources/marketmind_structural_break.joblib`.

## Research rule

Leaderboard performance is not a MarketMind scientific claim. Any comparison to reference models should be recorded as a separate benchmark result with the exact competition data/version, code commit, score, originality result, and date.

## Next experiment sequence

1. Run the compact baseline locally and record cross-validated ROC-AUC.
2. Add ablations for boundary / distribution / memory / spectral feature blocks.
3. Check deterministic inference byte-for-byte.
4. Submit the compact model before adding complexity.
5. Only add a second-stage model if it improves CV without collapsing originality.
