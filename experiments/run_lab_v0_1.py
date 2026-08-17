"""Controlled MarketMind Lab experiments.

LAB-v0.1 is deliberately synthetic: ground truth is known, no market-return
claim is made, and the active prospective holdout is never touched.

Run:
    python experiments/run_lab_v0_1.py
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "lab_v0_1_results.json"


def quantile_bins(x: np.ndarray, bins: int = 3) -> np.ndarray:
    cuts = np.quantile(x, np.linspace(0, 1, bins + 1)[1:-1])
    return np.digitize(x, cuts, right=False)


def cmi_discrete(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Plug-in I(X;Y|Z) in nats for small categorical arrays."""
    x = np.asarray(x); y = np.asarray(y); z = np.asarray(z)
    if z.ndim == 1:
        z = z[:, None]
    n = len(x)
    xyz: Counter[tuple[int, int, tuple[int, ...]]] = Counter()
    xz: Counter[tuple[int, tuple[int, ...]]] = Counter()
    yz: Counter[tuple[int, tuple[int, ...]]] = Counter()
    zc: Counter[tuple[int, ...]] = Counter()
    for i in range(n):
        zi = tuple(int(v) for v in z[i]); xi, yi = int(x[i]), int(y[i])
        xyz[(xi, yi, zi)] += 1; xz[(xi, zi)] += 1; yz[(yi, zi)] += 1; zc[zi] += 1
    value = 0.0
    for (xi, yi, zi), count in xyz.items():
        denominator = xz[(xi, zi)] * yz[(yi, zi)]
        if denominator:
            value += (count / n) * math.log((count * zc[zi]) / denominator)
    return value


