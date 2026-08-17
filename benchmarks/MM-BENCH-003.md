# MM-BENCH-003 — Network Metric Stability and Redundancy

**Status: COMPLETE · RESULT AVAILABLE**  
**Benchmark dataset:** MMSMB-1-v0.1  
**Prospective MarketMind trading holdout:** untouched.

## Question

Is the MarketMind connectivity component genuinely adding information, or is it largely average correlation with additional machinery?

## Test

The held-out half of MMSMB-1 is scored using the MarketMind connectivity component (the normalized mean of average absolute correlation, weighted clustering and MST coherence). Its continuous values and fixed-tercile state assignments are compared with individual network summaries. All thresholds are frozen from the development half.

| Comparator | Pearson r with connectivity component | State agreement | ARI |
|---|---:|---:|---:|
| Average absolute correlation | **0.981** | **95.3%** | 0.851 |
| Weighted clustering | 0.967 | 95.3% | 0.880 |
| MST coherence | 0.975 | **100.0%** | 1.000 |
| Leading-eigenvalue concentration | 0.981 | 95.3% | 0.851 |

## Result

**Average absolute correlation reproduces 95.3% of MarketMind connectivity-state assignments on this benchmark.** More uncomfortably, MST coherence reproduces 100% under the fixed-tercile protocol.

## Interpretation rule

Redundancy is a legitimate result. This benchmark does **not** justify a claim that the composite connectivity layer contains material state information unavailable from simpler summaries. In MMSMB-1, the complex layer is mostly redundant. That is precisely the kind of result the benchmark program is meant to expose.

The result is dataset- and protocol-specific: MMSMB-1 has a common-factor structure that can make several dependence measures co-move. Future controlled worlds should deliberately separate correlation magnitude, topology, direction and concentration to identify when a richer network representation becomes necessary.

## Reproduce

- Results: `benchmarks/results/MM-BENCH-003_results.csv`
- Daily support table: `benchmarks/results/MM-BENCH-003_timeseries.csv`
- Runner: `benchmarks/run_mm_bench_001_003.py`
- Dataset: `benchmarks/mmsmb1/`
