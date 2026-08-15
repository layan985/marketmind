# MarketMind Client Assurance Protocol

This protocol defines the minimum evidence required before a MarketMind analysis is presented as client-ready. It governs research delivery, not investment advice. A client engagement may add stricter requirements, but it may not waive the controls below without a written deviation.

## 1. Decision boundary

MarketMind is an inspectable market-regime research system. It measures memory, information flow, connectivity, network structure, regime state and strategy behavior under explicit assumptions. It does not guarantee return predictability, profitability, execution quality or future regime persistence.

Every client output must distinguish:

- observed market measurements;
- controlled synthetic validation;
- public-data results;
- prospective evidence;
- production-client evidence;
- external review or independent reproduction.

The canonical evidence labels in `PROOF_LEDGER.md` are mandatory. No substitute badge vocabulary may be introduced in client materials.

## 2. Release identity

Every client delivery must identify the exact analytical state used to produce it:

| Field | Required value |
| --- | --- |
| Package version | Semantic version from the installed package |
| Git revision | Full commit SHA |
| Configuration | Machine-readable frozen configuration |
| Input fingerprint | SHA-256 or equivalent deterministic fingerprint of the analytical input |
| Retrieval timestamp | UTC timestamp for every external data pull |
| Data source | Vendor or public-source identifier |
| Calendar/time zone | Explicit trading calendar and time-zone convention |
| Execution assumptions | Lag, costs, slippage and annualization |
| Randomness | Seed and generator settings for every stochastic procedure |
| Output manifest | File name, byte size and SHA-256 for every delivered analytical artifact |

A result without this identity block is a working result, not a client result.

## 3. Client acceptance gates

All applicable gates must pass before delivery. A failed gate must remain visible and must not be converted into a pass by changing the reporting threshold after the result is known.

### Gate A — Data provenance and temporal integrity

Required evidence:

1. source and retrieval record for every input series;
2. adjustment convention for prices, corporate actions and missing observations;
3. duplicate, non-monotonic timestamp and impossible-value checks;
4. explicit treatment of holidays, stale quotes and market-calendar mismatches;
5. a fingerprint of the exact frame used by the model;
6. confirmation that only information available by the stated decision time enters each feature.

Minimum pass condition: no unresolved critical provenance or timestamp defect.

### Gate B — Look-ahead and execution integrity

Required evidence:

1. feature future-invariance check;
2. regime-threshold future-invariance check;
3. one-session or explicitly stated execution lag;
4. no same-session position from a same-session signal unless the client has supplied a justified executable timestamp contract;
5. cost and slippage assumptions applied to turnover rather than only to terminal returns.

Minimum pass condition: zero earlier-output changes under the registered future-only perturbation tolerance and execution behavior matching the documented contract.

### Gate C — Benchmark discipline

Every strategy or regime-conditioned performance result must be shown against relevant non-complex alternatives. At minimum, where applicable:

- buy and hold;
- cash;
- lagged-sign or simple momentum reference;
- exposure-matched shuffled signal;
- unconditional version of the same signal family;
- transaction-cost sweep.

A sophisticated result is not client-ready if a materially simpler comparator explains the same result and that fact is omitted.

### Gate D — Statistical uncertainty

Where inference is reported, the delivery must specify:

- estimand;
- sample and effective sample size;
- resampling or asymptotic procedure;
- block length or dependence assumption;
- confidence level;
- multiplicity correction where several hypotheses are tested;
- sensitivity to reasonable alternative parameters.

Point estimates without their uncertainty contract must not be described as validated effects.

### Gate E — Multiple-testing and selection risk

If more than one strategy, parameterization or market is examined, the delivery must disclose the search set and use an appropriate control such as a reality check, deflated Sharpe probability, preregistered family comparison or another explicitly justified method.

Minimum pass condition: the client can reconstruct how many opportunities existed to obtain a favorable result.

### Gate F — Stability and perturbation

The analyst must test whether the decision materially changes under reasonable perturbations to at least the relevant subset of:

