# OSF Preregistration — Exact Page-by-Page Copy Sheet

Use the **OSF Preregistration** template. This is a field-by-field rendering of the canonical frozen plan in `OSF_MARKETMIND_PROSPECTIVE_2026.md`. Do not improvise scientific details in the OSF form; if an OSF label differs slightly, paste the answer under the closest matching field.

---

# START / TEMPLATE

## Do you have content for registration in an existing OSF project?
**Select: No**

Reason: create the registration from scratch so no unrelated project files are accidentally frozen into the registration.

## Registration template
**Select: OSF Preregistration**

---

# METADATA

## Title
**Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis**

## Description
This prospective study evaluates whether the Market Intelligence Index (MII), an information-theoretic regime measure combining market memory, information flow, and network connectivity, predicts which broad class of technical signal performs best out of sample. The preregistered mapping is High MII → trend-following, Medium MII → breakout/volatility expansion, and Low MII → mean reversion. The confirmatory sample is restricted to future observations from 10 August 2026 through 6 August 2027. The analysis uses frozen MarketMind 0.1.0 software, fixed signal definitions, causal regime classification, one-session execution lag, explicit transaction costs, prespecified bootstrap inference, and a public deviation log. Results will be reported regardless of whether the hypotheses are supported.

## Contributors
**Layan Oraidi**

Make Layan Oraidi a bibliographic contributor and administrator. Add no other contributor unless that person has genuinely contributed to the study and has agreed to authorship/contributorship.

## License
**Preferred: Creative Commons Attribution 4.0 International (CC BY 4.0), if available.**

This license applies to the preregistration text/materials, not to third-party market data whose redistribution may be restricted.

## Institutional affiliation
If the OSF account presents the relevant university affiliation and it is accurate at submission, select it. Otherwise leave this metadata field blank rather than inventing an institutional affiliation.

## Subjects
Select the closest available official OSF subjects to:
- Economics
- Finance
- Econometrics / Quantitative Methods
- Data Science / Computational Research

Do not worry if the exact labels differ; use the closest official OSF taxonomy entries.

## Tags
Add:
`market-regimes`
`technical-analysis`
`information-theory`
`financial-markets`
`marketmind`
`preregistration`
`out-of-sample`
`reproducibility`
`open-science`
`computational-finance`

---

# PAGE 1 — STUDY INFORMATION

## 1. Title
**Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis**

## 2. Authors
**Layan Oraidi**

## 3. Description
This study prospectively evaluates whether the Market Intelligence Index (MII), which combines market memory, information flow, and network connectivity, identifies market environments in which different technical-signal families have differential out-of-sample performance. Prior historical work reported the mapping High MII → trend-following, Medium MII → breakout/volatility expansion, and Low MII → mean reversion. The present study freezes that mapping before a new prospective sample begins and tests it using future daily market observations from 10 August 2026 through 6 August 2027. The analysis uses MarketMind 0.1.0, fixed signals, causal regime classification, one-session execution lag, explicit transaction costs, prespecified inference, and a public deviation log. No model or signal parameter will be selected using the prospective holdout.

## 4. Hypotheses
**H1 — Primary, directional.** A regime-aware strategy that activates the trend family in High-MII states, the breakout/volatility-expansion family in Medium-MII states, and the mean-reversion family in Low-MII states will have a higher net annualized Sharpe ratio over the prospective holdout than an unconditional equal-weight ensemble of all nine preregistered technical signals.

**H2a — Confirmatory, directional.** The trend-family return will be higher in High-MII observations than in the pooled Medium- and Low-MII observations.

**H2b — Confirmatory, directional.** The breakout/volatility-expansion-family return will be higher in Medium-MII observations than in the pooled High- and Low-MII observations.

**H2c — Confirmatory, directional.** The mean-reversion-family return will be higher in Low-MII observations than in the pooled High- and Medium-MII observations.

**H3 — Secondary confirmatory, directional.** The regime-aware strategy will have a higher net annualized Sharpe ratio than buy-and-hold over the prospective holdout.

H1 is the sole primary hypothesis. H2a–H2c test the preregistered regime-to-signal mechanism. H3 is a secondary benchmark comparison.

---

# PAGE 2 — DESIGN PLAN

## 5. Study type
**Select: Observational Study**

No treatment is assigned. The study prospectively observes financial-market time series and evaluates a pre-specified algorithmic classification and strategy mapping.

## 6. Blinding
**Select: No blinding is involved in this study.**

