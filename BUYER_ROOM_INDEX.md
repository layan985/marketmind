# MarketMind Buyer Room Index

MarketMind is research software for inspectable market-regime analysis. This index is the assurance room a buyer, reviewer, or institutional user should inspect before relying on a MarketMind deliverable.

## Assurance controls
- [Client assurance protocol](CLIENT_ASSURANCE_PROTOCOL.md)
- [Client delivery checklist](CLIENT_DELIVERY_CHECKLIST.md)
- [Model risk register](MODEL_RISK_REGISTER.md)
- [Public benchmark protocol](PUBLIC_BENCHMARK_PROTOCOL.md)
- [Proof ledger](PROOF_LEDGER.md)
- [Results status](RESULTS.md)
- [Reproducibility](REPRODUCIBILITY.md)
- [Replication challenge](REPLICATION_CHALLENGE.md)

## Executable benchmark

The branch contains an institutional benchmark engine at `marketmind.benchmark.run_benchmark_bundle` plus the frozen specification `config/institutional-public-benchmark.yml`.

Given a supplied price panel, the engine produces a 14-artifact evidence bundle containing:

- fixed nine-signal benchmark results;
- buy-and-hold, cash, lagged-sign and exposure-matched-shuffle comparators;
- transaction-cost sweeps;
- moving-block Sharpe intervals;
- a family-level White-style reality check;
- deflated-Sharpe diagnostics;
- MII/regime outputs;
- input fingerprint and source metadata;
- QA and limitations reports;
- machine-readable claim register;
- run metadata;
- SHA-256 artifact manifest;
- client decision memo.

CI exercises the same bundle generator on a controlled fixture labeled `SYNTHETIC`. A public-provider run may be labeled `REAL PUBLIC DATA` only when the source record and exact analytical frame support that label. Tests do not manufacture public-data claims.

## Technical evidence
- [Research terminal specification](RESEARCH_TERMINAL_SPEC.md)
- [Methodology](docs/methodology.md)
- [Codebook](data/CODEBOOK.md)
- [Dataset release standard](data/DATASET_RELEASE_STANDARD.md)
- [Prospective protocol](preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md)
- [Deviations log](preregistration/DEVIATIONS.csv)

## Current public evidence state

The latest frozen evidence snapshot records:

- 29 passing implementation tests on the recorded v0.2.0 environment;
- 83.06% branch-aware coverage on that recorded environment;
- controlled research audit: 7/7 checks pass;
- future-only perturbation: 0/350 earlier regime rows changed;
- known directional-information test: +1.218 nats;
- artifact integrity: 4/4 declared result files hash verified;
- prospective holdout active through 6 August 2027;
- no public holdout result yet;
- zero recorded independent reproductions;
- zero completed external methodological/code reviews;
- zero recorded outside research uses;
- zero disclosed production-client datasets.

The benchmark machinery added on the assurance branch does not alter those frozen counts. A new historical public-data run becomes a new ledger entry only after the run actually exists and its artifacts are frozen.

These counts are deliberately not upgraded by internal reruns, informal feedback, repository traffic, stars, or client interest. The proof ledger is the authoritative claim register.

## What a client receives

A high-assurance engagement is not a dashboard screenshot. The expected bundle includes a decision memo, claim register, input manifest, frozen configuration, run metadata, QA report, baseline matrix, sensitivity matrix, model-risk register, limitations, machine-readable outputs, hash manifest, reproducibility instructions and a delivery-to-delivery change log where applicable.

Every applicable acceptance gate in the client assurance protocol must pass before a result is marked `READY`. Critical integrity failures block a decision-ready delivery; they are not hidden by changing thresholds or removing adverse outputs.

## Commercial boundary

Suitable paid work includes custom market diagnostics, data adapters, reproducible research builds, methods audits and institutional workshops. MarketMind does not sell a promise of profitability. Historical, synthetic, prospective, externally reviewed, independently reproduced and production-client evidence remain separate evidence classes.
