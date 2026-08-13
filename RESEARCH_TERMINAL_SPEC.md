# MarketMind Research Terminal

## AWARD-WINNING THEORY. OPEN IMPLEMENTATION. FROZEN PROSPECTIVE TEST.

### Status strip

| Field | Current public status | Evidence class |
| --- | --- | --- |
| Frozen preregistration release | v0.1.0 | `FOUNDER PRODUCED` |
| Current controlled implementation | v0.2.0 | `FOUNDER PRODUCED` |
| PyPI | published | `EXTERNALLY VERIFIED` |
| Zenodo DOI | 10.5281/zenodo.21844956 | `EXTERNALLY VERIFIED` |
| CI tests | 29 passing | `FOUNDER PRODUCED` |
| Controlled audit | 7 / 7 checks passing | `FOUNDER PRODUCED` |
| Holdout start | 10 Aug 2026 | `EXTERNALLY VERIFIED` + `FOUNDER PRODUCED` |
| Holdout end | 6 Aug 2027 | `EXTERNALLY VERIFIED` + `FOUNDER PRODUCED` |
| Holdout result | NOT YET AVAILABLE | `PENDING VALIDATION` |
| Independent reproductions | 0 | `PENDING VALIDATION` |

Full claim-level detail: [PROOF_LEDGER.md](PROOF_LEDGER.md).

## Product contract

MarketMind should behave like a research terminal, not a trading-signal vending machine.

**choose market → choose window → calculate memory → information flow → connectivity → regime → uncertainty → diagnostics → export report**

The interface should always keep raw components and uncertainty visible before any composite interpretation.

## Core visual objects

1. **Market-memory history** — Hurst / fractal / persistence measurements through time.
2. **Information-transfer network** — directional information relationships with estimation window and method visible.
3. **Connectivity matrix** — correlation/network structure, not a black-box score.
4. **Regime timeline** — classification plus the thresholds and training window used at each date.
5. **Walk-forward diagnostics** — exact train/evaluation windows and timing convention.
6. **Transaction-cost sensitivity** — cost assumptions shown, never hidden.
7. **Benchmark comparison** — unconditional and simpler-model baselines.
8. **Preregistration timeline** — frozen release, registration, holdout start/end, deviations.
9. **Live frozen-test clock** — time status only; no interim performance leakage.
10. **Deviations ledger** — every post-registration change with impact classification.
11. **External reproduction scoreboard** — zero until a qualifying outside rerun is documented.

## Visual footer contract

Every chart and table should show:

**SOURCE / N / WINDOW / FILTER / STATUS / LIMITATION / DOWNLOAD DATA**

Where a result is produced from known-structure data, show `SYNTHETIC`. Where the paper cannot be exactly reproduced because Bloomberg/Refinitiv histories cannot be redistributed, state that next to the relevant public-data result rather than in a distant disclaimer.

## Exported market diagnostic

The commercial output should be a research diagnostic, not investment advice. A client-facing report can contain:

- market panel and data provenance;
- memory diagnostics;
- information-flow diagnostics;
- connectivity structure;
- regime classification and uncertainty;
- sensitivity to window length, thresholds, and costs;
- benchmark comparisons;
- failure modes and limitations;
- reproducible configuration and artifact hashes.

### Commercial action

**COMMISSION A MARKET DIAGNOSTIC**

Scope it as a bounded research engagement with specified markets, dates, data rights, methods, deliverables, exclusions, and reproducibility package. Never sell an unobserved prospective holdout as performance evidence.
