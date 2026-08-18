# MarketMind Model Risk Register

This register is the public baseline for risks inherent to MarketMind analyses. Engagement-specific risks should be added rather than replacing these entries.

| ID | Risk | Failure mode | Detection | Mitigation | Residual status |
| --- | --- | --- | --- | --- | --- |
| MR-01 | Look-ahead leakage | Future information enters features, regimes or execution | Future-only perturbation tests; timestamp audit | Trailing windows, shifted regime labels, explicit execution lag | Controlled test in place; external data timestamp quality remains engagement-specific |
| MR-02 | Data provenance error | Source, adjustment or vintage is misidentified | Input manifest, retrieval record, frame fingerprint | Preserve source metadata and exact input hash | Engagement-specific |
| MR-03 | Survivorship / universe bias | Asset set is conditioned on later survival or availability | Universe-construction review | Freeze universe rules ex ante; retain inclusion/exclusion log | Engagement-specific |
| MR-04 | Multiple testing | Favorable specification selected from many trials | Search-set disclosure; reality check; deflated Sharpe; preregistered comparisons | Report full tested family and corrected inference | Controlled methods available; application required per engagement |
| MR-05 | Regime instability | Small parameter changes alter state labels or conclusions | Sensitivity matrix | Report perturbation range and unstable regions | Engagement-specific |
| MR-06 | Transaction-cost misspecification | Apparent effect is not executable at realistic cost | Cost/slippage sweep | Use client-specific or conservative cost bands | Engagement-specific |
| MR-07 | Market impact omission | Larger notional changes achievable execution | Capacity review | Do not infer institutional capacity from friction-only backtests | Not modeled by default |
| MR-08 | Non-stationarity | Historical relationships decay or reverse | Rolling diagnostics; prospective evaluation | Treat relationships as conditional and time-varying | Inherent residual risk |
| MR-09 | Data snooping across markets | Cross-market selection inflates apparent evidence | Cross-market search-set disclosure | Family-wise inference or preregistered market set | Engagement-specific |
| MR-10 | Benchmark inadequacy | Complex method appears useful only because baseline is weak | Baseline matrix | Include simple, exposure-matched and unconditional comparators | Required client gate |
| MR-11 | Bootstrap dependence misspecification | Block size understates or overstates uncertainty | Block-length sensitivity | Report block size and sensitivity across plausible values | Engagement-specific |
| MR-12 | Metric interpretation | MII or network measure is treated as a trading recommendation | Report review and claim register | Separate measurement from decision rule; state evidence boundary | Required client gate |
| MR-13 | Reproducibility drift | Code/data/config changes make old result unrecoverable | Commit SHA, environment, manifest hashes | Freeze delivery identity and changelog | Required client gate |
| MR-14 | Vendor revision risk | External source revises historical observations | Retrieval timestamp and input fingerprint | Store permitted snapshots or exact fingerprints | Engagement-specific |
| MR-15 | Missing-data distortion | Fill/drop rules create artificial structure | Missingness report and alternative-treatment sensitivity | Explicit policy; no silent interpolation | Engagement-specific |
| MR-16 | Corporate-action distortion | Splits/dividends create spurious returns or network changes | Price-adjustment audit | State and verify adjustment convention | Engagement-specific |
| MR-17 | Calendar mismatch | Assets from different venues are compared on non-comparable sessions | Calendar/time-zone audit | Explicit session alignment and stale-price handling | Engagement-specific |
| MR-18 | Numerical instability | Estimator behaves poorly on degenerate or short samples | Unit tests, finite-value checks, perturbation tests | Input validation and minimum-history constraints | Controlled tests in place |
| MR-19 | Synthetic-to-real extrapolation | Controlled recovery is represented as real-market validation | Proof ledger evidence labels | Keep synthetic and real-data claims visibly separate | Required claim discipline |
| MR-20 | Prospective contamination | Registered holdout is inspected or altered mid-study | Sealed results boundary; deviation log | Do not expose interim outcome; record deviations | Active through registered end date |

## Engagement close-out

For every client delivery, append a section with:

- risks triggered by the engagement;
- severity;
- evidence reviewed;
- mitigation performed;
- residual risk accepted by the client or analyst;
- owner and date.
