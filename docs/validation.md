# Validation

MarketMind's publication strategy is **external use and falsifiable validation before JOSS**.

This page is the permanent public ledger for two distinct questions:

1. **Do independent researchers actually use and exercise the software?**
2. **Does the preregistered MarketMind regime-to-signal mapping survive a future holdout?**

Evidence is recorded whether it is favorable, null, adverse, or inconvenient. GitHub stars, private praise, self-authored issues, and unverified claims do not count as adoption evidence.

## External-adoption scorecard

Target window: **9 August 2026 through 9 February 2027**.

| Evidence target | Goal | Verified now | Counting rule |
| --- | ---: | ---: | --- |
| Independent installs / research uses | 5 | 0 | Five distinct non-author users with a named public person, lab, course, project, or repository and a verifiable use record. |
| Genuine non-author issues | 3 | 0 | Opened by accounts other than `layan985`; author tracking issues do not count. |
| Outside pull request | 1 | 0 | Substantive non-author PR reviewed and merged. |
| Independent technical reproduction | 1 | 0 | Fresh-environment reproduction with version/commit, environment, commands, outputs, and outcome publicly recorded. |
| Seminar / research demo | 1 | 0 | Public event record plus durable slides, notebook, recording, or equivalent artifact. |
| Outside research project using MarketMind | 1 | 0 | Public notebook, repository, preprint, paper, teaching object, or analysis that actually imports/uses MarketMind and records the version or DOI. |
| Prospective holdout report published | 1 | 0 | Final preregistered results published after the 6 August 2027 endpoint regardless of sign or statistical significance. |

