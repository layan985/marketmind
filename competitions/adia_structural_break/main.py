"""MarketMind submission scaffold for the 2026 ADIA Structural Break Open Benchmark.

The model is intentionally different from the large stacked-feature solutions published
for the original challenge. It compresses each series into a small set of regime-change
statistics derived from MarketMind's research themes: distribution shift, memory shift,
local boundary discontinuity, scale shift, and spectral reorganization.

Required CrunchDAO interface: train() + infer().
"""

from __future__ import annotations

from pathlib import Path
import math
import os

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


MODEL_FILE = "marketmind_structural_break.joblib"


def _safe_std(x: np.ndarray) -> float:
    return float(np.std(x, ddof=1)) if len(x) > 1 else 0.0


def _acf1(x: np.ndarray) -> float:
    if len(x) < 4:
        return 0.0
    a, b = x[:-1], x[1:]
    sa, sb = np.std(a), np.std(b)
    if sa < 1e-12 or sb < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _trend(x: np.ndarray) -> float:
    if len(x) < 3:
        return 0.0
    t = np.linspace(-1.0, 1.0, len(x))
    return float(np.polyfit(t, x, 1)[0])


def _robust_scale(x: np.ndarray) -> float:
    if len(x) == 0:
        return 0.0
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return float(1.4826 * mad)


def _spectral_centroid(x: np.ndarray) -> float:
    if len(x) < 8:
        return 0.0
    y = x - np.mean(x)
    power = np.abs(np.fft.rfft(y)) ** 2
    if power.sum() <= 1e-18:
        return 0.0
    freq = np.fft.rfftfreq(len(y))
    return float(np.sum(freq * power) / np.sum(power))


def _spectral_entropy(x: np.ndarray) -> float:
    if len(x) < 8:
        return 0.0
    y = x - np.mean(x)
    power = np.abs(np.fft.rfft(y)) ** 2
    total = power.sum()
    if total <= 1e-18:
        return 0.0
    p = power / total
    p = p[p > 0]
    return float(-(p * np.log(p)).sum() / math.log(max(len(power), 2)))


def _boundary_features(pre: np.ndarray, post: np.ndarray) -> dict[str, float]:
    k = max(5, min(64, len(pre) // 5, len(post) // 5))
    left = pre[-k:]
    right = post[:k]
    pooled = max(_robust_scale(pre), 1e-8)
    return {
        "boundary_level_jump": float(abs(np.mean(right) - np.mean(left)) / pooled),
        "boundary_scale_ratio": float(np.log((_safe_std(right) + 1e-8) / (_safe_std(left) + 1e-8))),
        "boundary_slope_jump": float(abs(_trend(right) - _trend(left)) / pooled),
    }


def _series_features(frame: pd.DataFrame) -> dict[str, float]:
    pre = frame.loc[frame["period"] == 0, "value"].to_numpy(dtype=float)
    post = frame.loc[frame["period"] == 1, "value"].to_numpy(dtype=float)
    if len(pre) == 0 or len(post) == 0:
        return {"invalid_split": 1.0}

    pooled_scale = max(_robust_scale(pre), 1e-8)
    pre_std, post_std = _safe_std(pre), _safe_std(post)

    # Distributional break signals.
    ks = stats.ks_2samp(pre, post, method="asymp")
    wasserstein = stats.wasserstein_distance(pre, post)
    q_pre = np.quantile(pre, [0.1, 0.25, 0.5, 0.75, 0.9])
    q_post = np.quantile(post, [0.1, 0.25, 0.5, 0.75, 0.9])

    f = {
        "invalid_split": 0.0,
        "n_log": float(np.log1p(len(pre) + len(post))),
        "segment_balance": float(len(post) / max(len(pre), 1)),
        "mean_shift_z": float((np.mean(post) - np.mean(pre)) / pooled_scale),
        "median_shift_z": float((np.median(post) - np.median(pre)) / pooled_scale),
        "std_log_ratio": float(np.log((post_std + 1e-8) / (pre_std + 1e-8))),
        "mad_log_ratio": float(np.log((_robust_scale(post) + 1e-8) / (_robust_scale(pre) + 1e-8))),
        "iqr_log_ratio": float(np.log(((q_post[3] - q_post[1]) + 1e-8) / ((q_pre[3] - q_pre[1]) + 1e-8))),
        "tailspread_log_ratio": float(np.log(((q_post[4] - q_post[0]) + 1e-8) / ((q_pre[4] - q_pre[0]) + 1e-8))),
        "quantile_l1_z": float(np.mean(np.abs(q_post - q_pre)) / pooled_scale),
        "ks_stat": float(ks.statistic),
        "ks_logp": float(-np.log10(max(float(ks.pvalue), 1e-300))),
        "wasserstein_z": float(wasserstein / pooled_scale),
        # MarketMind-style memory / organization changes.
        "acf1_pre": _acf1(pre),
        "acf1_post": _acf1(post),
        "acf1_shift": float(_acf1(post) - _acf1(pre)),
        "trend_pre_z": float(_trend(pre) / pooled_scale),
        "trend_post_z": float(_trend(post) / pooled_scale),
        "trend_shift_z": float((_trend(post) - _trend(pre)) / pooled_scale),
        "spectral_centroid_shift": float(_spectral_centroid(post) - _spectral_centroid(pre)),
        "spectral_entropy_shift": float(_spectral_entropy(post) - _spectral_entropy(pre)),
    }
    f.update(_boundary_features(pre, post))
    return f


def extract_features(X: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    ids: list[object] = []
    for series_id, frame in X.groupby(level="id", sort=False):
        rows.append(_series_features(frame))
        ids.append(series_id)
    out = pd.DataFrame(rows, index=pd.Index(ids, name="id"))
    return out.replace([np.inf, -np.inf], np.nan)


def train(X_train: pd.DataFrame, y_train: pd.Series, model_directory_path: str = "resources", **_: object) -> None:
    features = extract_features(X_train)
    y = y_train.reindex(features.index).astype(int)
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("model", HistGradientBoostingClassifier(
            learning_rate=0.045,
            max_iter=350,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            min_samples_leaf=25,
            random_state=2026,
        )),
    ])
    model.fit(features, y)
    path = Path(model_directory_path)
    path.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "columns": list(features.columns)}, path / MODEL_FILE)


def infer(X_test: pd.DataFrame, model_directory_path: str = "resources", **_: object) -> pd.Series:
    artifact = joblib.load(Path(model_directory_path) / MODEL_FILE)
    features = extract_features(X_test)
    features = features.reindex(columns=artifact["columns"])
    probability = artifact["model"].predict_proba(features)[:, 1]
    return pd.Series(probability, index=features.index, name="prediction")
