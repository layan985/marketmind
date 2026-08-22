# MM-RN-004 — Same Market, Different Machine

**22 August 2026**

Financial regime work often starts by asking whether a model can recover a regime. MMSMB-2 starts one step earlier: **what changed?**

A jump in volatility is a state change. A rewiring of temporal propagation is a mechanism change. They can coincide, but they do not have to.

That distinction matters because a sophisticated regime score can look structurally intelligent while mostly rediscovering volatility, correlation, or a first principal component. MMSMB-1 gave MarketMind a reason to take that possibility seriously: simple volatility recovered the synthetic latent regime better than MII, and simple dependence measures reproduced nearly all connectivity-state assignments. MMSMB-2 is designed as a direct falsification test of the proxy explanation.

## Construction

For each regime,

`x_t = A_r x_(t-1) + epsilon_t`, with `epsilon_t ~ N(0, Q_r)`.

Fix a target stationary covariance `Sigma`, choose different stable propagation matrices `A_1` and `A_2`, and set

`Q_r = Sigma - A_r Sigma A_r^T`.

The resulting regimes have the same contemporaneous stationary covariance but different lagged mechanisms.

Across 200 replications, mean volatility, average absolute correlation and PC1 concentration are all approximately chance at detecting the hidden switch (mean AUC 0.505, 0.497 and 0.497). A simple rolling VAR coefficient-distance score reaches 0.797 mean AUC; a lag-correlation distance reaches 0.727.

Then the benchmark is inverted. The transition matrix stays fixed while the stationary covariance scale rises 2.25x. Mean volatility reaches 1.000 AUC, while the VAR and lag-correlation mechanism scores fall back to 0.492 and 0.500.

So the benchmark contains both directions of the falsification:

1. **mechanism changed; easy state summaries did not**;
2. **state changed; mechanism did not**.

## What this adds to the surrounding literature

Recent time-series causal work already makes clear that nonstationarity, interventions and changing mechanisms deserve explicit treatment. TimeGraph supplies synthetic causal-discovery benchmarks with known graphs under realistic temporal complications. SPACETIME jointly searches for temporal causal graphs and regime changepoints in nonstationary data. DoTime extends synthetic temporal SCM generation to intervention windows, counterfactuals and regime-switching mechanisms.

MMSMB-2 is deliberately narrower and finance-facing: its object is not a new general causal-discovery algorithm. It is an adversarial evaluation surface for deciding whether a claimed financial regime measure reacts to a mechanism change, a nuisance/state change, or an observationally non-identifiable target.

## A third answer: cannot know

The benchmark also includes a linear-Gaussian orientation case in which `X -> Y` and `Y -> X` produce the same observational distribution. A classifier supplied with finite-sample moments performs at 0.516 accuracy across 800 generated datasets. The scientifically desirable behavior on such cases is not confident guessing. It is abstention, equivalence-class reporting, or an explicit statement of the extra assumption required for identification.

## Proposed evaluation language

Future submissions should be judged on more than generic regime accuracy:

- **structural sensitivity:** reaction to genuine mechanism changes;
- **nuisance invariance:** quietness under state changes that leave the target mechanism fixed;
- **detection frontier:** performance as structural displacement shrinks;
- **localization:** whether the method identifies what changed rather than only that something moved;
- **abstention quality:** whether confidence falls when the target is observationally unidentified;
- **proxy collapse:** how much of the method's decisions can be reproduced by simple state summaries.

The benchmark is useful even if MarketMind loses. In fact, a method that beats MarketMind cleanly on this surface is exactly the kind of result the project should publish.

## Claim boundary

This note reports controlled synthetic evidence. It does not establish causal identification in real markets and makes no return-prediction or trading-performance claim.

## Related work

- Ferdous, Hossain & Gani (2025), *TimeGraph: Synthetic Benchmark Datasets for Robust Time-Series Causal Discovery*.
- Mameche, Cornanguer, Ninad & Vreeken (2025), *SPACETIME: Causal Discovery from Non-Stationary Time Series*, AAAI-25.
- Thumm, Anthony & Chen (2026), *DoTime: A Synthetic Benchmark Generator for Interventional and Counterfactual Time Series*.
