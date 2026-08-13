# Controlled research audit

MarketMind includes a deterministic audit that challenges the implementation against
known structure and explicit invariants:

```bash
marketmind audit --output artifacts/research-audit
```

The command writes a human-readable report, a machine-readable report, the controlled
tracking table, a complete MII run, and SHA-256 manifests. It exits with a nonzero status
if any acceptance rule fails.

## Frozen v0.2.0 audit result

The repository's [`validation/audit-v0.2.0`](https://github.com/layan985/marketmind/blob/main/validation/audit-v0.2.0/AUDIT.md)
evidence pack records **7/7 passing controlled checks**:

| Check | Observed result |
| --- | --- |
| Deterministic replay | Identical input fingerprint |
| Known-structure recovery | Correlations of 0.879–0.901 with trailing latent coherence |
| Feature look-ahead | Maximum prior-metric difference: 0.0 after future perturbation |
| Regime look-ahead | 350/350 prior threshold rows unchanged |
| Directional information | Known direction exceeds reverse transfer entropy by 1.218 nats |
| Strategy contract | Exact regime-family selection and zero same-session position |
| Artifact integrity | All declared file sizes and SHA-256 hashes verified |

## What this establishes

The audit provides controlled evidence that the tested implementation:

- reproduces seeded inputs;
- responds to disclosed network coherence in the intended direction;
- does not allow future changes to rewrite earlier features or regime thresholds;
- recovers a known information-transfer direction;
- executes the preregistered High/Medium/Low signal-family map with the stated lag;
- produces result bundles whose numerical files are bound to their metadata.

## What this does not establish

The synthetic generator is not a calibrated market simulator. Passing these checks does
not establish predictive power, economic profitability, or prospective confirmation.
Those claims remain reserved for the sealed 10 August 2026–6 August 2027 holdout.
