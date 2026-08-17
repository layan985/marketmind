# MMSMB-1 — MarketMind Structural Market Benchmark

**Version:** MMSMB-1-v0.1  
**Purpose:** deterministic benchmark infrastructure for regime, network and directional-information methods.

MMSMB-1 is synthetic by design. The hidden truth is published beside the observed price panel so competing methods can be evaluated against a known generating process.

## Files

- `prices.csv` — generated observed synthetic prices with disclosed missingness.
- `latent_state.csv` — generated regime, latent connectivity, volatility, memory parameter, active information direction, break state, noise and missing-cell count.
- `causal_graph.json` — lagged directed edges before and after the structural break.
- `event_log.csv` — outliers, structural break and missing-data block.
- `generator_config.json` — deterministic generator settings.
- `generator.py` — complete generator.
- `CODEBOOK.md` — field definitions and interpretation boundary.
- `baseline_results.json` — transparent baseline recovery statistics.

## Generate

```bash
python benchmarks/mmsmb1/generator.py
```

The generator and published baseline were frozen with seed `20260817`. Running the generator writes the full CSV outputs deterministically; the large generated CSVs are intentionally not required as source files.

## Benchmark use

A method may use `prices.csv` as the observed input and compare its recovered states, dependence structure or directional edges with the disclosed truth. Researchers should report the generator version, whether any latent file was used during fitting, the evaluation metric and all hyperparameter selection rules.

## Interpretation boundary

MMSMB-1 is not intended to mimic every empirical feature of real markets. Success on MMSMB-1 establishes performance on the disclosed controlled process only. Real-market conclusions require separate evidence.