## 7. Additional blinding details
No participant or treatment blinding is applicable because this is an observational financial time-series study. The researcher cannot be blinded to publicly observable historical market information. To reduce researcher degrees of freedom, the hypotheses, sample dates, MarketMind software version, frozen source commit, MII construction, signal definitions, execution lag, cost assumptions, exclusions, inferential procedures, and decision criteria are fixed before the prospective holdout begins. Confirmatory performance statistics for the 10 August 2026–6 August 2027 window will not be used to modify the preregistered design.

## 8. Study design
This is a prospective observational time-series validation study with four primary markets: SPX, NDX, SX5E, and ES. The prospective confirmatory window is 10 August 2026 through 6 August 2027 inclusive. Historical observations beginning 1 January 2003 may be used only to initialize trailing estimators, technical indicators, normalization, and causal regime thresholds. Performance evaluation used as confirmatory evidence is restricted to the prospective window.

At each eligible date, MarketMind computes an MII state using only information available at or before that date. Signal information observed at date-t close becomes an implementable position no earlier than session t+1. Regime labels are subjected to the same execution lag. Strategies are unlevered and long-only.

The central comparison is between (i) a preregistered regime-aware strategy selecting the trend family in High MII, breakout/volatility expansion in Medium MII, and mean reversion in Low MII; and (ii) an unconditional equal-weight ensemble of all nine fixed technical signals. Buy-and-hold is a secondary comparator.

## 9. Randomization
No experimental randomization or treatment assignment is used. Where stochastic resampling is required for inference or robustness checks, pseudorandom draws will use the prespecified seed `20260807`. This computational resampling is not a randomized study design.

---

# PAGE 3 — SAMPLING PLAN

## 10. Existing data
**Select: Registration following analysis of the data.**

This is the most transparent option because historical data relevant to the framework have already been accessed and analyzed in prior work. The prospective confirmatory outcomes themselves have not yet been realized at preregistration.

## 11. Explanation of existing data
Historical market data from 2003–2024 were previously analyzed in development of the Market Intelligence Index and the prior study from which the directional regime-to-signal mapping was derived. Those historical findings motivated the present hypotheses and therefore are not treated as new confirmatory evidence.

The present confirmatory sample is prospectively separated from that prior work: only observations from 10 August 2026 through 6 August 2027 will be used to evaluate the preregistered confirmatory hypotheses. Historical observations before 10 August 2026 may be used mechanically to initialize trailing windows, technical indicators, normalization bounds, and causal regime thresholds. No historical result will be counted as confirmation of H1–H3 in the prospective study.

No performance result from the prospective holdout will be used to alter hypotheses, signal definitions, MII weights, cost assumptions, sample endpoint, exclusion rules, or inferential criteria. Any deviation will be timestamped in the public deviation log and clearly distinguished from confirmatory results.

## 12. Data collection procedures
Market data will be obtained through the MarketMind public `yfinance` data adapter using the frozen acquisition configuration `config/preregistered-validation-2026.yml`.

Primary market series:
- SPX public proxy: Yahoo Finance `^GSPC`
- NDX public proxy: Yahoo Finance `^NDX`
- SX5E public proxy: Yahoo Finance `^STOXX50E`
- ES continuous public proxy: Yahoo Finance `ES=F`

Connectivity panel additionally includes:
- `^VIX`
- `XLK`
- `XLF`
- `XLV`
- `XLE`

The requested historical range begins 1 January 2003 to provide initialization history. Confirmatory evaluation begins 10 August 2026 and ends 6 August 2027 inclusive. The configured price field is Close and the data-preparation forward-fill limit is five observations where applicable; no future value may be used to fill a past missing value.

For the final analysis, the exact raw-data snapshot used will be retained where redistribution is permitted. A provenance manifest will record the retrieval configuration, retrieval timestamp, row counts, missingness, and SHA-256 content fingerprint. Vendor revisions may cause later downloads to differ, so the final archive will preserve the analysis snapshot or, where licensing prevents redistribution, the request configuration and integrity/provenance information.

## 13. Sample size
The confirmatory sample consists of all eligible daily observations for SPX, NDX, SX5E, and ES from 10 August 2026 through 6 August 2027 inclusive. The exact number of observations is determined by each market's valid trading calendar and data availability. This is approximately one trading year per market. The study will report exact observation counts by market and regime.

