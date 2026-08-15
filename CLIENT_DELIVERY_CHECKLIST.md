# MarketMind Client Delivery Checklist

A delivery is marked **READY** only when every applicable blocking item below is complete. Record `N/A` only with a reason.

## Release identity

- [ ] Exact MarketMind package version recorded.
- [ ] Full Git commit SHA recorded.
- [ ] Frozen client configuration included.
- [ ] Input dataset fingerprint recorded.
- [ ] Data retrieval timestamp and source recorded.
- [ ] Trading calendar and time-zone convention recorded.
- [ ] Execution lag, cost, slippage and annualization assumptions recorded.
- [ ] Random seeds recorded for stochastic procedures.
- [ ] Output manifest contains SHA-256 digests for delivered artifacts.

## Data QA

- [ ] Timestamps are monotonic and duplicates are resolved.
- [ ] Missingness is quantified by series.
- [ ] Adjustment convention is documented.
- [ ] Holiday/calendar alignment is documented.
- [ ] Stale observations are tested where relevant.
- [ ] Universe construction and exclusions are documented.
- [ ] Source licensing permits the intended analytical use and delivery.

## Temporal integrity

- [ ] Feature future-invariance test passes.
- [ ] Regime future-invariance test passes.
- [ ] Same-session execution is absent unless explicitly justified by timestamped execution data.
- [ ] Signal generation and realized-return timestamps are visibly separated.

## Benchmarks and robustness

- [ ] Buy-and-hold benchmark reported where applicable.
- [ ] Cash benchmark reported where applicable.
- [ ] Simple momentum/lagged-sign benchmark reported where applicable.
- [ ] Exposure-matched randomized/shuffled benchmark reported where applicable.
- [ ] Unconditional counterpart reported for regime-aware claims.
- [ ] Transaction-cost sensitivity reported.
- [ ] Material parameter sensitivities reported.
- [ ] Asset-universe/date-range sensitivity reported where decision-relevant.

## Statistical controls

- [ ] Estimand is explicitly stated.
- [ ] Effective sample size is reported.
- [ ] Dependence assumption or block size is reported.
- [ ] Confidence interval is reported for inferential claims.
- [ ] Number of tested specifications is disclosed.
- [ ] Multiple-testing correction or selection-risk control is applied where required.
- [ ] Null/adverse results remain visible.

## Claim control

- [ ] Every material number is mapped to a claim register entry.
- [ ] Every claim has a canonical evidence label.
- [ ] Synthetic evidence is not described as real-market validation.
- [ ] Internal tests are not described as independent reproduction.
- [ ] Informal feedback is not described as external review.
- [ ] Client data is not described as production evidence unless the engagement actually used it and disclosure is authorized.
- [ ] Prospective holdout status remains sealed where required.

## Reproducibility

- [ ] Clean-environment install instructions are present.
- [ ] Single run command or runbook is present.
- [ ] Environment dependencies are frozen or reconstructable.
- [ ] Machine-readable outputs accompany presentation outputs.
- [ ] Audit output accompanies the delivery.
- [ ] Manifest integrity has been verified after final file generation.

## Model risk

- [ ] Relevant entries from `MODEL_RISK_REGISTER.md` have been assessed.
- [ ] Critical risks are resolved or the analysis is explicitly delivered as failed/not decision-ready.
- [ ] High residual risks are prominently disclosed.
- [ ] Limitations are specific to this engagement rather than boilerplate.

## Sign-off

- [ ] Delivery status: `READY`, `READY WITH RESIDUAL RISK`, or `NOT DECISION-READY`.
- [ ] Analyst sign-off date recorded.
- [ ] Client-requested deviations recorded.
- [ ] Change log from the previous delivery included where applicable.
