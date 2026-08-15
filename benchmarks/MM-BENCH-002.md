# MM-BENCH-002 — Leakage Resistance Laboratory

## Question

How much apparent performance or state quality can common time-series leakage errors create?

## Deliberate contamination arms

1. full-sample normalization;
2. full-sample regime terciles;
3. centered rolling windows;
4. same-session execution;
5. future-volatility scaling;
6. retrospective threshold optimization;
7. feature timestamps shifted earlier than availability.

## Control

The leakage-aware MarketMind timing contract with trailing inputs, causal classification, and explicit execution lag.

## Outputs

For every contamination arm report the change in state assignments, metric values, apparent out-of-sample separation, trading metrics where applicable, and exact point where future information entered the pipeline.

The study is educational even if MarketMind itself is not the best-performing method. The target is to quantify contamination, not advertise a strategy.