## 14. Sample-size rationale
The sample is date-bounded rather than p-value-bounded. A one-year prospective horizon was selected in advance because it provides a meaningful out-of-sample market interval while preventing the study from selecting an endpoint after observing unusually favorable or unfavorable performance. The study is not powered under an IID-observation assumption because daily financial returns are serially dependent and regime occupancy is unknown in advance. Inferential uncertainty will therefore be assessed using prespecified moving-block bootstrap procedures that preserve short-run dependence.

## 15. Stopping rule
Data collection ends after the 6 August 2027 trading session. There is no optional stopping based on interim Sharpe ratio, cumulative return, drawdown, p-value, bootstrap interval, regime distribution, or visual inspection. If one or more series become temporarily unavailable, the fixed calendar endpoint remains unchanged and the preregistered missing-data rules apply. If a primary series becomes permanently unavailable, this will be disclosed as a deviation rather than changing the endpoint to obtain a preferred result.

---

# PAGE 4 — VARIABLES

## 16. Manipulated variables
**None.** This is an observational study. No market variable, treatment, exposure, or participant assignment is experimentally manipulated.

## 17. Measured variables
The confirmatory analysis uses the following measured or algorithmically derived variables.

**Market prices and returns.** Daily Close-price histories for the prespecified primary and connectivity series. Primary asset returns are computed from the corresponding price series using the frozen MarketMind implementation.

**MII memory submetrics.** DFA Hurst exponent; Higuchi fractal dimension calculated with `k = 1,...,20`; absolute-return autocorrelation decay.

**MII information-flow submetrics.** Shannon entropy with 20 equal-width bins; Kraskov mutual information with primary `k = 3`; transfer entropy implemented as conditional mutual information with primary `k = 3`.

**MII connectivity submetrics.** Mean absolute pairwise correlation; Onnela-style weighted clustering; minimum-spanning-tree coherence based on correlation distance.

**MII and regime.** Composite Market Intelligence Index and its causal Low-, Medium-, or High-MII state.

**Technical-signal positions.** Nine frozen long-only signals grouped into three families:
- Trend: 50/200 simple-moving-average signal; 100-day moving-average slope; close above EMA(100).
- Mean reversion: RSI(14) entry/exit; lower-Bollinger reversal; three-down-close reversal.
- Breakout/volatility expansion: 20-day-high; 20-day Donchian; ATR(14) expansion.

**Strategy outcomes.** Daily position, turnover, gross return, transaction-cost-adjusted net return, annualized Sharpe ratio, cumulative/annualized return, annualized volatility, maximum drawdown, exposure, and trade count. The primary outcome for H1 and H3 is the difference in net annualized Sharpe ratio between the relevant strategies. H2a–H2c use preregistered regime-conditional family-return contrasts.

## 18. Indices
The MII combines three component indices: Memory (M), Information Flow (I), and Connectivity (C).

`MII_t = 0.35*M_t + 0.40*I_t + 0.25*C_t`.

Each component is formed from its three frozen submetrics after transformations that orient larger values toward greater coherent information structure and after the normalization procedure implemented in MarketMind 0.1.0. The primary normalization policy is `development`, with bounds frozen using data through `2014-12-31`. Shannon entropy is oriented so structural order points upward. Higuchi dimension enters through the paper-aligned memory orientation implemented in the frozen package. The exact implementation is fixed by MarketMind 0.1.0 and source commit `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`.

At the first trading observation of each month, Low/Medium/High regime thresholds are the lower and upper terciles estimated from up to the preceding 756 sessions of MII history. The current MII observation is not included in the threshold sample used to classify itself; monthly thresholds remain fixed through the month.

For strategy construction, each signal family exposure is the arithmetic mean of the three constituent long-only signal positions. The regime-aware exposure equals the trend-family exposure in High MII, breakout/volatility-expansion-family exposure in Medium MII, and mean-reversion-family exposure in Low MII. The unconditional comparator equals the arithmetic mean of all nine signal positions independent of MII state. Buy-and-hold exposure equals 1 whenever a valid market return is available. Turnover is the absolute position change. The primary transaction-cost rate is 5 basis points per unit of turnover.

---

# PAGE 5 — ANALYSIS PLAN

## 19. Statistical models
### H1 — Primary regime-aware versus unconditional ensemble
For each of SPX, NDX, SX5E, and ES, compute the daily net-return series of the preregistered regime-aware strategy and the unconditional equal-weight nine-signal ensemble during 10 August 2026–6 August 2027. Annualized Sharpe ratio is computed using 252 trading sessions per year and a zero daily risk-free rate for the primary analysis.

