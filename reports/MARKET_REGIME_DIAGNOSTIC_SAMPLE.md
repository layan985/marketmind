# MarketMind — Market Regime Diagnostic Sample

**Status:** controlled implementation evidence; prospective holdout sealed.

## Audit result

MarketMind v0.2.0 passes **7/7 controlled checks**. This is not a profitability claim.

| Check | Observed statistic | Result |
| --- | ---: | --- |
| Connectivity recovery — clustering | 0.878759 correlation | PASS |
| Connectivity recovery — mean correlation | 0.889022 | PASS |
| Connectivity recovery — MST coherence | 0.901451 | PASS |
| Future perturbation effect on earlier raw metrics | 0.0 max absolute difference | PASS |
| Earlier regime rows unchanged | 350 / 350 | PASS |
| Source→target transfer-entropy margin | +1.21798 nats | PASS |
| Same-session position | 0.0 | PASS |
| Result files hash verified | 4 / 4 | PASS |

## Interpretation

The controlled audit shows that the tested implementation can recover disclosed synthetic structure, rejects future-information leakage in the tested paths, recovers a known directional-information relationship, respects the preregistered one-session execution timing rule, and reproduces declared result files exactly.

It does **not** establish that the Market Intelligence Index predicts returns.

## Prospective boundary

The confirmatory holdout runs from **10 August 2026 through 6 August 2027**. Its performance remains sealed until the registered endpoint. Favorable, null and adverse outcomes remain possible.

## Institutional diagnostic package

A commissioned diagnostic can return:

- memory, information-flow and connectivity diagnostics;
- network and regime-transition reports;
- normalization and threshold sensitivity;
- future-perturbation/look-ahead checks;
- timing and execution-lag checks;
- benchmark and transaction-cost sensitivity where relevant;
- reproducible configuration, output hashes and a limitations statement.

## Evidence rule

Every headline result must identify whether it comes from controlled synthetic validation, historical development evidence, public proxy data, an external reproduction, or the future prospective holdout. These categories must never be blended.