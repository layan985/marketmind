# Experiments

Experiments are registered evidence objects rather than screenshots or post-hoc demonstrations.

## Current experiment classes

| Class | Purpose | Evidence state |
| --- | --- | --- |
| Future-only perturbation | Detect look-ahead leakage by changing future information and checking earlier outputs | `SYNTHETIC` |
| Known-direction information flow | Test whether a controlled source→target direction separates from the reverse direction | `SYNTHETIC` |
| Cost and slippage stress | Test sensitivity of strategy-family results to execution assumptions | controlled / public-data dependent |
| Benchmark comparisons | Compare pre-specified methods with naive baselines under the same evaluation contract | controlled / public-data dependent |
| Prospective holdout | Evaluate frozen choices after the registered out-of-sample period | `PENDING VALIDATION` / sealed |

## Experiment record

Every experiment should resolve to: `experiment_id`, hypothesis, pre-specified configuration, data class, train/test boundary, seed where applicable, metrics, guardrails, artifacts, hashes, result state, limitation and whether the result was known before specification.

A failed experiment remains in the research record.