For market `m`, define:
`Delta_SR_m = SR_regime-aware,m - SR_unconditional,m`.

The study-level H1 statistic is the arithmetic mean of `Delta_SR_m` across the four primary markets.

Uncertainty is estimated using a synchronized moving-block bootstrap within markets with primary block length 20 observations, 10,000 bootstrap replications, and random seed `20260807`. Each bootstrap replication recomputes the complete study-level Sharpe-difference statistic.

### H2a–H2c — Regime-to-signal mechanism tests
For each primary market, construct the net return of each signal-family exposure. Calculate:
- H2a trend contrast = mean trend-family return in High MII minus mean trend-family return in pooled Medium/Low MII.
- H2b breakout contrast = mean breakout-family return in Medium MII minus mean breakout-family return in pooled High/Low MII.
- H2c mean-reversion contrast = mean mean-reversion-family return in Low MII minus mean mean-reversion-family return in pooled Medium/High MII.

For each contrast, average the market-level contrast across the four primary markets. Use moving-block bootstrap inference with primary block length 20, 10,000 replications, seed `20260807`. Multiplicity across H2a–H2c is controlled with Holm's procedure at family-wise alpha 0.05.

### H3 — Regime-aware versus buy-and-hold
Repeat the H1 Sharpe-difference procedure with buy-and-hold as the comparator. H3 is secondary and will be reported regardless of its result.

### Prespecified robustness analyses
Robustness analyses do not replace the primary decision rule:
1. Transaction costs 0, 5, 10, and 25 bps per unit turnover; 5 bps is primary.
2. Moving-block bootstrap block lengths 5, 10, and 20; 20 is primary.
3. Kraskov estimator `k = 4` and `k = 5`; `k = 3` is primary.
4. Naive baselines: cash, lag-sign, and exposure-matched shuffled signals.
5. White-style reality-check and deflated-Sharpe diagnostics using the preregistered signal family.
6. Gross-return results alongside the primary 5-bps net-return results.

## 20. Transformations
Close prices are converted to the return representation implemented in MarketMind 0.1.0. All indicator, MII, and regime transformations follow the frozen package. Signal information based on date-t close is shifted so that it becomes a position no earlier than session t+1; regime labels are shifted by the same execution lag. Turnover equals the absolute position change and primary transaction costs equal 5/10,000 times turnover.

MII raw submetrics are directionally transformed where required so that larger values correspond to more coherent information structure, then normalized under the frozen `development` normalization policy with development end `2014-12-31`, combined within components, and weighted 0.35 memory, 0.40 information flow, and 0.25 connectivity.

No confirmatory winsorization, volatility targeting, leverage scaling, post-hoc smoothing, post-hoc sample splitting, or parameter optimization is permitted.

## 21. Inference criteria
The primary significance level is alpha = 0.05. H1 is the sole primary hypothesis and is not multiplicity-adjusted. H1 is supported only if the estimated study-level Sharpe difference is positive and the two-sided 95% moving-block-bootstrap confidence interval excludes zero.

H2a–H2c are a confirmatory family and use Holm correction at family-wise alpha = 0.05. Each mechanism hypothesis is supported only if its multiplicity-adjusted inference is significant and the estimated contrast has the preregistered positive direction.

H3 is explicitly secondary. It will be reported with its point estimate and 95% interval and will not be substituted for H1 if H1 fails.

Regardless of statistical significance, the final report will provide point estimates, relevant effect sizes/contrasts, 95% intervals, observation counts, regime counts, exposure, turnover, returns, volatility, Sharpe ratios, and maximum drawdowns. Null or adverse results remain reportable outcomes.

## 22. Data exclusion
No observation will be excluded solely because it produces an extreme return, adverse strategy performance, an unexpected MII state, or weak support for the hypotheses.

An absolute one-session price move greater than 25% triggers verification against at least one independent source for a potential vendor/data error. A value may be replaced only if the primary source is demonstrably erroneous. Any correction must be recorded in a machine-readable correction/deviation record including date, series, original value, replacement value, reason, independent verification source, and repository reference.

Observations before sufficient trailing history exists for a required estimator are initialization observations rather than confirmatory observations. Because more than twenty years of initialization data precede the holdout, this should not ordinarily remove prospective observations except following unusual data interruptions.

