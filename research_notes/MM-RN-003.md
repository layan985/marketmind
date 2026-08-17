# MM-RN-003 — How Much Alpha Can Look-Ahead Bias Manufacture?

**MarketMind Research Note · 18 August 2026**  
**Status:** COMPLETE · REPRODUCIBLE  
**Evidence class:** controlled synthetic experiment

## Abstract

How large can apparent risk-adjusted performance become under common timing mistakes when the underlying data contain no genuine predictive structure? We run 100 simulations of 4,000 IID Gaussian returns and compare a strictly causal trailing construction with deliberately contaminated alternatives. The clean control produces mean annualized Sharpe **0.019**. A centered rolling feature produces **2.796**, while same-session execution produces **21.017**. The distributional result is stronger than the means: every centered-window replication exceeds Sharpe 2, while no causal-control replication exceeds Sharpe 1. These experiments do not estimate bias in any named real strategy. They show how an invalid information set can manufacture apparently decisive evidence from pure noise.

## 1. Question

A backtest is a historical simulation of a decision rule, but its validity depends on a stricter object: the **information set available at the decision time**. A feature can be mathematically well-defined and still be unusable if its value at t depends on observations from t or later. This note asks a narrow falsification-style question: if returns are truly unpredictable, how much apparent Sharpe can be manufactured by common timing errors?

The null is unusually strong because the data-generating process contains no latent alpha to discover. Therefore any persistent positive performance is created by sampling variation, selection, or contamination introduced by the research design itself.

## 2. Experimental design

For replication j=1,…,100, draw r_t ~ IID N(0,0.01), t=1,…,4000. Seeds are 1000 through 1099. Strategy returns equal s_t r_t, where s_t is the arm-specific position. We report annualized Sharpe as √252 × mean(s_t r_t)/sd(s_t r_t). No transaction-cost model is required because the object under study is contamination magnitude rather than economic viability.

### 2.1 Causal trailing control

The signal is the sign of a 20-session rolling mean shifted by one session. The observation at t therefore uses only returns through t−1. This is the reference information set.

### 2.2 Centered rolling statistic

The signal uses a 21-session centered rolling mean. A value attached to date t includes future observations. This is a subtle implementation failure because the feature can look like an ordinary smoothing operation in code while violating the decision-time information set.

### 2.3 Same-session execution

The signal is sign(r_t), and the strategy is credited with r_t. The trade therefore sees the exact return it is supposed to earn. This arm is deliberately pathological: it establishes how extreme a timing violation can become.

### 2.4 Secondary selection arms

A retrospective-threshold arm selects the best of 17 cutoffs after observing realized noise. A multiple-search arm generates 50 unrelated noise signals and retains the best backtest. These are not look-ahead in the same mechanical sense, but they expose adjacent researcher degrees of freedom.

## 3. Results

| Arm | Mean | Median | 5th pct | 95th pct | Max | Fraction >1 | Fraction >2 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Causal trailing control | **0.019** | 0.007 | -0.328 | 0.417 | 0.555 | 0% | 0% |
| Centered rolling window | **2.796** | 2.791 | 2.359 | 3.118 | 3.356 | 100% | 100% |
| Same-session execution | **21.017** | 21.033 | 20.752 | 21.232 | 21.463 | 100% | 100% |
| Retrospective threshold | 0.191 | 0.141 | -0.102 | 0.676 | 1.102 | 1% | 0% |
| Best of 50 noise signals | 0.555 | 0.527 | 0.410 | 0.757 | 0.958 | 0% | 0% |

The causal control behaves as the null requires. Its mean is close to zero, its central distribution spans both signs, and even its maximum across 100 simulations is only 0.555. Centering the rolling feature changes the entire distribution: the *5th percentile* is 2.359. The result is therefore not driven by a few lucky simulations. Same-session execution is more destructive still, with a narrow distribution centered around Sharpe 21.

## 4. What the distributions add

Reporting only the mean can hide whether contamination creates a systematic distortion or occasional spectacular accidents. Here the centered-window error is systematic: P(Sharpe>2)=1 across the 100 disclosed replications. The causal control has P(Sharpe>1)=0. The non-overlap is a direct consequence of importing information unavailable at trade time.

Selection effects are smaller in this design but still directionally important. Searching 50 meaningless signals raises the average winning Sharpe to 0.555 even though every candidate is generated independently of future returns. Retrospective threshold choice raises the mean to 0.191 and creates one run above Sharpe 1. These results illustrate why an apparently modest degree of search can alter the reference distribution before any economic mechanism is present.

## 5. Why centered windows are dangerous

Centered windows are especially useful as a teaching failure because they often enter research through generic preprocessing. Smoothing, denoising, decomposition and label construction can all be technically correct as descriptive operations while being invalid as predictive inputs. A useful audit question is therefore not “was this feature shifted?” but “for every timestamp, what is the latest raw observation capable of changing this value?”

The same logic applies to normalization. Full-sample means, variances, quantiles and dimensionality reductions can transmit future distributional information backward even when the final signal is shifted. MarketMind’s validation philosophy treats the information boundary as an object to test directly rather than a convention to assume.

## 6. What this note does not show

This experiment does **not** imply that a specific reported strategy with Sharpe 2.8 contains a centered-window bug, nor that every timing error inflates performance. Some errors can attenuate results or change them unpredictably. The same-session arm is intentionally unrealistic. The exact magnitudes depend on sample length, volatility, signal construction, turnover and estimator choice.

The note also makes no claim about prospective MarketMind returns. The active prospective holdout is not accessed, scored or summarized here. The only outcomes in this note come from disclosed synthetic IID simulations.

## 7. Falsification and extensions

A useful next test would vary sample size, autocorrelation, heavy tails, volatility clustering and transaction costs while preserving a known zero-predictability null. Another would compare leakage detection methods by inserting known information violations of increasing subtlety. A robust audit tool should detect not only the catastrophic same-session case but also transformations whose leakage enters indirectly through estimation windows.

## 8. Reproduction record

- Experiment: LAB-002
- Replications: 100
- Observations per replication: 4,000
- Seeds: 1000–1099
- Raw results: `experiments/records/LAB-002_runs.csv`
- Summary: `experiments/records/LAB-002_summary.csv`
- Figure: `experiments/records/LAB-002_chart.svg`
- Generator: `experiments/build_lab_records.py`
- Original Lab generator: `experiments/run_lab_v0_1.py`
- Environment: `experiments/records/environment.json`
- Integrity: `experiments/records/manifest.json` contains SHA-256 digests

**Interpretation boundary:** controlled synthetic evidence only; no real-market performance claim; prospective holdout untouched.
