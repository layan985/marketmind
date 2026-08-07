# OSF Preregistration — Field-by-Field Copy Sheet

Use the **OSF Preregistration** template. This file is a convenience rendering of the canonical plan in `OSF_MARKETMIND_PROSPECTIVE_2026.md`. If wording differs, the canonical plan controls.

## Title
Prospective Out-of-Sample Validation of the Market Intelligence Index for Regime-Conditioned Technical Analysis

## Description
This prospective study evaluates whether the Market Intelligence Index (MII), an information-theoretic regime measure combining market memory, information flow, and network connectivity, predicts which broad class of technical signal performs best out of sample. The preregistered mapping is High MII → trend-following, Medium MII → breakout/volatility expansion, and Low MII → mean reversion. The confirmatory sample is restricted to future observations from 10 August 2026 through 6 August 2027. The analysis uses frozen MarketMind 0.1.0 software, fixed signal definitions, causal regime classification, one-session execution lag, explicit transaction costs, prespecified bootstrap inference, and a public deviation log. Results will be reported regardless of whether the hypotheses are supported.

## Hypotheses
H1 — Primary, directional. A regime-aware strategy that activates the trend family in High-MII states, the breakout/volatility-expansion family in Medium-MII states, and the mean-reversion family in Low-MII states will have a higher net annualized Sharpe ratio over the prospective holdout than an unconditional equal-weight ensemble of all nine preregistered technical signals.

H2a — Confirmatory, directional. The trend-family return will be higher in High-MII observations than in the pooled Medium- and Low-MII observations.

H2b — Confirmatory, directional. The breakout/volatility-expansion-family return will be higher in Medium-MII observations than in the pooled High- and Low-MII observations.

H2c — Confirmatory, directional. The mean-reversion-family return will be higher in Low-MII observations than in the pooled High- and Medium-MII observations.

H3 — Confirmatory, directional. The regime-aware strategy will have a higher net annualized Sharpe ratio than buy-and-hold over the prospective holdout.

H1 is the single primary hypothesis. H2a–H2c are mechanism tests of the preregistered regime-to-signal mapping. H3 is a secondary benchmark comparison.

## Study type / design
Observational, prospective financial time-series validation study. There are no human participants and no randomized treatment assignment. The prospective holdout begins 10 August 2026 and ends 6 August 2027. Historical observations beginning 1 January 2003 may be used only to initialize trailing estimators, causal normalizers, regime thresholds, and technical indicators. All prospective performance evaluation is restricted to the holdout interval.

## Blinding
No participant blinding is applicable. The researcher cannot be blinded to publicly observable market history. To reduce researcher degrees of freedom, analysis code, MII construction, signal definitions, execution lag, cost assumptions, evaluation dates, hypotheses, and inferential procedures are fixed in advance. Confirmatory outcome statistics for the prospective window will not be computed until the final scheduled observation has been collected.

## Existing data
This is a mixed historical-plus-prospective design. Historical data before 10 August 2026 already exist and may have been observed in prior research. They are used only to initialize rolling estimators and thresholds. The confirmatory outcome sample consists of future market observations from 10 August 2026 through 6 August 2027.

## Data collection procedures
Data will be collected through the MarketMind public yfinance adapter. Primary series are `^GSPC`, `^NDX`, `^STOXX50E`, and `ES=F`. Connectivity additionally uses `^VIX`, `XLK`, `XLF`, `XLV`, and `XLE`. Raw downloads, request configuration, row counts, missingness, retrieval timestamp, and SHA-256 content fingerprint will be retained. The acquisition configuration is `config/preregistered-validation-2026.yml`.

## Sample size
All eligible daily observations for SPX, NDX, SX5E, and ES from 10 August 2026 through 6 August 2027 inclusive. Expected size is approximately one trading year per market; the exact count is determined by valid trading calendars and observations.

## Sample-size rationale
A one-year horizon was chosen ex ante to provide a meaningful prospective market sample while avoiding short-event cherry-picking. Serial dependence is handled with moving-block bootstrap inference rather than treating daily observations as independent.

## Stopping rule
Data collection ends after the 6 August 2027 session. There is no optional stopping based on interim Sharpe ratios, returns, p-values, drawdowns, or visual inspection.

## Measured variables
MII uses MarketMind 0.1.0 with a 252-session window and 21-session step. Memory uses DFA Hurst exponent, Higuchi fractal dimension (`k=1,...,20`), and absolute-return autocorrelation decay. Information flow uses Shannon entropy with 20 equal-width bins, Kraskov mutual information (`k=3`), and transfer entropy as conditional mutual information (`k=3`). Connectivity uses mean absolute correlation, Onnela-style weighted clustering, and minimum-spanning-tree coherence. Component weights are fixed at 0.35 memory, 0.40 information flow, and 0.25 connectivity. Normalization uses the development policy with development end 2014-12-31. Regimes use lower and upper terciles estimated from up to the preceding 756 sessions and refreshed monthly without including the current MII observation in its own threshold sample.

## Technical signals
Trend: 50/200 SMA; 100-day moving-average slope; close above EMA(100).

Mean reversion: RSI(14) entry/exit; lower-Bollinger reversal; three-down-close reversal.