## 23. Missing data
No future observation may be used to fill a missing past observation. The frozen acquisition configuration allows a forward-fill limit of up to five observations where the data pipeline deems it appropriate. Performance is calculated separately for each primary market on its valid trading calendar, avoiding mechanical return imputation across different market holidays.

If a primary series is unavailable for more than five consecutive scheduled observations, the affected interval is treated as missing for that market rather than filled indefinitely; the other primary markets remain in the study. If an entire prespecified primary series becomes permanently unavailable, the study endpoint remains unchanged, the issue is logged as a deviation, and results will transparently report the available-market analysis rather than silently replacing the series.

## 24. Exploratory analysis
Only after the confirmatory analysis is run and frozen may exploratory analyses examine individual signals, individual MII subcomponents, subperiods, alternative MII weights, alternative normalization policies, different network universes, nonlinear classifiers, volatility scaling, additional markets, alternative transaction-cost structures beyond the prespecified robustness sweep, or interactions among MII components.

All such analyses will be labeled exploratory and will not be described as preregistered evidence for H1–H3. Any exploratory pattern intended for later confirmatory interpretation will require a new prospective holdout and a new preregistration.

---

# PAGE 6 — OTHER

## 25. Other
This study is a prospective validation of claims motivated by prior historical work on the Market Intelligence Index. The historical 2003–2024 analyses previously reported that High-MII environments favored trend-following signals, Medium-MII environments favored breakout/volatility-expansion signals, and Low-MII environments favored mean-reversion signals. Those historical findings generated the present hypotheses and are not treated as new confirmatory evidence.

The confirmatory window is prospectively fixed at 10 August 2026 through 6 August 2027. The research software is frozen at `marketmind==0.1.0`; the source implementation underlying the preregistered methods is commit `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`. The preregistration materials and acquisition configuration are publicly versioned in `https://github.com/layan985/marketmind` and a dedicated preregistration freeze branch preserves the pre-holdout state.

The final research archive will include the OSF registration identifier, frozen software/version information, acquisition configuration, raw-data snapshots where redistribution is legally permitted, provenance manifests with SHA-256 fingerprints, confirmatory analysis code, environment information, machine-readable confirmatory and robustness results, and a public deviation log. A DOI-bearing archival release of software/data/results will be created where licensing permits.

Any deviation from this plan will be timestamped and disclosed. The study will be reported regardless of whether H1, H2a–H2c, or H3 is supported. Null or adverse prospective results will not be suppressed.

### Related public materials
GitHub repository: `https://github.com/layan985/marketmind`

Frozen software: `marketmind==0.1.0`

Frozen source implementation: `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`

Preregistration plan: `preregistration/OSF_MARKETMIND_PROSPECTIVE_2026.md`

Acquisition configuration: `config/preregistered-validation-2026.yml`

Deviation log: `preregistration/DEVIATIONS.csv`

Tracking issue: GitHub issue #1

---

# IF OSF SHOWS AN OPTIONAL ANALYSIS SCRIPTS / FILES FIELD

Paste:

The methods and reusable research software are publicly versioned at `https://github.com/layan985/marketmind`. The confirmatory study is tied to MarketMind 0.1.0 and source commit `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`. The repository contains the frozen preregistration text, acquisition configuration, reproducibility documentation, signal and MII implementations, backtesting utilities, and deviation log. The final confirmatory runner and result artifacts will be archived without changing the preregistered scientific decisions. Any implementation correction required to execute the preregistered plan will be documented in the deviation log and will not be used to change the substantive hypothesis or decision rule.

If OSF permits file attachments, attach the preregistration plan and acquisition config only if desired. Do not attach licensed/raw vendor data.

---

# REVIEW / SUBMISSION

Before registering, verify:
- Title exactly matches this sheet.
- Study type = Observational Study.
- Existing data = Registration following analysis of the data.
- Confirmatory window = 2026-08-10 through 2027-08-06.
- Primary markets = SPX, NDX, SX5E, ES.
- MarketMind = 0.1.0.
- Frozen implementation commit = `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`.
- Primary comparator = unconditional equal-weight nine-signal ensemble.
- Primary cost = 5 bps per unit turnover.
- Primary block length = 20.
- Bootstrap replications = 10,000.
- Seed = 20260807.
- H2a–H2c = Holm correction at family-wise alpha 0.05.
- Null/adverse results commitment is present.

On the final privacy/registration step, choose **public immediately** if the goal is an immediate public registration/DOI. Review every page once, then register. Do not fabricate an OSF DOI before OSF assigns one.
