# MMSMB-1 Benchmark Challenge Submission Protocol

## Principle

Ignore MarketMind. Bring your own model. The benchmark exists to compare methods against disclosed synthetic ground truth, not to validate MarketMind. Results that disagree with MarketMind are explicitly welcome.

## Frozen comparison task

- Benchmark: `MMSMB-1-v0.1`
- Sessions: 1,800
- Assets: 9
- Development segment: first 900 sessions
- Held-out segment: final 900 sessions
- Primary metrics: held-out accuracy, adjusted Rand index (ARI), normalized mutual information (NMI)
- If cluster labels require alignment, learn the mapping on the development segment only. Do not use held-out labels for mapping, tuning or model selection.

## Any method is eligible

HMMs, Markov-switching models, change-point detectors, graph learners, deep state models, volatility rules, clustering systems and simple heuristics are all eligible. A method does not receive credit for complexity.

## Required submission record

Provide `method / author / code / version / accuracy / ARI / NMI / notes`, plus a public code URL and exact commit/release; preprocessing and missing-data handling; random seeds; held-out predictions or a deterministic reproduction command; deviations from the frozen split; and a one-paragraph interpretation including failures.

Open a GitHub issue using the MMSMB-1 challenge template or submit a pull request. Reproducible accepted entries are added to `leaderboard.csv` with permanent author credit.
