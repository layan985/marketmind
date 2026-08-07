# MarketMind

MarketMind is the research implementation of Layan Oraidi's 2026 Charles H. Dow Award
paper, *The Emergent Market Mind*. It treats the market as an adaptive information
network and estimates its changing structural coherence.

The central object is the Market Intelligence Index (MII):

\[
\mathrm{MII}_t = 0.35 M_t + 0.40 I_t + 0.25 C_t,
\]

where \(M\) measures memory, \(I\) information flow, and \(C\) network connectivity.

## Design principles

- **Causal by construction.** Rolling features, scalers, regimes, and orders use no future data.
- **Scientifically explicit.** Ambiguities in the manuscript become named configuration choices.
- **Auditable.** Every pipeline run retains raw metrics, transformed metrics, configuration, and input hash.
- **Data-source honest.** Public proxies are not presented as licensed-vendor reproductions.
- **Hard to fool.** Costs, naive baselines, resampling, and multiple-testing corrections are first-class APIs.

## Capabilities

| Layer | Package support |
| --- | --- |
| Memory | DFA Hurst, Higuchi dimension, volatility-memory decay |
| Information | Shannon entropy, KSG mutual information, conditional-MI transfer entropy |
| Networks | Threshold graphs, weighted clustering, correlation-distance Prim MST |
| Regimes | Causal monthly rolling terciles |
| Strategies | Nine fixed indicators, next-session execution, costs and slippage |
| Robustness | Cost sweeps, naive baselines, block bootstrap, reality check, deflated Sharpe |
| Delivery | CLI, notebooks, Streamlit dashboard, CI, PyPI and Zenodo metadata |

Start with the [quickstart](quickstart.md) or inspect the [methodology](methodology.md).

!!! warning
    MarketMind is research software. It does not place trades and is not investment advice.