- estimation window;
- step frequency;
- entropy discretization or nearest-neighbor settings;
- network threshold or construction choice;
- transaction costs;
- slippage;
- missing-data handling;
- asset universe;
- start/end date;
- seed for stochastic procedures.

A result that changes sign or interpretation under small plausible perturbations must be labeled unstable.

### Gate G — Reproducible bundle

A clean rerun must be possible from the delivered configuration and permitted data inputs. The bundle must include:

- environment specification;
- run command;
- frozen configuration;
- input fingerprint;
- raw and normalized analytical outputs;
- audit output;
- artifact manifest;
- limitations register.

Where raw data cannot legally be redistributed, the bundle must contain retrieval instructions and a fingerprint of the non-redistributable input.

### Gate H — Claim discipline

Every material number in the executive report must be traceable to one row of the proof ledger or to an engagement-specific claim register containing the same fields:

`CLAIM → NUMBER → EVIDENCE LABEL → SOURCE → DATE → CODE/RECORD → REPRODUCIBLE? → LIMITATION → STATUS`

No client document may imply `EXTERNAL REVIEW`, `INDEPENDENT REPRODUCTION` or `PRODUCTION CLIENT DATA` unless that evidence actually exists for the claim.

## 4. Mandatory client delivery bundle

A complete high-assurance engagement should contain the following, scaled only where a component is genuinely not applicable:

1. `EXECUTIVE_DECISION_MEMO.pdf` or equivalent client report;
2. `CLAIM_REGISTER.csv`;
3. `INPUT_MANIFEST.csv`;
4. `CONFIG.yml`;
5. `RUN_METADATA.json`;
6. `QA_REPORT.md`;
7. `BASELINE_MATRIX.csv`;
8. `SENSITIVITY_MATRIX.csv`;
9. `MODEL_RISK_REGISTER.md`;
10. `LIMITATIONS.md`;
11. machine-readable analytical outputs;
12. `artifact_manifest.json` with SHA-256 digests;
13. reproducibility instructions;
14. change log from the previous client delivery, if one exists.

The client-facing report is therefore the top layer of a verifiable evidence package, not a detached presentation.

## 5. Severity and sign-off

Findings use four operational severities:

| Severity | Meaning | Delivery rule |
| --- | --- | --- |
| Critical | Could invalidate the analytical conclusion or temporal contract | Block delivery until resolved or explicitly delivered as a failed analysis |
| High | Could materially alter magnitude, sign or decision | Must be resolved or prominently accepted in writing |
| Medium | Limits interpretation or portability | Must be disclosed with mitigation |
| Low | Presentation, convenience or minor robustness issue | Track; does not block delivery |

A delivery sign-off must state which gates passed, which were not applicable and which residual risks remain open.

## 6. Change control

Any change to feature definitions, regime logic, estimator implementation, execution timing, cost treatment, benchmark set or confirmatory hypothesis after a client baseline has been established must be recorded with:

- previous behavior;
- new behavior;
- reason for the change;
- affected claims;
- migration or comparability consequence;
- rerun requirement.

A methodological change and a bug fix are not interchangeable descriptions.

## 7. Evidence escalation path

MarketMind separates levels of evidence instead of collapsing them into a single claim of validity:

1. implementation invariant;
2. controlled known-structure synthetic recovery;
3. real public-data execution;
4. external methodological/code review;
5. independent reproduction;
6. production-client evidence;
7. prospective confirmatory result where preregistered.

Passing one level does not silently grant the next.

## 8. Stop conditions

The analysis must stop and be re-scoped when any of the following is true:

- timestamp provenance cannot establish what was knowable at decision time;
- the result depends on a data license that does not permit the required use;
- the result cannot survive a clean rerun;
- the reported advantage disappears under the agreed cost range and the client objective requires executable performance;
- a critical look-ahead, survivorship or universe-construction defect is unresolved;
- a requested claim would exceed the evidence label supported by the record.

These are research-integrity controls, not presentation preferences.
