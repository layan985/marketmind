"""MMSMB-2 / Market Twins benchmark.

A controlled financial time-series falsification benchmark with three tracks:
1. Silent mechanism shift: transition matrix changes while stationary covariance is fixed.
2. Market mirage: volatility scale changes while transition matrix is fixed.
3. Impossible orientation: two linear-Gaussian SEM directions induce the same observational law.

Synthetic evidence only. No trading-performance claim.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score

N_ASSETS = 9
T = 3000
BREAK = T // 2
WINDOW = 240
STEP = 60
REFERENCE_END = 600
EVAL_MIN_START = 720
RHO = 0.30
N_REPS = 200
SEVERITY_REPS = 20
BASE_SEED = 20260822


def equicorr_cov(n: int = N_ASSETS, rho: float = RHO, scale: float = 1.0) -> np.ndarray:
    sigma = np.full((n, n), rho * scale, dtype=float)
    np.fill_diagonal(sigma, scale)
    return sigma


def spectral_radius(a: np.ndarray) -> float:
    return float(np.max(np.abs(np.linalg.eigvals(a))))


def build_mechanisms(n: int = N_ASSETS) -> tuple[np.ndarray, np.ndarray]:
    """Return two stable, sparse VAR(1) propagation mechanisms."""
    a1 = np.eye(n) * 0.10
    a2 = np.eye(n) * 0.10

    for i in range(n):
        a1[(i + 1) % n, i] += 0.105
    for child, parent in [(3, 0), (6, 3), (0, 6)]:
        a1[child, parent] += 0.055

    hub = 4
    for i in range(n):
        if i != hub:
            a2[i, hub] += 0.085
    for i in range(0, n - 1, 2):
        a2[i, i + 1] += 0.075

    max_radius = max(spectral_radius(a1), spectral_radius(a2))
    if max_radius >= 0.80:
        a1 *= 0.75 / max_radius
        a2 *= 0.75 / max_radius
    return a1, a2


def q_for_target(sigma: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Innovation covariance making sigma stationary under x_t=A x_{t-1}+e_t."""
    q = sigma - a @ sigma @ a.T
    q = (q + q.T) / 2
    minimum = float(np.linalg.eigvalsh(q).min())
    if minimum <= 1e-9:
        raise ValueError(f"innovation covariance is not positive definite: {minimum}")
    return q


