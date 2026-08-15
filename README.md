# MarketMind Research

[![CI](https://github.com/layan985/marketmind/actions/workflows/ci.yml/badge.svg)](https://github.com/layan985/marketmind/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/marketmind.svg)](https://pypi.org/project/marketmind/)
[![Python](https://img.shields.io/pypi/pyversions/marketmind.svg)](https://pypi.org/project/marketmind/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21844956.svg)](https://doi.org/10.5281/zenodo.21844956)
[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](LICENSE)

**Open research infrastructure for measuring market organization, regimes, and information dynamics.**

MarketMind Research studies how memory, information flow, and cross-asset dependence reorganize through time. The software is one part of the program. The larger object is an inspectable research workflow: explicit timing contracts, frozen specifications, controlled audits, public datasets, benchmark studies, replication records, methodological review, and prospective tests.

MarketMind does **not** claim to predict markets by virtue of complexity. It is designed to make quantitative market-structure claims easier to inspect, challenge, reproduce, and falsify.

## Current status

As of 16 August 2026:

| Object | Status |
| --- | --- |
| Research implementation | `v0.2.0` |
| Frozen prospective implementation | `v0.1.0` |
| Test suite | 29 passing tests; 83.06% branch-aware coverage in the recorded source environment |
| Controlled research audit | 7/7 checks passed |
| Future-only perturbation | 0 / 350 earlier regime rows changed |
| Prospective holdout | **SEALED** through 6 August 2027 |
| Independent reproductions | **0** |
| External methodological reviews | **0** |
| Recorded outside research applications | **0** |

Zeroes are reported deliberately. A reproduction, review, application, or institutional use is not counted until an evidence record exists in `registry/`.

## Research programs

1. **Market Memory & Persistence** — how temporal dependence changes across market states.
2. **Information Flow** — when directional information transmission strengthens, weakens, or becomes confounded.
3. **Market Networks** — how cross-asset dependence and network structure reorganize.
4. **Regime Measurement & Validation** — whether structural measurements yield stable, useful, leakage-resistant regime classifications.

See [RESEARCH_PROGRAM.md](RESEARCH_PROGRAM.md).

## Verification snapshot

| Controlled check | Frozen v0.2.0 result |
| --- | ---: |
| Connectivity metrics vs. disclosed trailing latent coherence | 0.879–0.901 correlation |
| Earlier raw-metric change after a future-only perturbation | 0.0 max absolute difference |
| Earlier regime rows changed after a future-only perturbation | 0 / 350 |
| Known source→target minus reverse transfer entropy | +1.218 nats |
| Same-session position under the confirmatory contract | 0.0 |
| Hash-verified result files | 4 / 4 |

Reproduce the controlled evidence pack:

```bash
marketmind audit --output artifacts/research-audit
```

The committed [audit report](validation/audit-v0.2.0/AUDIT.md) defines acceptance rules, observed statistics, environment information, and interpretation boundaries. It is controlled implementation evidence, not a profitability claim.

## Benchmark program

MarketMind now maintains frozen study specifications before comparative results are interpreted:

- `MM-BENCH-001` — multiscale regime discrimination versus simpler regime models.
- `MM-BENCH-002` — leakage-resistance laboratory.
- `MM-BENCH-003` — network-metric stability and redundancy.
- `MM-BENCH-004` — directional-information validation under known synthetic structures.

Specifications live in [`benchmarks/`](benchmarks/README.md). Results are not entered into the registry until the corresponding study artifact is frozen.

## Red team

[`validation/RED_TEAM_PROTOCOL.md`](validation/RED_TEAM_PROTOCOL.md) defines adversarial checks for look-ahead leakage, timestamp leakage, normalization leakage, label instability, short-sample instability, outliers, missingness, parameter sensitivity, universe sensitivity, survivorship assumptions, transaction costs, timing, frequency, market selection, and random seeds.

A release can pass ordinary tests and still fail a research-integrity check. Those are different claims.

## Prospective holdout

The confirmatory study runs from **10 August 2026 through 6 August 2027**. Historical data may initialize trailing estimators but cannot contribute confirmatory performance observations. The frozen implementation is `marketmind==0.1.0`, frozen source commit `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`.

The acquisition configuration has SHA-256 fingerprint:

`443e914e87929f95fc53531cfb2fd0969dd424b2cd843654d345d79d2d2303be`

Current result status: **SEALED**.

See [HOLDOUT_GOVERNANCE.md](HOLDOUT_GOVERNANCE.md) and the [preregistration](preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md). Interim confirmatory performance is not exposed.

## Method

MII combines three groups of measurements:

| Component | Measurements | Weight |
| --- | --- | ---: |
| Memory | DFA Hurst exponent, Higuchi fractal dimension, absolute-return ACF decay | 0.35 |
| Information flow | Shannon entropy, Kraskov mutual information, transfer entropy | 0.40 |
| Connectivity | Correlation strength, weighted clustering, correlation-distance MST | 0.25 |

Sophistication is not treated as evidence by itself. The benchmark program asks whether components are stable, redundant, robust, and useful compared with simpler alternatives.

## Research registries

The public truth source is machine-readable:

- [`registry/studies.json`](registry/studies.json)
- [`registry/datasets.json`](registry/datasets.json)
- [`registry/releases.json`](registry/releases.json)
- [`registry/replications.json`](registry/replications.json)
- [`registry/reviews.json`](registry/reviews.json)
- [`registry/applications.json`](registry/applications.json)
- [`registry/publications.json`](registry/publications.json)
- [`registry/deviations.json`](registry/deviations.json)
- [`registry/benchmarks.json`](registry/benchmarks.json)

CI validates the registry structure. Public counters should resolve to these files rather than hand-maintained marketing numbers.

## Independent reproduction and review

A rerun is not called an independent reproduction until it records the reproducer, exact release and commit, environment, exact command, expected and observed outputs, numerical tolerance, differences, issues, and resolution. A methodological review is separate: reviewers are asked to challenge bounded claims rather than endorse the project.

Templates and standards are in [`validation/`](validation/).

## Negative results

MarketMind has a permanent [Negative Results & Failed Claims](NEGATIVE_RESULTS.md) ledger. Failures, instability regions, unsupported hypotheses, and benchmark losses belong there. A failed prospective hypothesis does not invalidate the software as research infrastructure; suppressing that failure would.

## Research applications

External use is counted when a researcher actually runs MarketMind on a defined research question and leaves a reproducible record. The application series uses IDs such as `MM-APP-001` and records release, configuration, data, question, outputs, limitations, and citation.

See [`research_applications/README.md`](research_applications/README.md).

## Institutional research

Commercial work is separated from scientific claims. The two flagship scopes are:

- **Quant Research Integrity Audit** — timing, normalization, labels, feature availability, execution, costs, multiple testing, validation, holdout contamination, and artifact reproducibility.
- **Market Structure Study** — memory, information flow, network structure, regime analysis, sensitivity, conventional-model comparison, and a reproducible package.

See [`institutional/`](institutional/README.md). No investment-return promise is part of these scopes.

## Install

```bash
pip install marketmind
```

```python
from marketmind import MarketMind, MarketMindConfig
from marketmind.synthetic import synthetic_market

prices = synthetic_market(periods=1_500, assets=8, seed=42)
model = MarketMind(MarketMindConfig(window=252, step=21))
result = model.fit_transform(
    prices[["SPX", "NDX", "SX5E", "ES"]],
    network_data=prices,
)
print(result.to_frame().tail())
```

## Research software publication path

MarketMind is intentionally **not** presented as publication-ready merely because it has tests and documentation. Readiness requires sustained public development, genuine research use, iterative releases, and evidence that other researchers can install and interrogate it. The live gap assessment is in [JOSS_READINESS.md](JOSS_READINESS.md).

## Citation and license

> Oraidi, L. (2026). *MarketMind: Multiscale Market Intelligence Research Software* (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.21844956

BSD 3-Clause. MarketMind is research software, not an execution engine or investment recommendation.
