"""Generate MMSMB-1: MarketMind Structural Market Benchmark v0.1.

The generator is deterministic and discloses the latent truth used to create the
observed price panel. It is designed for measurement-method benchmarking, not
for claims about real financial returns.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SEED = 20260817
N = 1800
K = 9
ASSETS = [f"A{i:02d}" for i in range(1, K + 1)]


def auc_binary(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    pos = y.astype(bool)
    n_pos = int(pos.sum())
    n_neg = int((~pos).sum())
    rank_sum = float(ranks[pos].sum())
    return (rank_sum - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def avg_abs_corr(window: np.ndarray) -> float:
    frame = pd.DataFrame(window).dropna(axis=1, how="any")
    corr = frame.corr().to_numpy()
    tri = np.triu_indices_from(corr, k=1)
    return float(np.nanmean(np.abs(corr[tri])))


def generate() -> dict[str, object]:
    rng = np.random.default_rng(SEED)
    dates = pd.bdate_range("2019-01-02", periods=N)

    regime = np.zeros(N, dtype=int)
    t = 0
    state = 0
    while t < N:
        duration = int(rng.integers(120, 250))
        regime[t:min(N, t + duration)] = state
        state = (state + 1) % 3
        t += duration

    connectivity_map = np.array([0.20, 0.50, 0.82])
    volatility_map = np.array([0.006, 0.010, 0.017])
    memory_map = np.array([0.05, 0.25, 0.48])
    noise_map = np.array([1.00, 0.85, 0.70])

    structural_break = np.arange(N) >= 900
    latent_connectivity = connectivity_map[regime]
    volatility = volatility_map[regime]
    memory = memory_map[regime]
    noise_level = noise_map[regime]

    returns = np.zeros((N, K))
    factor = np.zeros(N)
    idio = np.zeros((N, K))

    for i in range(1, N):
        factor[i] = memory[i] * factor[i - 1] + rng.normal()
        idio[i] = 0.12 * idio[i - 1] + rng.normal(size=K)
        base_load = 0.15 + 0.72 * latent_connectivity[i]
        loads = np.linspace(base_load * 0.88, base_load * 1.12, K)
        if structural_break[i]:
            loads[[0, 4]] *= [1.25, 0.78]
        r = volatility[i] * (loads * factor[i] + noise_level[i] * idio[i])
        if i > 1:
            if not structural_break[i]:
                r[1] += 0.24 * returns[i - 1, 0]
                r[3] += 0.18 * returns[i - 1, 2]
            else:
                r[5] += 0.26 * returns[i - 1, 4]
                r[8] += 0.20 * returns[i - 1, 6]
        returns[i] = r

    events = [
        {"index": 350, "event": "outlier", "asset": "A01", "magnitude_sigma": 11.0},
        {"index": 900, "event": "structural_break", "asset": "ALL", "magnitude_sigma": 0.0},
        {"index": 1230, "event": "outlier", "asset": "A06", "magnitude_sigma": -9.0},
        {"index": 1450, "event": "missing_block_start", "asset": "A08", "magnitude_sigma": 0.0},
        {"index": 1464, "event": "missing_block_end", "asset": "A08", "magnitude_sigma": 0.0},
    ]
    returns[350, 0] += 11 * volatility[350]
    returns[1230, 5] -= 9 * volatility[1230]
    prices = 100 * np.exp(np.cumsum(returns, axis=0))

    missing = rng.random((N, K)) < 0.004
    missing[:120] = False
    missing[1450:1465, 7] = True
    observed_prices = prices.copy()
    observed_prices[missing] = np.nan
    price_df = pd.DataFrame(observed_prices, columns=ASSETS, index=dates)
    price_df.index.name = "date"
    price_df.to_csv(ROOT / "prices.csv", float_format="%.8f")

    info_direction = np.where(structural_break, "A05>A06|A07>A09", "A01>A02|A03>A04")
    latent_df = pd.DataFrame({
        "date": dates,
        "regime": regime,
        "latent_connectivity": latent_connectivity,
        "volatility_state": regime,
        "volatility_scale": volatility,
        "memory_parameter": memory,
        "information_direction": info_direction,
        "structural_break": structural_break.astype(int),
        "noise_level": noise_level,
        "missing_cells": missing.sum(axis=1),
    })
    latent_df.to_csv(ROOT / "latent_state.csv", index=False, float_format="%.6f")
    pd.DataFrame(events).assign(date=lambda x: [dates[i] for i in x["index"]]).to_csv(ROOT / "event_log.csv", index=False)

    graph = {
        "version": "MMSMB-1-v0.1",
        "pre_break_edges": [
            {"source": "A01", "target": "A02", "lag": 1, "coefficient": 0.24},
            {"source": "A03", "target": "A04", "lag": 1, "coefficient": 0.18},
        ],
        "post_break_edges": [
            {"source": "A05", "target": "A06", "lag": 1, "coefficient": 0.26},
            {"source": "A07", "target": "A09", "lag": 1, "coefficient": 0.20},
        ],
        "break_index": 900,
        "break_date": str(dates[900].date()),
    }
    (ROOT / "causal_graph.json").write_text(json.dumps(graph, indent=2) + "\n")

    metric, truth = [], []
    clean_returns = pd.DataFrame(returns, index=dates, columns=ASSETS)
    for i in range(59, N):
        metric.append(avg_abs_corr(clean_returns.iloc[i - 59:i + 1].to_numpy()))
        truth.append(int(regime[i] == 2))
    metric = np.asarray(metric)
    truth = np.asarray(truth)
    baseline = {
        "version": "MMSMB-1-v0.1",
        "baseline": "60-day average absolute correlation",
        "high_connectivity_auc": auc_binary(truth, metric),
        "metric_latent_connectivity_correlation": float(np.corrcoef(metric, latent_connectivity[59:])[0, 1]),
        "observed_missing_fraction": float(np.mean(missing)),
        "outlier_events": 2,
        "structural_breaks": 1,
        "n_sessions": N,
        "n_assets": K,
    }
    (ROOT / "baseline_results.json").write_text(json.dumps(baseline, indent=2) + "\n")
    config = {
        "version": "MMSMB-1-v0.1",
        "seed": SEED,
        "n_sessions": N,
        "n_assets": K,
        "start_date": str(dates[0].date()),
        "regime_connectivity": connectivity_map.tolist(),
        "regime_volatility": volatility_map.tolist(),
        "regime_memory": memory_map.tolist(),
        "sparse_missing_probability": 0.004,
        "structural_break_index": 900,
    }
    (ROOT / "generator_config.json").write_text(json.dumps(config, indent=2) + "\n")
    return baseline


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
