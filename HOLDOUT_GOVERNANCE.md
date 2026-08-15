# Prospective Holdout Governance

## Status

**SEALED**

No confirmatory performance result is published or used to alter the registered specification before the final scheduled observation.

## Frozen study record

| Field | Frozen value |
| --- | --- |
| Study | Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis |
| Plan prepared | 7 August 2026 |
| Holdout start | 10 August 2026 |
| Holdout end | 6 August 2027 |
| Frozen package | `marketmind==0.1.0` |
| Frozen source commit | `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97` |
| Acquisition config | `config/preregistered-validation-2026.yml` |
| Config SHA-256 | `443e914e87929f95fc53531cfb2fd0969dd424b2cd843654d345d79d2d2303be` |
| Primary hypothesis | H1: regime-aware strategy Sharpe exceeds unconditional nine-signal ensemble Sharpe |
| Primary cost | 5 bps per unit turnover |
| Execution lag | one session |
| Primary bootstrap | synchronized moving-block; length 20; 10,000 replications; seed 20260807 |
| Result status | SEALED |

## Market universe

Primary markets: `^GSPC`, `^NDX`, `^STOXX50E`, `ES=F`.

Connectivity panel additionally contains `^VIX`, `XLK`, `XLF`, `XLV`, and `XLE`.

## Confirmatory hypotheses

- **H1:** regime-aware strategy has a higher net annualized Sharpe ratio than the unconditional equal-weight nine-signal ensemble.
- **H2a:** trend-family return is higher in High-MII observations.
- **H2b:** breakout-family return is higher in Medium-MII observations.
- **H2c:** mean-reversion-family return is higher in Low-MII observations.
- **H3:** regime-aware strategy has a higher net annualized Sharpe ratio than buy-and-hold.

H1 is primary. H2a–H2c use Holm family-wise correction. H3 is secondary.

## Prohibited during seal

The following may not be used to modify the confirmatory specification:

- interim Sharpe ratios, returns, p-values, drawdowns, or performance plots;
- post-hoc threshold or weight changes prompted by holdout behavior;
- alternative signal selection based on holdout outcomes;
- revised exclusions motivated by adverse observations;
- hidden replacement of the frozen implementation.

## Permitted maintenance

Operational fixes that do not alter the frozen confirmatory computation may occur in later software releases, but the confirmatory analysis remains tied to the frozen release and source commit. Any unavoidable study deviation is entered in `preregistration/DEVIATIONS.csv` and `registry/deviations.json` before interpretation.

## Unsealing rule

After the 6 August 2027 session and final permitted data collection, the confirmatory analysis is run exactly as registered. The final package reports supported and unsupported hypotheses, point estimates, uncertainty, observation counts, costs, turnover, drawdowns, robustness checks, raw-data provenance, environment, code commit, and all deviations.

Null, adverse, or contradictory results are published under the same rule as favorable results.
