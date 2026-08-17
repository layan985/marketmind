# MMSMB-1 Codebook

## `prices.csv`

`date` plus synthetic assets `A01`–`A09`. Prices begin at 100 before compounding synthetic returns. Missing cells are deliberately injected and must not be silently forward-filled without disclosure.

## `latent_state.csv`

- `regime` — integer latent state {0,1,2}.
- `latent_connectivity` — generating common-factor connectivity level.
- `volatility_state` — generating volatility state; aligned with regime in v0.1.
- `volatility_scale` — return-scale parameter.
- `memory_parameter` — AR coefficient applied to the latent common factor.
- `information_direction` — active lagged directed edges in the generator.
- `structural_break` — 0 before the graph/loading break, 1 after.
- `noise_level` — idiosyncratic noise multiplier.
- `missing_cells` — number of missing observed prices on the date.

## `causal_graph.json`

Discloses the lag-one directed edges used before and after the structural break.

## `event_log.csv`

Discloses two outlier shocks, one structural break and one contiguous missing-data episode.

## Baseline

`baseline_results.json` reports a deliberately simple 60-day average-absolute-correlation baseline. It is included so complex methods must demonstrate an advantage over a transparent comparator rather than only over chance.
