# MarketMind Benchmark Program

MarketMind already has a completed deterministic benchmark product and an executable institutional benchmark engine, alongside the next comparative benchmark specifications.

## MM-BENCH-SYN-001 — completed synthetic benchmark

MarketMind Synthetic Regime Benchmark Dataset v1.0.0 contains 4,000 business days, nine synthetic series, known latent regimes, rolling structural features, MII, causal prior-only thresholds, inferred states, benchmark summary, confusion matrix, provenance, codebook, data dictionary and SHA-256 hashes. Recorded exact latent-regime classification accuracy after warm-up: **0.497**. This is synthetic benchmark evidence only.

## MM-BENCH-INST-001 — executable institutional benchmark

`marketmind.benchmark.run_benchmark_bundle` generates a 14-artifact assurance bundle from a supplied price panel using the frozen contract `config/institutional-public-benchmark.yml` and `PUBLIC_BENCHMARK_PROTOCOL.md`. It includes fixed signal-family results, buy-and-hold/cash/lagged-sign/exposure-matched-shuffle comparators, cost sweeps, moving-block Sharpe intervals, White-style family reality-check and deflated-Sharpe diagnostics, MII/regime outputs, source/input fingerprinting, QA, limitations, claim register, run metadata, decision memo and artifact hashes.

A provider result is labeled `REAL PUBLIC DATA` only after the actual run is frozen.

## Next comparative specifications

- `MM-BENCH-001` — multiscale regime discrimination.
- `MM-BENCH-002` — leakage resistance laboratory.
- `MM-BENCH-003` — network metric stability and redundancy.
- `MM-BENCH-004` — directional-information validation.
