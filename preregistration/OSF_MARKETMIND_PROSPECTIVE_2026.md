# OSF Preregistration — MarketMind Prospective Validation 2026–2027

**Status:** Public pre-analysis plan prepared 7 August 2026. The prospective evaluation window begins 10 August 2026. This GitHub file is a public, versioned pre-analysis plan; it is not a substitute for submitting the same plan to the OSF Registry before the evaluation window begins.

**Frozen software:** `marketmind==0.1.0`

**Frozen source commit:** `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`

**Prospective evaluation window:** 10 August 2026 through 6 August 2027 inclusive.

---

## Study Information

### Title

**Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis**

### Authors

Layan Oraidi. ORCID will be linked in OSF metadata when the registration is submitted.

### Description

This study prospectively evaluates whether the Market Intelligence Index (MII), an information-theoretic market-regime measure combining memory, information flow, and network connectivity, predicts which broad class of technical signal performs best out of sample. The study is a prospective extension of *The Emergent Market Mind: Detecting Self-Organizing Intelligence in Financial Markets Through Multiscale Information Networks*. The prior paper reports the directional mapping High MII → trend-following, Medium MII → breakout/volatility-expansion, and Low MII → mean-reversion. The present study freezes that mapping before the prospective sample begins and tests it on future observations using the public MarketMind 0.1.0 implementation, fixed signal definitions, causal regime classification, one-session execution lag, and explicit transaction costs. No parameter will be selected on the 2026–2027 holdout sample.

### Hypotheses

**H1 — Primary, directional.** A regime-aware strategy that activates the trend family in High-MII states, the breakout/volatility-expansion family in Medium-MII states, and the mean-reversion family in Low-MII states will have a higher net annualized Sharpe ratio over the prospective holdout than an unconditional equal-weight ensemble of all nine preregistered technical signals.

**H2a — Confirmatory, directional.** The trend-family return will be higher in High-MII observations than in the pooled Medium- and Low-MII observations.

**H2b — Confirmatory, directional.** The breakout/volatility-expansion-family return will be higher in Medium-MII observations than in the pooled High- and Low-MII observations.

**H2c — Confirmatory, directional.** The mean-reversion-family return will be higher in Low-MII observations than in the pooled High- and Medium-MII observations.

**H3 — Confirmatory, directional.** The regime-aware strategy will have a higher net annualized Sharpe ratio than buy-and-hold over the prospective holdout.

H1 is the single primary hypothesis. H2a–H2c are mechanism tests of the preregistered regime-to-signal mapping. H3 is a secondary benchmark comparison.

---

## Design Plan

### Study type

Observational, prospective financial time-series validation study. There are no human participants and no randomized treatment assignment.

### Blinding

No participant blinding is applicable. The researcher cannot be blinded to publicly observable market history. To reduce researcher degrees of freedom, the analysis code, MII construction, signal definitions, execution lag, cost assumptions, evaluation dates, hypotheses, and inferential procedures are fixed in advance. Confirmatory outcome statistics for the prospective window will not be computed until the final scheduled observation has been collected.

### Study design

The study uses a prospective holdout beginning on the first trading session after the preregistration weekend, 10 August 2026, and ending 6 August 2027. Historical observations beginning 1 January 2003 may be used only to initialize trailing estimators, causal normalizers, regime thresholds, and technical indicators. All prospective performance evaluation is restricted to the holdout interval.

The primary market panel is:

- SPX public proxy: Yahoo Finance `^GSPC`
- NDX public proxy: Yahoo Finance `^NDX`
- SX5E public proxy: Yahoo Finance `^STOXX50E`
- ES continuous public proxy: Yahoo Finance `ES=F`

The connectivity panel additionally contains:

- `^VIX`
- `XLK`
- `XLF`
- `XLV`
- `XLE`

The public-data design is intentionally distinct from a bit-for-bit replication of licensed Bloomberg/Refinitiv histories used in the original paper.

### Randomization

Not applicable. Exposure-matched shuffled baselines and bootstrap resamples use pseudorandom draws with a fixed seed of `20260807` wherever a seed is required.

---

## Sampling Plan

### Existing data

This is a mixed historical-plus-prospective design. Historical market data before 10 August 2026 already exist and may have been observed in prior research. They are used only to initialize rolling estimators and thresholds. The confirmatory outcome sample does not exist at the time this plan is written: it consists of market observations from 10 August 2026 through 6 August 2027.

No performance result from the prospective window will be used to alter hypotheses, parameters, regime definitions, signal definitions, costs, exclusions, or inference criteria. Any such change will be documented as a dated deviation and treated as exploratory unless a new preregistration is filed before the affected data are analyzed.

### Data collection procedures

Data will be collected through the MarketMind public `yfinance` adapter using the tickers listed above. Raw downloads, the exact request configuration, row counts, missingness report, retrieval timestamp, and SHA-256 content fingerprint will be retained. Vendor revisions can alter later downloads; therefore, the raw file and provenance manifest used for the final analysis will be archived with the study materials.