def stationary_covariance(a: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Solve the discrete Lyapunov equation by fixed-point iteration."""
    sigma = q.copy()
    for _ in range(10000):
        nxt = a @ sigma @ a.T + q
        if np.max(np.abs(nxt - sigma)) < 1e-13:
            return (nxt + nxt.T) / 2
        sigma = nxt
    raise RuntimeError("stationary covariance did not converge")


def simulate_switch(
    rng: np.random.Generator,
    a_pre: np.ndarray,
    q_pre: np.ndarray,
    a_post: np.ndarray,
    q_post: np.ndarray,
    *,
    total: int = T,
    break_index: int = BREAK,
) -> np.ndarray:
    sigma_pre = stationary_covariance(a_pre, q_pre)
    x = np.empty((total, a_pre.shape[0]))
    x[0] = rng.multivariate_normal(np.zeros(a_pre.shape[0]), sigma_pre)
    l_pre = np.linalg.cholesky(q_pre)
    l_post = np.linalg.cholesky(q_post)
    for t in range(1, total):
        if t < break_index:
            a, chol = a_pre, l_pre
        else:
            a, chol = a_post, l_post
        x[t] = a @ x[t - 1] + chol @ rng.standard_normal(a.shape[0])
    return x


def fit_var1(x: np.ndarray) -> np.ndarray:
    y = x[1:]
    z = x[:-1]
    b = np.linalg.lstsq(z, y, rcond=None)[0]
    return b.T


def lag_corr_matrix(x: np.ndarray) -> np.ndarray:
    current = x[1:]
    lagged = x[:-1]
    current = (current - current.mean(axis=0)) / current.std(axis=0, ddof=1)
    lagged = (lagged - lagged.mean(axis=0)) / lagged.std(axis=0, ddof=1)
    return (current.T @ lagged) / (len(current) - 1)


def window_features(x: np.ndarray, a_ref: np.ndarray, lag_ref: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    n = x.shape[1]
    offdiag = ~np.eye(n, dtype=bool)
    for end in range(WINDOW, len(x) + 1, STEP):
        start = end - WINDOW
        if start < EVAL_MIN_START:
            continue
        if start < BREAK < end:
            continue
        window = x[start:end]
        corr = np.corrcoef(window, rowvar=False)
        eig = np.linalg.eigvalsh(corr)
        a_hat = fit_var1(window)
        lag_hat = lag_corr_matrix(window)
        rows.append(
            {
                "end": end,
                "label": int(start >= BREAK),
                "mean_vol": float(window.std(axis=0, ddof=1).mean()),
                "avg_abs_corr": float(np.abs(corr[offdiag]).mean()),
                "pc1_share": float(eig[-1] / eig.sum()),
                "var_shift": float(np.linalg.norm(a_hat - a_ref, ord="fro")),
                "lagcorr_shift": float(np.linalg.norm(lag_hat - lag_ref, ord="fro")),
            }
        )
    return pd.DataFrame(rows)


def auc_score(y: np.ndarray, score: np.ndarray) -> float:
    return float(roc_auc_score(y, score))


def run_track(
    rng: np.random.Generator,
    a_pre: np.ndarray,
    q_pre: np.ndarray,
    a_post: np.ndarray,
    q_post: np.ndarray,
) -> tuple[dict[str, float], pd.DataFrame, np.ndarray]:
    x = simulate_switch(rng, a_pre, q_pre, a_post, q_post)
    a_ref = fit_var1(x[:REFERENCE_END])
    lag_ref = lag_corr_matrix(x[:REFERENCE_END])
    frame = window_features(x, a_ref, lag_ref)
    metrics = ["mean_vol", "avg_abs_corr", "pc1_share", "var_shift", "lagcorr_shift"]
    aucs = {metric: auc_score(frame.label.values, frame[metric].values) for metric in metrics}
    return aucs, frame, x


def summarize(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    se = array.std(ddof=1) / math.sqrt(len(array))
    return {
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "mean_ci95_low": float(array.mean() - 1.96 * se),
        "mean_ci95_high": float(array.mean() + 1.96 * se),
        "replication_p05": float(np.quantile(array, 0.05)),
        "replication_p95": float(np.quantile(array, 0.95)),
    }


def impossible_orientation(seed: int = BASE_SEED + 999) -> dict[str, object]:
    """Empirically verify an exact linear-Gaussian observational equivalence."""
    rng = np.random.default_rng(seed)
    rho = 0.65
    n_datasets = 800
    sample_n = 350
    features: list[list[float]] = []
    labels: list[int] = []
    for k in range(n_datasets):
        label = k % 2
        z1 = rng.standard_normal(sample_n)
        z2 = rng.standard_normal(sample_n)
        if label == 0:
            x = z1
            y = rho * x + math.sqrt(1 - rho * rho) * z2
        else:
            y = z1
            x = rho * y + math.sqrt(1 - rho * rho) * z2
        row = [x.mean(), y.mean(), x.var(ddof=1), y.var(ddof=1), np.cov(x, y, ddof=1)[0, 1]]
        for series in (x, y):
            z = (series - series.mean()) / series.std(ddof=1)
            row.extend([float(np.mean(z**3)), float(np.mean(z**4))])
        features.append(row)
        labels.append(label)

    model = LogisticRegression(max_iter=2000)
    cv = StratifiedKFold(10, shuffle=True, random_state=seed)
    accuracy = cross_val_score(model, np.asarray(features), np.asarray(labels), cv=cv, scoring="accuracy")
    return {
        "rho": rho,
        "observational_covariance": [[1.0, rho], [rho, 1.0]],
        "10fold_cv_accuracy_mean": float(accuracy.mean()),
        "10fold_cv_accuracy_sd": float(accuracy.std(ddof=1)),
        "chance_accuracy": 0.5,
        "do_X_equals_1_predicted_EY": {"X_to_Y": rho, "Y_to_X": 0.0},
        "interpretation": (
            "Both directions induce the same observational bivariate Gaussian law. "
            "Orientation requires extra assumptions, non-observational information, or intervention."
        ),
    }


def main() -> None:
    out = Path(__file__).resolve().parent
    sigma = equicorr_cov()
    a1, a2 = build_mechanisms()
    q1 = q_for_target(sigma, a1)
    q2 = q_for_target(sigma, a2)

    silent = {k: [] for k in ["mean_vol", "avg_abs_corr", "pc1_share", "var_shift", "lagcorr_shift"]}
    mirage = {k: [] for k in silent}
    sample_silent: pd.DataFrame | None = None
    sample_mirage: pd.DataFrame | None = None
    sample_twin: np.ndarray | None = None

    sigma_hi = equicorr_cov(scale=2.25)
    q_hi = q_for_target(sigma_hi, a1)

    for rep in range(N_REPS):
        aucs, frame, x = run_track(np.random.default_rng(BASE_SEED + rep), a1, q1, a2, q2)
        for metric, value in aucs.items():
            silent[metric].append(value)
        if rep == 0:
            sample_silent = frame
            sample_twin = x

        aucs, frame, _ = run_track(np.random.default_rng(BASE_SEED + 10000 + rep), a1, q1, a1, q_hi)
        for metric, value in aucs.items():
            mirage[metric].append(value)
        if rep == 0:
            sample_mirage = frame

    severity_curve: dict[str, object] = {}
    for alpha in [0.25, 0.50, 1.00, 1.50, 2.00]:
        a_post = a1 + alpha * (a2 - a1)
        q_post = q_for_target(sigma, a_post)
        scores = {"var_shift": [], "lagcorr_shift": [], "mean_vol": [], "avg_abs_corr": []}
        for rep in range(SEVERITY_REPS):
            aucs, _, _ = run_track(
                np.random.default_rng(BASE_SEED + 20000 + int(alpha * 1000) + rep),
                a1,
                q1,
                a_post,
                q_post,
            )
            for metric in scores:
                scores[metric].append(aucs[metric])
        severity_curve[f"alpha_{alpha:.2f}"] = {
            "frobenius_mechanism_displacement": float(np.linalg.norm(a_post - a1, ord="fro")),
            "auc": {metric: summarize(values) for metric, values in scores.items()},
        }

    results = {
        "benchmark": "MMSMB-2 / Market Twins",
        "run_date": "2026-08-22",
        "seed_base": BASE_SEED,
        "replications_per_core_track": N_REPS,
        "replications_per_severity_level": SEVERITY_REPS,
        "n_assets": N_ASSETS,
        "observations_per_replication": T,
        "break_index": BREAK,
        "rolling_window": WINDOW,
        "step": STEP,
        "reference_end": REFERENCE_END,
        "evaluation_min_start": EVAL_MIN_START,
        "target_average_correlation": RHO,
        "mechanism_A_frobenius_distance": float(np.linalg.norm(a1 - a2, ord="fro")),
        "mechanism_A1_spectral_radius": spectral_radius(a1),
        "mechanism_A2_spectral_radius": spectral_radius(a2),
        "silent_shift_stationary_covariance_max_abs_difference": float(
            np.max(np.abs(stationary_covariance(a1, q1) - stationary_covariance(a2, q2)))
        ),
        "silent_shift_innovation_covariance_min_eigenvalue": float(
            min(np.linalg.eigvalsh(q1).min(), np.linalg.eigvalsh(q2).min())
        ),
        "silent_mechanism_shift_auc": {metric: summarize(values) for metric, values in silent.items()},
        "market_mirage_auc": {metric: summarize(values) for metric, values in mirage.items()},
        "severity_curve": severity_curve,
        "impossible_orientation": impossible_orientation(),
        "claim_boundary": (
            "Controlled synthetic measurement evidence only. The VAR and lag-correlation baselines are change detectors, "
            "not guarantees of causal identification; no trading or return-prediction claim is made."
        ),
    }

    (out / "mmsmb2_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    np.savetxt(out / "A_pre.csv", a1, delimiter=",", header="A_pre", comments="")
    np.savetxt(out / "A_post.csv", a2, delimiter=",", header="A_post", comments="")
    np.savetxt(out / "Sigma_target.csv", sigma, delimiter=",", header="Sigma_target", comments="")

    assert sample_silent is not None and sample_mirage is not None and sample_twin is not None
    sample_silent.to_csv(out / "silent_shift_windows_seed20260822.csv", index=False)
    sample_mirage.to_csv(out / "market_mirage_windows_seed20260822.csv", index=False)
    columns = [f"asset_{i+1}" for i in range(N_ASSETS)]
    twin = pd.DataFrame(sample_twin, columns=columns)
    twin.insert(0, "regime", np.where(np.arange(T) < BREAK, "A", "B"))
    twin.insert(0, "t", np.arange(T))
    twin.to_csv(out / "market_twin_seed20260822.csv", index=False)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
