"""RCA-1: Regime Claim Audit / metamorphic validation for MMSMB-2.

Tests whether regime/mechanism scores earn the claims made about them across:
1. silent mechanism change,
2. nuisance/state change,
3. target-preserving reparameterization,
4. trivial permutation sanity checks.

Synthetic evidence only. No trading-performance or live-market causal claim.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
MMSMB2 = HERE.parent / "mmsmb2" / "run_mmsmb2.py"

spec = importlib.util.spec_from_file_location("mmsmb2", MMSMB2)
m2 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m2)

N_REPS = 200
PERMUTATION_REPS = 50
BASE_SEED = 20260822
METRICS = [
    "mean_vol",
    "avg_abs_corr",
    "pc1_share",
    "var_raw_shift",
    "var_std_shift",
    "lagcorr_shift",
]


def fit_var1_standardized(x: np.ndarray) -> np.ndarray:
    sd = x.std(axis=0, ddof=1)
    z = (x - x.mean(axis=0)) / sd
    return m2.fit_var1(z)


def refs_for(x: np.ndarray) -> dict[str, np.ndarray]:
    ref = x[: m2.REFERENCE_END]
    return {
        "var_raw": m2.fit_var1(ref),
        "var_std": fit_var1_standardized(ref),
        "lagcorr": m2.lag_corr_matrix(ref),
    }


def window_features(x: np.ndarray, refs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    n = x.shape[1]
    offdiag = ~np.eye(n, dtype=bool)
    for end in range(m2.WINDOW, len(x) + 1, m2.STEP):
        start = end - m2.WINDOW
        if start < m2.EVAL_MIN_START:
            continue
        if start < m2.BREAK < end:
            continue
        window = x[start:end]
        corr = np.corrcoef(window, rowvar=False)
        eig = np.linalg.eigvalsh(corr)
        a_raw = m2.fit_var1(window)
        a_std = fit_var1_standardized(window)
        lag = m2.lag_corr_matrix(window)
        rows.append(
            {
                "end": end,
                "label": int(start >= m2.BREAK),
                "mean_vol": float(window.std(axis=0, ddof=1).mean()),
                "avg_abs_corr": float(np.abs(corr[offdiag]).mean()),
                "pc1_share": float(eig[-1] / eig.sum()),
                "var_raw_shift": float(np.linalg.norm(a_raw - refs["var_raw"], ord="fro")),
                "var_std_shift": float(np.linalg.norm(a_std - refs["var_std"], ord="fro")),
                "lagcorr_shift": float(np.linalg.norm(lag - refs["lagcorr"], ord="fro")),
            }
        )
    return pd.DataFrame(rows)


def summarize(values: list[float]) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    se = a.std(ddof=1) / math.sqrt(len(a))
    return {
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "mean_ci95_low": float(a.mean() - 1.96 * se),
        "mean_ci95_high": float(a.mean() + 1.96 * se),
        "replication_p05": float(np.quantile(a, 0.05)),
        "replication_p95": float(np.quantile(a, 0.95)),
    }


def main() -> None:
    sigma = m2.equicorr_cov()
    a_pre, a_post = m2.build_mechanisms()
    q_pre = m2.q_for_target(sigma, a_pre)
    q_post = m2.q_for_target(sigma, a_post)
    sigma_hi = m2.equicorr_cov(scale=2.25)
    q_hi = m2.q_for_target(sigma_hi, a_pre)

    silent = {m: [] for m in METRICS}
    mirage = {m: [] for m in METRICS}
    scale_test = {m: {"spearman": [], "auc_abs_delta": [], "max_relative_score_delta": []} for m in METRICS}

    for rep in range(N_REPS):
        x = m2.simulate_switch(
            np.random.default_rng(BASE_SEED + 60000 + rep), a_pre, q_pre, a_post, q_post
        )
        original = window_features(x, refs_for(x))
        for metric in METRICS:
            silent[metric].append(float(roc_auc_score(original.label, original[metric])))

        rng = np.random.default_rng(BASE_SEED + 70000 + rep)
        scales = np.exp(rng.uniform(np.log(0.05), np.log(20.0), size=m2.N_ASSETS))
        transformed_x = x * scales
        transformed = window_features(transformed_x, refs_for(transformed_x))
        for metric in METRICS:
            rho = float(spearmanr(original[metric], transformed[metric]).statistic)
            auc0 = float(roc_auc_score(original.label, original[metric]))
            auc1 = float(roc_auc_score(transformed.label, transformed[metric]))
            denom = np.maximum(np.abs(original[metric].to_numpy()), 1e-12)
            max_rel = float(
                np.max(np.abs(transformed[metric].to_numpy() - original[metric].to_numpy()) / denom)
            )
            scale_test[metric]["spearman"].append(rho)
            scale_test[metric]["auc_abs_delta"].append(abs(auc1 - auc0))
            scale_test[metric]["max_relative_score_delta"].append(max_rel)

        x_mirage = m2.simulate_switch(
            np.random.default_rng(BASE_SEED + 80000 + rep), a_pre, q_pre, a_pre, q_hi
        )
        mirage_frame = window_features(x_mirage, refs_for(x_mirage))
        for metric in METRICS:
            mirage[metric].append(float(roc_auc_score(mirage_frame.label, mirage_frame[metric])))

    permutation_test = {m: [] for m in METRICS}
    for rep in range(PERMUTATION_REPS):
        x = m2.simulate_switch(
            np.random.default_rng(BASE_SEED + 90000 + rep), a_pre, q_pre, a_post, q_post
        )
        original = window_features(x, refs_for(x))
        permutation = np.random.default_rng(BASE_SEED + 91000 + rep).permutation(m2.N_ASSETS)
        permuted_x = x[:, permutation]
        permuted = window_features(permuted_x, refs_for(permuted_x))
        for metric in METRICS:
            denom = np.maximum(np.abs(original[metric].to_numpy()), 1e-12)
            delta = float(
                np.max(np.abs(permuted[metric].to_numpy() - original[metric].to_numpy()) / denom)
            )
            permutation_test[metric].append(delta)

    results = {
        "benchmark": "RCA-1 / Regime Claim Audit",
        "run_date": "2026-08-22",
        "replications": N_REPS,
        "permutation_replications": PERMUTATION_REPS,
        "silent_mechanism_shift_auc": {m: summarize(v) for m, v in silent.items()},
        "market_mirage_auc": {m: summarize(v) for m, v in mirage.items()},
        "positive_diagonal_reparameterization": {
            m: {k: summarize(v) for k, v in tests.items()} for m, tests in scale_test.items()
        },
        "column_permutation_sanity": {m: summarize(v) for m, v in permutation_test.items()},
        "key_result": {
            "raw_VAR": {
                "silent_shift_auc": float(np.mean(silent["var_raw_shift"])),
                "mirage_auc": float(np.mean(mirage["var_raw_shift"])),
                "rescaling_score_spearman": float(np.mean(scale_test["var_raw_shift"]["spearman"])),
                "rescaling_auc_abs_delta": float(np.mean(scale_test["var_raw_shift"]["auc_abs_delta"])),
            },
            "standardized_VAR": {
                "silent_shift_auc": float(np.mean(silent["var_std_shift"])),
                "mirage_auc": float(np.mean(mirage["var_std_shift"])),
                "rescaling_score_spearman": float(np.mean(scale_test["var_std_shift"]["spearman"])),
                "rescaling_auc_abs_delta": float(np.mean(scale_test["var_std_shift"]["auc_abs_delta"])),
            },
        },
        "interpretation": (
            "The raw VAR Frobenius score detects the silent mechanism change but is strongly representation-dependent "
            "under positive diagonal rescaling. Per-window standardization preserves essentially the same detection "
            "performance while making the score invariant to this reparameterization. This is a model-validation "
            "result, not a causal-identification or trading claim."
        ),
    }
    (HERE / "rca1_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results["key_result"], indent=2))


if __name__ == "__main__":
    main()