The machine-readable adoption ledger lives at [`validation/adoption-evidence.csv`](https://github.com/layan985/marketmind/blob/main/validation/adoption-evidence.csv). External researchers can use the repository's **Research use report** or **Replication report** issue templates to create inspectable evidence.

## Frozen prospective validation

**Protocol:** *Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis*

- Frozen package: `marketmind==0.1.0`
- Frozen source commit: `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`
- Holdout: **10 August 2026 through 6 August 2027 inclusive**
- Primary markets: `^GSPC`, `^NDX`, `^STOXX50E`, `ES=F`
- Connectivity panel additions: `^VIX`, `XLK`, `XLF`, `XLV`, `XLE`
- Data adapter: `yfinance`
- Frozen acquisition config: [`config/preregistered-validation-2026.yml`](https://github.com/layan985/marketmind/blob/main/config/preregistered-validation-2026.yml)
- Preregistration: [`preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md`](https://github.com/layan985/marketmind/blob/main/preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md)
- Deviation log: [`preregistration/DEVIATIONS.csv`](https://github.com/layan985/marketmind/blob/main/preregistration/DEVIATIONS.csv)

### Frozen hypotheses

**H1 — primary.** The regime-aware strategy has a higher net annualized Sharpe ratio than the unconditional equal-weight ensemble of all nine preregistered technical signals.

**H2a.** Trend-family returns are higher in High-MII observations than in pooled Medium/Low-MII observations.

**H2b.** Breakout/volatility-expansion-family returns are higher in Medium-MII observations than in pooled High/Low-MII observations.

**H2c.** Mean-reversion-family returns are higher in Low-MII observations than in pooled High/Medium-MII observations.

**H3.** The regime-aware strategy has a higher net annualized Sharpe ratio than buy-and-hold.

The preregistered mapping is fixed:

- **High MII → trend**
- **Medium MII → breakout / volatility expansion**
- **Low MII → mean reversion**

No parameter may be selected on the 2026–2027 holdout sample.

## Benchmarks

### Confirmatory benchmarks

1. **Unconditional nine-signal ensemble** — arithmetic mean of all nine long-only signal exposures, independent of MII state. This is the H1 comparator.
2. **Buy-and-hold** — unit exposure whenever a valid market return exists. This is the H3 comparator.

### Prespecified robustness benchmarks

- cash;
- lag-sign;
- exposure-matched shuffled signals;
- gross-return results;
- transaction-cost sweep at 0, 5, 10, and 25 bps per unit turnover;
- moving-block intervals with 5-, 10-, and 20-session blocks, with 20 primary.

Robustness checks cannot replace or redefine the primary H1 decision rule.

## Transaction costs and execution assumptions

These assumptions are frozen for the confirmatory analysis:

| Assumption | Frozen value |
| --- | --- |
| Signal direction | Long-only |
| Leverage | None |
| Signal timing | Date-*t* close information can affect a position no earlier than session *t+1* |
| Regime timing | MII regime labels use the same one-session execution lag |
| Turnover | Absolute change in position |
| Primary transaction cost | **5 bps per unit of turnover**, charged on every position change |
| Primary Sharpe convention | 252 sessions/year, zero daily risk-free rate |
| Primary bootstrap | Synchronized moving-block bootstrap, block length 20, 10,000 replications |
| Bootstrap seed | `20260807` |
| Optional stopping | Forbidden |
| Post-hoc parameter optimization | Forbidden in confirmatory analysis |

## Prospective scoreboard

!!! warning "No interim confirmatory performance"
    The preregistration states that confirmatory outcome statistics for the prospective window will not be computed until the final scheduled observation has been collected. A live Sharpe ratio, p-value, or winner/loser display would create an interim-analysis channel and weaken the holdout. This scoreboard therefore reports **protocol and collection status only** until the endpoint.

| Item | Live status |
| --- | --- |
| Holdout start | 10 August 2026 |
| Holdout end | 6 August 2027 |
| Status as of 13 August 2026 | **Active / protocol frozen / outcomes sealed** |
| Eligible confirmatory observations collected | Not reported during the sealed holdout |
| Registered deviations | 0 |
| Interim H1/H2/H3 performance | **Sealed — not computed** |
| Final results commitment | Publish regardless of favorable, null, or adverse outcome |

## Controlled implementation audit

The prospective outcome is sealed, but implementation invariants can be tested without
touching that outcome. The frozen v0.2.0 controlled audit passes 7/7 checks covering
deterministic replay, recovery of disclosed synthetic coherence, feature and threshold
look-ahead perturbations, directional information recovery, exact signal-family selection,
next-session execution, and SHA-256 artifact integrity.

The full [audit report](https://github.com/layan985/marketmind/blob/main/validation/audit-v0.2.0/AUDIT.md)
publishes each acceptance criterion and observed statistic. These checks do not test
whether the prospective trading hypothesis succeeds.

After the holdout closes, this table will be replaced or extended with the preregistered point estimates, confidence intervals, observation counts, exposure, turnover, drawdowns, multiplicity-adjusted H2 inference, and benchmark comparisons. The result will remain public even if MarketMind fails its primary hypothesis.

## Negative results and failures

Negative evidence is part of the validation record, not something to hide.

**Currently published:** none yet.

When they occur, this section will retain links to:

- failed or partial independent installations;
- numerical discrepancies found by external reproducers;
- confusing or incorrect API behavior;
- non-author issues that reveal genuine limitations;
- null or adverse prospective hypotheses;
- robustness results that weaken the main interpretation;
- deviations from the preregistered protocol.

A negative result may be fixed in later software versions, but the original evidence remains in the public history. The machine-readable ledger is [`validation/negative-results.csv`](https://github.com/layan985/marketmind/blob/main/validation/negative-results.csv).

## What counts as progress

MarketMind should improve because outsiders use it, challenge it, reproduce it, or find problems. The preferred next changes are therefore installation/documentation fixes, stronger reference tests, research examples, diagnostics, provenance improvements, and API clarifications that are traceable to real external evidence.

JOSS is a later publication target. It is not being used as a substitute for adoption, sustained public development, or research impact.
