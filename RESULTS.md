# Results status

Last updated: 13 August 2026.

| Question | Status | What can be said now |
| --- | --- | --- |
| Do the paper's regime-to-signal rules work prospectively? | Active; outcome sealed | The holdout opened on 10 August 2026. Interim confirmatory statistics are not computed or reported. |
| Does the implementation pass controlled integrity checks? | Yes, within stated scope | The v0.2.0 audit passes 7/7 deterministic checks; this is not evidence of return predictability. |
| Can the public proxy reproduce the paper numerically? | No | Bloomberg and Refinitiv inputs cannot be redistributed. The public pipeline tests the method with substitute histories. |
| Has someone outside the project reproduced a result? | Not yet | No outside reproduction is recorded. |
| Is MarketMind used in an outside research project? | Not yet | No outside use is recorded. |

The paper's development and validation results motivated the registered test, but they do not answer the prospective question. Positive, null, and negative holdout results will be reported under the same frozen rules.

The controlled audit is published at [validation/audit-v0.2.0/AUDIT.md](validation/audit-v0.2.0/AUDIT.md). It tests reproducibility, known-structure recovery, look-ahead invariance, directionality, execution timing, and artifact integrity. It deliberately does not compute a prospective Sharpe ratio or hypothesis result.

The machine-readable negative-results log is [validation/negative-results.csv](validation/negative-results.csv). It is currently empty because the confirmatory period has just begun, not because every hypothesis succeeded.
