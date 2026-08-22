# Regime Claim Audit (RCA)

## A falsification protocol for nonstationary time-series models

A detector saying that "the regime changed" is not yet a scientific interpretation. The phrase can refer to at least four different claims, and the evidence required for them is not interchangeable.

RCA is a claim-audit protocol. It does not award a single grand score. It asks what claim a model is trying to make, then subjects that claim to the smallest set of tests that could prove it wrong.

## The claim ladder

### C0 — Change detection
**Claim:** something in the observed stochastic process changed.

Required evidence:
- null false-positive calibration;
- power across break magnitudes;
- localization error / detection delay;
- stability to seed and sample length.

Passing C0 does **not** identify what changed.

### C1 — Observable-state attribution
**Claim:** a named observable feature changed — for example volatility, covariance, tail dependence, factor concentration, or a marginal distribution.

Required evidence:
- direct recovery of the named target in controlled data;
- rejection of alternative observable explanations;
- unit/representation checks appropriate to that target;
- robustness to outliers, missingness and sampling choices when those are outside the target definition.

Passing C1 does **not** establish a change in the data-generating mechanism.

### C2 — Mechanism-change attribution
**Claim:** the conditional or temporal propagation mechanism changed.

Required evidence:
- **silent mechanism shift:** mechanism changes while chosen state summaries are held fixed;
- **nuisance inversion:** observable state changes while the target mechanism is fixed;
- **proxy-collapse test:** simpler observable statistics are allowed to reproduce the result;
- **metamorphic invariance:** target-preserving reparameterizations should not materially alter the conclusion;
- a difficulty frontier rather than one favorable break magnitude.

Passing C2 does **not** by itself identify causal orientation.

### C3 — Directional / causal identification
**Claim:** a direction, structural edge, or intervention-relevant effect is identified.

Required evidence:
- observational-equivalence challenges;
- explicit identifying assumptions;
- abstention or equivalence-class output when those assumptions are insufficient;
- interventional, multi-environment, natural-experiment, or other identifying evidence when the target requires it;
- calibration of confidence near the identification boundary.

A method that always returns a direction cannot pass C3 on a benchmark containing genuinely non-identifiable cases.

## The claim ceiling

**Report no stronger interpretation than the strongest claim level whose required falsification tests pass.**

This is deliberately asymmetric. A model can be useful at C0 while failing C2. A volatility detector can be excellent at detecting a volatility state and still be the wrong instrument for a mechanism-change claim. A causal-discovery method can recover an observational equivalence class correctly without earning a unique orientation.

## Metamorphic validation

In real financial data, ground truth is usually unavailable. RCA therefore includes *metamorphic relations*: transformations of an input dataset that are known, by construction, to preserve the scientific target being claimed.

Examples include:
- positive diagonal unit reparameterization when the claim is coordinate-free existence/timing of a mechanism switch;
- column permutation when variable ordering has no semantic content;
- timestamp translation when only relative timing matters;
- transformations that preserve a specified conditional-independence target;
- nuisance injections that are explicitly outside the claimed mechanism.

A model is run on the original and follow-up dataset. If the target is preserved but the conclusion changes materially, the claim is representation-dependent.

Metamorphic relations must be declared **per claim**. A transformation that should preserve one estimand may legitimately change another.

## RCA-1 result: the benchmark caught its own baseline

The first RCA run audits the simple VAR-change baseline used in MMSMB-2.

Across 200 silent mechanism-shift replications:
- raw VAR coefficient-distance AUC: **0.804**;
- standardized VAR coefficient-distance AUC: **0.806**.

Both remain near chance on the Market Mirage nuisance track:
- raw VAR: **0.520**;
- standardized VAR: **0.520**.

Then each variable is independently rescaled by a fixed positive factor for the entire dataset. The mechanism-switch existence and timing are unchanged.

For the **raw** VAR Frobenius score:
- mean original/transformed score-rank correlation: **0.328**;
- mean absolute change in AUC: **0.220**.

For the **per-window standardized** VAR score:
- score-rank correlation: **1.000**;
- mean absolute AUC change: **0.000** (numerical tolerance).

The important result is not that standardization is sophisticated. It is the opposite: a benchmark should be capable of revealing that a promising structural score depends on arbitrary coordinate scale, and the correction should be simpler than the story built around the uncorrected result.

## Reporting template

Every RCA result should report:

1. **Claim** — exact sentence the model wants to support.
2. **Estimand** — mathematical/statistical object that sentence refers to.
3. **Observable inputs** — information made available to the method.
4. **Falsification worlds** — controlled cases that should trigger the claim.
5. **Nuisance worlds** — cases that should not trigger it.
6. **Metamorphic relations** — target-preserving transformations.
7. **Identification boundary** — cases where the target is not uniquely recoverable.
8. **Simple baselines** — cheapest competing explanations.
9. **Failure record** — adverse results remain public.
10. **Claim ceiling** — C0, C1, C2, or C3.

## Scope

RCA is currently a research protocol, not an industry standard and not a certification framework. The first implementation is built around synthetic multivariate financial time series, but the logic is applicable to nonstationary time-series models in other domains where "change," "state," and "mechanism" are easy to conflate.