The acquisition configuration is stored in `config/preregistered-validation-2026.yml`.

### Sample size

The confirmatory sample is all eligible daily observations for the four primary markets from 10 August 2026 through 6 August 2027 inclusive. The study does not stop after a target p-value or performance threshold. The expected size is approximately one trading year per market; the exact count is determined by each market's trading calendar and valid observations.

### Sample-size rationale

The one-year horizon was selected ex ante to provide a meaningful prospective market sample while keeping the design operationally feasible and resistant to short-event cherry-picking. Inference will account for serial dependence through moving-block resampling rather than treating market-days as independent observations.

### Stopping rule

Data collection ends after the 6 August 2027 session. There is no optional stopping based on interim Sharpe ratios, returns, p-values, drawdowns, or visual inspection. If one or more specified series are permanently discontinued, the original endpoint remains unchanged and the missing-data rule below applies.

---

## Variables

### Manipulated variables

None.

### Measured variables

#### Market Intelligence Index

The MII is computed with the frozen MarketMind 0.1.0 implementation using a 252-session estimation window and a 21-session step.

Memory component:

- DFA Hurst exponent
- Higuchi fractal dimension with `k = 1,...,20`
- absolute-return autocorrelation decay

Information-flow component:

- Shannon entropy with 20 equal-width bins, transformed so greater structural order points upward
- Kraskov mutual information with `k = 3`
- transfer entropy implemented as conditional mutual information with `k = 3`

Connectivity component:

- mean absolute pairwise correlation
- Onnela-style weighted clustering
- minimum-spanning-tree coherence based on correlation distance

Component weights are fixed:

- Memory: 0.35
- Information flow: 0.40
- Connectivity: 0.25

Normalization uses the package's `development` policy with development end `2014-12-31`, preserving the paper-aligned frozen development scaling. MII regimes are defined by lower and upper terciles estimated from up to the preceding 756 sessions and refreshed at the first trading observation of each month. The current MII observation is not included in the threshold sample used to classify itself.

#### Technical signals

All signals are unlevered and long-only with parameters fixed in MarketMind 0.1.0.

Trend family:

1. 50/200 simple-moving-average signal
2. 100-day moving-average slope signal
3. close-above-EMA(100) signal

Mean-reversion family:

1. RSI(14) entry/exit signal
2. lower-Bollinger reversal signal
3. three-down-close reversal signal

Breakout/volatility-expansion family:

1. 20-day-high signal
2. 20-day Donchian signal
3. ATR(14) expansion signal

Signals computed from date-t close information become positions no earlier than session t+1. MII regime labels are shifted by the same execution lag.

### Indices and constructed variables

For each market and session, each signal takes the package-defined long-only position. Family exposure is the arithmetic mean of the three constituent signal positions and therefore lies between 0 and 1.

The **regime-aware exposure** is:

- High MII: trend-family exposure
- Medium MII: breakout/volatility-expansion-family exposure
- Low MII: mean-reversion-family exposure

The **unconditional ensemble exposure** is the arithmetic mean of all nine signal positions, independent of MII state.

The **buy-and-hold exposure** is 1 whenever a valid market return is available.

Turnover is the absolute change in position. The primary cost assumption is 5 basis points per unit of turnover, charged on every position change. No leverage is permitted.

---

## Analysis Plan

### Statistical models and confirmatory tests

All returns used for strategy evaluation respect the one-session signal lag implemented by MarketMind.

#### Test of H1: primary strategy comparison

For each of the four markets, calculate the daily net return series of the regime-aware strategy and the unconditional nine-signal ensemble during the prospective window. Calculate each strategy's annualized Sharpe ratio using 252 trading sessions per year and a zero daily risk-free rate for the primary analysis. The market-level Sharpe difference is:

`Delta_SR_m = SR_regime-aware,m - SR_unconditional,m`.

The study-level statistic is the arithmetic mean of `Delta_SR_m` across the four primary markets.

Uncertainty is estimated by a synchronized moving-block bootstrap within each market, using a 20-observation block length, 10,000 bootstrap replications, and random seed `20260807`. Each replication recomputes the complete study-level Sharpe-difference statistic. H1 is supported if the two-sided 95% bootstrap confidence interval excludes zero and the estimated difference is positive.

#### Tests of H2a–H2c: preregistered regime mapping

For each market, construct the net return series of each signal-family exposure. The three preregistered contrasts are:

- Trend contrast: mean trend-family return in High MII minus mean trend-family return in pooled Medium/Low MII.
- Breakout contrast: mean breakout-family return in Medium MII minus mean breakout-family return in pooled High/Low MII.
- Mean-reversion contrast: mean mean-reversion-family return in Low MII minus mean mean-reversion-family return in pooled Medium/High MII.

