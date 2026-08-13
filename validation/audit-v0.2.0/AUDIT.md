# MarketMind controlled research audit

**Result: 7/7 controlled checks passed.**

This audit tests implementation invariants and recovery of disclosed synthetic structure. It is not evidence of trading profitability and is not a substitute for the sealed 2026–2027 prospective holdout.

| Check | Result | Observed statistic | Acceptance rule |
| --- | --- | --- | --- |
| Seeded synthetic replay | **PASS** | `{"sha256": "a10ed7912f197c4dab98c34879b7557503a5e0d51661542909a40e3956a20432"}` | identical frame fingerprints |
| Known-structure recovery | **PASS** | `{"clustering": 0.878759, "mean_correlation": 0.889022, "mst_coherence": 0.901451}` | every connectivity measure correlates at least 0.75 with trailing latent coherence |
| Feature look-ahead audit | **PASS** | `{"max_abs_difference": 0.0}` | future perturbation changes no earlier raw metric beyond 1e-12 |
| Threshold look-ahead audit | **PASS** | `{"unchanged_rows": 350}` | future MII perturbation changes zero prior thresholds or labels |
| Directional information recovery | **PASS** | `{"margin": 1.21798, "source_to_target": 1.240758, "target_to_source": 0.022778}` | known causal direction exceeds reverse transfer entropy by at least 0.15 nats |
| Preregistered strategy contract | **PASS** | `{"max_family_selection_error": 0.0, "same_session_position": 0.0}` | exact High/Medium/Low family mapping and no same-session execution |
| Result-bundle integrity | **PASS** | `{"verified_files": 4}` | every declared byte count and SHA-256 digest matches |

## Audit configuration

```json
{
  "assets": 9,
  "numpy": "2.5.2",
  "package": "marketmind",
  "pandas": "3.0.5",
  "periods": 2000,
  "python": "3.12.13",
  "scipy": "1.18.0",
  "scope": "controlled implementation audit; prospective outcomes remain sealed",
  "seed": 42,
  "step": 21,
  "version": "0.2.0",
  "window": 252
}
```

## Interpretation boundary

Passing means the tested code path obeyed the stated invariant in this deterministic environment. It does not prove that the MII predicts returns. Favorable, null, and adverse prospective outcomes remain sealed until the registered endpoint.
