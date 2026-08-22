# MarketMind Benchmark Program

A benchmark is valuable only if it can embarrass the method that created it. Competitors are selected because they are reasonable alternatives, not because they are easy to beat. Simpler models can win, negative findings remain public, and an unidentified target is allowed to have the answer “cannot know from these observations.”

## Registry

| ID | Question | Status |
| --- | --- | --- |
| MM-BENCH-001 | Does multiscale structure improve regime discrimination beyond simpler state models? | **complete** — realized volatility 71.5%, MII 48.3% held-out accuracy |
| MM-BENCH-002 | How much apparent performance inflation can common leakage errors create? | active laboratory evidence |
| MM-BENCH-003 | Do MarketMind network metrics contain distinct information? | **complete** — average correlation reproduces 95.3% of connectivity states |
| MM-BENCH-004 | When does directional-information estimation succeed or fail under known structure? | partial laboratory evidence |
| MM-BENCH-005 | Which MII components survive ablation? | specified |
| MM-BENCH-006 | How stable are conclusions to universe changes? | specified |
| MM-BENCH-007 | How stable are conclusions to sampling frequency? | specified |
| MM-BENCH-008 | What is the smallest model that reproduces the scientifically relevant conclusions? | specified |
| MM-BENCH-009 | Can a method distinguish a mechanism change from a state change, and abstain when structure is not identifiable? | **complete** — MMSMB-2 / Market Twins |

## MMSMB-2 / Market Twins

The newest benchmark holds stationary contemporaneous covariance fixed while changing a temporal propagation mechanism, then reverses the experiment by changing volatility scale while holding propagation fixed.

Across 200 replications:

- silent mechanism shift: VAR coefficient-distance AUC **0.797**; mean-volatility AUC **0.505**;
- market mirage: mean-volatility AUC **1.000**; VAR coefficient-distance AUC **0.492**;
- observationally equivalent orientation challenge: direction classifier accuracy **0.516** across 800 datasets.

See `benchmarks/mmsmb2/` and `MM-BENCH-009.md`.

## Completion standard

Each completed benchmark should publish configuration, data or generator version, code, environment, comparator implementation, acceptance metrics, prespecified results, negative findings, claim boundaries and a machine-readable result record.