def common_driver_trial(n: int, strength: float, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    a = np.zeros(n); b = np.zeros(n); c = np.zeros(n)
    for t in range(1, n):
        a[t] = 0.55 * a[t - 1] + rng.normal()
        b[t] = 0.30 * b[t - 1] + strength * a[t - 1] + rng.normal()
        c[t] = 0.30 * c[t - 1] + strength * a[t - 1] + rng.normal()
    ab, bb, cb = quantile_bins(a), quantile_bins(b), quantile_bins(c)
    naive = cmi_discrete(bb[:-1], cb[1:], cb[:-1])
    conditional = cmi_discrete(bb[:-1], cb[1:], np.column_stack([cb[:-1], ab[:-1]]))
    return naive, conditional


def annualized_sharpe(x: np.ndarray) -> float:
    sd = np.std(x, ddof=1)
    return float(np.sqrt(252) * np.mean(x) / sd) if sd else float("nan")


def leakage_trial(n: int, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0, 0.01, n); s = pd.Series(returns)
    control_signal = np.sign(s.shift(1).rolling(20, min_periods=20).mean()).fillna(0).to_numpy()
    centered_signal = np.sign(s.rolling(21, center=True, min_periods=21).mean()).fillna(0).to_numpy()
    same_session_signal = np.sign(returns)
    score = s.shift(1).rolling(20, min_periods=20).mean().fillna(0).to_numpy()
    thresholds = np.quantile(np.abs(score[20:]), np.linspace(0.1, 0.9, 17))
    retrospective = []
    for threshold in thresholds:
        signal = np.where(score > threshold, 1, np.where(score < -threshold, -1, 0))
        retrospective.append((annualized_sharpe(signal * returns), signal))
    retrospective_signal = max(retrospective, key=lambda item: item[0])[1]
    candidates = []
    for _ in range(50):
        noise_score = rng.normal(size=n)
        signal = np.sign(pd.Series(noise_score).shift(1).rolling(5, min_periods=5).mean()).fillna(0).to_numpy()
        candidate_returns = signal * returns
        candidates.append((annualized_sharpe(candidate_returns), candidate_returns))
    selected_returns = max(candidates, key=lambda item: item[0])[1]
    return {
        "control": annualized_sharpe(control_signal * returns),
        "centered_window": annualized_sharpe(centered_signal * returns),
        "same_session": annualized_sharpe(same_session_signal * returns),
        "retrospective_threshold": annualized_sharpe(retrospective_signal * returns),
        "survivorship_selection_50": annualized_sharpe(selected_returns),
    }


def avg_abs_corr(window: np.ndarray) -> float:
    corr = np.corrcoef(window, rowvar=False); tri = np.triu_indices_from(corr, k=1)
    return float(np.mean(np.abs(corr[tri])))


def auc_binary(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score); ranks = np.empty_like(order, dtype=float); ranks[order] = np.arange(1, len(score) + 1)
    pos = y == 1; n_pos = int(pos.sum()); n_neg = int((~pos).sum()); rank_sum = float(ranks[pos].sum())
    return (rank_sum - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def network_amputation(seed: int = 42, n: int = 2200, window: int = 80) -> dict[str, float]:
    rng = np.random.default_rng(seed); regime = np.zeros(n, dtype=int); t, state = 0, 0
    while t < n:
        duration = int(rng.integers(120, 260)); regime[t:min(n, t + duration)] = state; state = 1 - state; t += duration
    returns = np.zeros((n, 7))
    for t in range(n):
        factor = rng.normal()
        loads = np.array([0.55, 0.25, 0.22, 0.20, 0.18, 0.20, 0.23]) if regime[t] == 0 else np.array([1.60, 0.75, 0.70, 0.72, 0.68, 0.74, 0.71])
        returns[t] = 0.007 * (loads * factor + rng.normal(size=7))
    full, no_hub, no_random, idx = [], [], [], []
    for t in range(window - 1, n):
        sample = returns[t - window + 1:t + 1]
        full.append(avg_abs_corr(sample)); no_hub.append(avg_abs_corr(sample[:, 1:])); no_random.append(avg_abs_corr(np.delete(sample, 3, axis=1))); idx.append(t)
    full, no_hub, no_random = np.asarray(full), np.asarray(no_hub), np.asarray(no_random)
    truth = regime[idx]; threshold = np.median(full); label_full = full >= threshold
    return {
        "auc_full": auc_binary(truth, full),
        "auc_remove_hub": auc_binary(truth, no_hub),
        "auc_remove_random": auc_binary(truth, no_random),
        "corr_full_hub": float(np.corrcoef(full, no_hub)[0, 1]),
        "corr_full_random": float(np.corrcoef(full, no_random)[0, 1]),
        "label_disagree_remove_hub": float(np.mean(label_full != (no_hub >= threshold))),
        "label_disagree_remove_random": float(np.mean(label_full != (no_random >= threshold))),
    }


def one_outlier(seed: int, n: int = 500, k: int = 8) -> tuple[float, float]:
    rng = np.random.default_rng(seed); factor = rng.normal(size=n)
    panel = np.array([0.35 * factor + rng.normal(size=n) for _ in range(k)]).T
    contaminated = panel.copy(); contaminated[n // 2, 0] += 15
    def mean_corr(frame: np.ndarray, method: str) -> float:
        corr = np.corrcoef(frame, rowvar=False) if method == "pearson" else pd.DataFrame(frame).corr(method="spearman").to_numpy()
        tri = np.triu_indices_from(corr, k=1); return float(corr[tri].mean())
    return abs(mean_corr(contaminated, "pearson") - mean_corr(panel, "pearson")), abs(mean_corr(contaminated, "spearman") - mean_corr(panel, "spearman"))


def main() -> None:
    driver_rows = []
    for strength in [0.0, 0.3, 0.6, 0.9, 1.2]:
        values = np.array([common_driver_trial(4000, strength, 100 + i) for i in range(30)])
        driver_rows.append({"strength": strength, "naive_te_mean": float(values[:, 0].mean()), "conditional_te_mean": float(values[:, 1].mean())})
    leakage = pd.DataFrame([leakage_trial(4000, 1000 + i) for i in range(100)])
    outliers = np.array([one_outlier(200 + i) for i in range(100)])
    results = {
        "version": "LAB-v0.1", "generated": "2026-08-17",
        "interpretation_boundary": "Synthetic controlled experiments only. No prospective trading outcome or return-predictability claim is computed.",
        "common_driver_trap": {"replications": 30, "sample_size": 4000, "rows": driver_rows},
        "leakage_machine": {"replications": 100, "sample_size": 4000, "mean_annualized_sharpe": {key: float(value) for key, value in leakage.mean().items()}},
        "network_amputation": network_amputation(),
        "one_outlier_different_market": {"replications": 100, "pearson_abs_change_mean": float(outliers[:, 0].mean()), "spearman_abs_change_mean": float(outliers[:, 1].mean()), "pearson_to_spearman_sensitivity_ratio": float(outliers[:, 0].mean() / outliers[:, 1].mean())},
    }
    OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