Breakout/volatility expansion: 20-day high; 20-day Donchian; ATR(14) expansion.

All are long-only and unlevered. Signals computed from date-t close information become positions no earlier than session t+1. Regime labels are shifted by the same execution lag.

## Constructed variables
Family exposure is the arithmetic mean of each family's three constituent signal positions. Regime-aware exposure selects trend in High MII, breakout/volatility expansion in Medium MII, and mean reversion in Low MII. The unconditional ensemble is the arithmetic mean of all nine signal positions. Buy-and-hold exposure is 1 whenever a valid market return is available. Primary transaction costs are 5 basis points per unit turnover.

## Primary analysis
For each market, compute daily net returns for the regime-aware strategy and unconditional nine-signal ensemble. Calculate annualized Sharpe with 252 sessions/year and zero daily risk-free rate. Define `Delta_SR_m = SR_regime-aware,m - SR_unconditional,m`. The study-level statistic is the arithmetic mean across the four markets. Use synchronized moving-block bootstrap inference with block length 20, 10,000 replications, seed 20260807. H1 is supported if the two-sided 95% bootstrap confidence interval excludes zero and the estimated difference is positive.

## Mechanism analyses
H2a: trend-family return in High MII minus pooled Medium/Low MII.

H2b: breakout-family return in Medium MII minus pooled High/Low MII.

H2c: mean-reversion-family return in Low MII minus pooled Medium/High MII.

Average market-level contrasts across the four primary markets. Use the same block bootstrap design. Apply Holm correction across H2a–H2c at family-wise alpha 0.05.

## Secondary benchmark analysis
Repeat the H1 Sharpe-difference procedure using buy-and-hold as comparator. H3 is secondary and will be reported regardless of result.

## Transformations
No winsorization, volatility targeting, leverage scaling, post-hoc smoothing, or parameter optimization is permitted in the confirmatory analysis. MII transformations, normalization, and regime classification follow MarketMind 0.1.0 exactly.

## Inference criteria
Primary alpha = 0.05. H1 is the sole primary hypothesis and is not multiplicity-adjusted. H2a–H2c use Holm family-wise correction at 0.05. H3 is secondary. Point estimates, effect sizes, 95% intervals, counts, exposure, turnover, and drawdowns will be reported regardless of significance.

## Exclusions
No observation will be excluded because it produces an extreme return, poor strategy performance, or unexpected regime classification. Any absolute one-session price move greater than 25% triggers verification against at least one independent source. Replacement is allowed only for a demonstrable vendor error and must be logged with original value, replacement, reason, date, and verification source.

## Missing data
No future value may fill a missing past observation. Performance is computed separately on each market's valid trading calendar. If a primary series is unavailable for more than five consecutive scheduled observations, the affected interval is marked missing for that market rather than filled indefinitely. Other markets remain in the study. Permanent loss of a primary series is disclosed as a deviation.

## Robustness analyses
1. Transaction-cost sweep: 0, 5, 10, 25 bps.
2. Moving-block confidence intervals: block lengths 5, 10, 20; 20 primary.
3. Kraskov sensitivity: k=4 and k=5; k=3 primary.
4. Naive baselines: cash, lag-sign, exposure-matched shuffle.
5. White-style reality-check and deflated-Sharpe diagnostics.
6. Gross-return results alongside primary 5-bps net-return results.

These are robustness checks and do not replace the primary decision rule.

## Exploratory analyses
After confirmatory analysis is frozen, exploratory work may examine individual signals, subperiods, alternative MII weights, alternative normalization, different network universes, nonlinear classifiers, volatility scaling, additional markets, and MII-component interactions. These analyses will be explicitly labeled exploratory. Any exploratory claim intended as confirmatory evidence requires a new future holdout and new preregistration.

## Other information / prior work
This study is a prospective validation of a mapping previously observed in historical 2003–2024 analyses: High MII favored trend-following, Medium MII favored breakout/volatility expansion, and Low MII favored mean reversion. Historical results are not treated as confirmatory evidence here; confirmation is restricted to the future holdout.

## Reproducibility
Final archive will include the OSF registration identifier, frozen MarketMind release and Git commit, acquisition configuration, raw snapshots where redistribution is allowed, SHA-256 manifests, analysis code, environment lock, machine-readable confirmatory and robustness results, and a public deviations log. A DOI-bearing data/code archive will be produced where licensing permits.

## Deviations
Any deviation from the preregistered plan will be timestamped and disclosed before interpretation. Deviations will not silently replace preregistered decisions. The final paper will match every hypothesis to its result and identify exploratory analyses.

## Null-results commitment
The study will be reported regardless of whether H1, H2a–H2c, or H3 is supported. Null or adverse prospective evidence will not be suppressed.

## Metadata
Contributor: Layan Oraidi

Suggested tags: `market-regimes`, `technical-analysis`, `information-theory`, `financial-markets`, `marketmind`, `preregistration`, `out-of-sample`, `reproducibility`, `open-science`, `computational-finance`

Related repository: https://github.com/layan985/marketmind

Frozen software: `marketmind==0.1.0`

Frozen source commit: `ad1b13da2f7ea02ee24ae6097d8451a634e4ee97`

Prospective evaluation: 2026-08-10 through 2027-08-06

Visibility at submission: make public immediately.
