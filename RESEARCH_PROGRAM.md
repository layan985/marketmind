# MarketMind Research Program

## Mission

MarketMind Research develops inspectable quantitative research infrastructure for studying market organization, temporal dependence, directional information flow, cross-asset networks, and regime measurement.

The core research question is not whether a complicated index can be made to look predictive. It is whether structural measurements behave correctly under known conditions, remain causal under time ordering, survive perturbation, add information beyond simpler models, and produce claims that another researcher can reproduce.

## Program 1 — Market Memory & Persistence

**Question:** How does temporal dependence vary through time and across market states?

Primary objects include DFA Hurst estimates, fractal dimension, absolute-return dependence, estimator stability, scale sensitivity, and known-answer synthetic processes.

Required validation includes short-sample stress tests, noise sensitivity, structural breaks, rolling-window sensitivity, and comparison with simpler persistence summaries.

## Program 2 — Information Flow

**Question:** When and where does directional information transmission strengthen?

Primary objects include entropy, mutual information, transfer entropy, lag structure, common-driver confounding, nonlinear coupling, changing coupling, and estimator uncertainty.

A positive directional statistic is never sufficient by itself. Known source→target, null, bidirectional, confounded, and noise-dominated systems must all be tested.

## Program 3 — Market Networks

**Question:** How does cross-asset dependence reorganize through time?

Primary objects include correlation strength, weighted clustering, correlation-distance minimum-spanning trees, eigenvalue concentration, centrality, and network-state stability.

The program explicitly tests metric redundancy. If two nominally sophisticated metrics carry effectively the same information, that is a result to publish rather than conceal.

## Program 4 — Regime Measurement & Validation

**Question:** Can the structural measurements above yield stable, leakage-resistant, useful regime classifications?

The program tests persistence, turnover, future-outcome separation where prespecified, perturbation sensitivity, computational cost, threshold stability, and comparative performance against strong conventional alternatives.

## Research objects

MarketMind produces six classes of inspectable object:

1. **Research** — papers, methods notes, benchmark studies, application studies.
2. **Software** — versioned Python releases and executable research workflows.
3. **Validation** — controlled audits, red-team reports, reproductions, external methodological reviews.
4. **Data** — versioned synthetic and public benchmark datasets with provenance.
5. **Benchmarks** — frozen comparisons against appropriate conventional methods.
6. **Institutional research** — bespoke reproducible research performed under the same integrity rules.

## Publication IDs

- `MM-RP-*` — research papers.
- `MM-BENCH-*` — benchmark studies.
- `MM-MN-*` — methods notes.
- `MM-VAL-*` — validation reports.
- `MM-APP-*` — research applications.
- `MM-DATA-*` — datasets.

## Interpretation discipline

MarketMind does not claim that complexity is inherently informative, that MII is uniquely correct, that a retrospective result confirms a prospective hypothesis, or that a benchmark is won before a frozen comparison is run.

The research program is allowed to delete components, reduce weights, reject hypotheses, publish nulls, and document conditions where simpler methods dominate.
