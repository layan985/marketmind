# MM-BENCH-001 — Multiscale Regime Discrimination

**Status: COMPLETE · RESULT AVAILABLE**  
**Benchmark dataset:** MMSMB-1-v0.1  
**Seed:** 20260817  
**Development cut:** first 900 synthetic sessions; all state-label alignment learned on development data only.  
**Prospective MarketMind trading holdout:** untouched.

## Question

Does the Market Intelligence Index (MII) improve latent-regime recovery beyond simpler state measurements on a synthetic benchmark where the true regime is known?

## Comparators

- MarketMind MII state classification.
- 63-session realized-volatility state classification.
- trend × volatility clustering.
- k-means clustering.
- Gaussian mixture model.
- diagonal Gaussian hidden Markov model.

## Primary result

On the held-out half of MMSMB-1, **realized volatility is the strongest comparator**. It recovers 71.5% of latent regime labels after development-sample label alignment; MII recovers 48.3%.

| Model | Held-out accuracy | ARI | NMI |
|---|---:|---:|---:|
| Realized volatility | **0.715** | 0.446 | 0.400 |
| Gaussian mixture | 0.677 | 0.344 | 0.291 |
| Gaussian HMM | 0.662 | 0.222 | 0.260 |
| k-means | 0.576 | 0.198 | 0.253 |
| **MII** | **0.483** | 0.081 | 0.145 |
| Trend × volatility | 0.279 | 0.437 | 0.433 |

## Interpretation

This is a **benchmark loss for MarketMind**, and it is retained as such. MMSMB-1 deliberately makes volatility, memory and connectivity co-move with the latent state. In this environment, the additional MII complexity does not earn its keep relative to the simplest volatility state rule. The result argues for subtraction and sharper benchmark design rather than another feature.

It is not evidence that realized volatility is universally sufficient, nor is it a real-market trading-performance comparison. The next question is whether there are controlled structures in which memory or directional information changes while volatility does not.

## Frozen evaluation details

- 1,800 synthetic sessions × 9 assets.
- Development/test split at synthetic session 900.
- MII rolling window 252 sessions; evaluation step 21 sessions.
- Fixed development-sample state alignment; test labels are not used to choose the mapping.
- Model seeds fixed at 20260817.
- Missing observations are forward-filled before return construction; this choice is disclosed and should be challenged in sensitivity work.

## Reproduce

- Results: `benchmarks/results/MM-BENCH-001_results.csv`
- MII raw metrics: `benchmarks/results/MM-BENCH-001_mii_raw_metrics.csv`
- MII components: `benchmarks/results/MM-BENCH-001_mii_components.csv`
- Runner: `benchmarks/run_mm_bench_001_003.py`
- Synthetic benchmark: `benchmarks/mmsmb1/`