Market-level contrasts are averaged across the four primary markets. Moving-block bootstrap confidence intervals use the same 20-observation block length, 10,000 replications, and seed. Multiplicity across H2a–H2c is controlled using Holm's procedure at family-wise alpha = 0.05. Each hypothesis is supported only if its corrected inference is significant and the effect has the preregistered positive sign.

#### Test of H3: buy-and-hold benchmark

Repeat the H1 Sharpe-difference procedure with buy-and-hold as the comparator. H3 is secondary and will be reported regardless of result.

### Transformations

Price series are converted to the return representation used by the frozen package. No winsorization, volatility targeting, leverage scaling, post-hoc smoothing, or parameter optimization is permitted in the confirmatory analysis. MII transformations, normalization, and regime classification follow MarketMind 0.1.0 exactly.

### Inference criteria

Primary alpha is 0.05. H1 is the sole primary hypothesis and is not multiplicity-adjusted. H2a–H2c use Holm family-wise correction at 0.05. H3 is explicitly secondary. Effect sizes, point estimates, 95% intervals, observation counts, exposure, turnover, and drawdowns will be reported even when null hypotheses are not rejected.

A failure to reject does not become evidence for the preregistered theory through exploratory analyses. Any unregistered model, threshold, signal, subset, alternative cost, or post-hoc explanation will be labeled exploratory.

### Data exclusion

No observation will be excluded solely because it produces an extreme return, adverse strategy performance, or an unexpected regime classification.

A price observation may be corrected only when it is demonstrably a data-vendor error. Any absolute one-session price move greater than 25% triggers verification against at least one independent source. Replacement is permitted only when the primary source is clearly erroneous; the original value, replacement value, reason, date, and verification source must be recorded in a machine-readable correction log.

Observations occurring before enough history exists to compute a required trailing estimator are initialization observations and are not part of the confirmatory evaluation. Because the evaluation begins after more than twenty years of initialization history, this should not remove holdout observations except after unusual data interruptions.

### Missing data

The package's configured forward-fill limit is five observations for data preparation where appropriate. No future value may be used to fill a missing past observation.

Performance is first computed separately for each market on its valid trading calendar. Market-level summary statistics are then combined, which avoids mechanically imputing returns across different market holidays. If a primary series is unavailable for more than five consecutive scheduled observations, the affected interval is marked missing for that market rather than filled indefinitely. The other markets remain in the study. If an entire primary series becomes permanently unavailable, results will be reported both for the remaining prespecified markets and as a documented deviation from the four-market design.

### Robustness analyses

The following analyses are prespecified as robustness checks and do not replace the primary H1 specification:

1. Transaction-cost sweep at 0, 5, 10, and 25 basis points per unit turnover.
2. Moving-block confidence intervals using block lengths 5, 10, and 20 sessions; 20 is primary.
3. Kraskov information-estimator sensitivity at `k = 4` and `k = 5`; `k = 3` is primary.
4. Naive baselines supplied by MarketMind: cash, lag-sign, and exposure-matched shuffled signals.
5. White-style reality-check and deflated-Sharpe diagnostics using the set of preregistered signals.
6. Gross-return results alongside the prespecified 5-bps net-return results.

Robustness results will be labeled as such and cannot retroactively change the primary decision rule.

### Exploratory analyses

After the confirmatory analysis is completed and frozen, exploratory work may examine individual signals, subperiods, alternative MII weights, alternative normalization policies, different network universes, nonlinear classifiers, volatility scaling, additional markets, and interactions among MII components. These analyses will be clearly separated from confirmatory results. Any promising exploratory claim intended as confirmatory evidence will require a new future holdout and a new preregistration.

---

## Other Information

### Relationship to prior work

This study is a prospective validation of a mapping previously reported from historical 2003–2024 analyses: High-MII environments favored trend-following signals, Medium-MII environments favored breakout/volatility-expansion signals, and Low-MII environments favored mean-reversion signals. Because that mapping was observed in prior data, the present study does not treat the old sample as confirmatory evidence. The confirmatory evidence is restricted to the future holdout defined above.

### Reproducibility and archiving

The final research archive will include:

- this preregistration and its OSF registration identifier;
- the frozen MarketMind release and Git commit;
- the acquisition configuration;
- raw-data snapshots where redistribution is permitted;
- SHA-256 provenance manifests;
- the analysis script/notebook used to generate results;
- `pip freeze` or equivalent environment lock;
- machine-readable tables of every confirmatory and robustness result;
- a deviation log;
- a public dataset/code release archived with a persistent DOI where licensing permits.

### Deviations

Any deviation from this plan will be timestamped and disclosed before the deviating result is interpreted. Deviations will not be silently substituted for preregistered decisions. The final paper will contain a table matching every preregistered hypothesis to its corresponding result and identifying all exploratory analyses.

### Null-results commitment

The study will be reported regardless of whether H1, H2a–H2c, or H3 is supported. A null or adverse prospective result is an informative test of the MarketMind framework and will not be suppressed.
