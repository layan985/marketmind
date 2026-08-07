"""Construction of the full Market Intelligence Index (MII)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations, permutations
from typing import Literal

import numpy as np
import pandas as pd

from marketmind._validation import validate_frame
from marketmind.fractal import (
    absolute_return_acf_decay,
    dfa_hurst,
    higuchi_fractal_dimension,
    hurst_from_fractal_dimension,
)
from marketmind.information import mutual_information, shannon_entropy, transfer_entropy
from marketmind.networks import network_snapshot
from marketmind.regimes import classify_regimes


@dataclass(frozen=True)
class MarketMindConfig:
    """Paper-aligned defaults for Market Intelligence Index estimation."""

    window: int = 252
    step: int = 21
    entropy_bins: int = 20
    knn_k: int = 3
    higuchi_k_max: int = 20
    acf_max_lag: int = 20
    network_threshold: float = 0.30
    memory_weight: float = 0.35
    information_weight: float = 0.40
    connectivity_weight: float = 0.25
    regime_lookback: int = 756
    regime_min_history: int = 252
    development_end: str | None = None
    normalization: Literal["expanding", "development"] = "expanding"

    def __post_init__(self) -> None:
        if self.window < 32:
            raise ValueError("window must be at least 32 observations")
        if self.step < 1:
            raise ValueError("step must be positive")
        if self.entropy_bins < 2 or self.knn_k < 1:
            raise ValueError("entropy_bins and knn_k are invalid")
        weights = self.memory_weight + self.information_weight + self.connectivity_weight
        if not np.isclose(weights, 1.0):
            raise ValueError("MII component weights must sum to 1")
        if self.normalization == "development" and self.development_end is None:
            raise ValueError("development normalization requires development_end")


@dataclass(frozen=True)
class MIIResult:
    """All intermediate and final outputs from a MarketMind estimation."""

    raw_metrics: pd.DataFrame
    normalized_metrics: pd.DataFrame
    components: pd.DataFrame
    mii: pd.Series
    regimes: pd.DataFrame
    config: MarketMindConfig

    def to_frame(self) -> pd.DataFrame:
        """Return components, MII, rolling thresholds, and regime in one frame."""
        return self.components.join(self.regimes[["mii", "lower", "upper", "regime"]])

    def metadata(self) -> dict[str, object]:
        """Return a JSON-serializable estimator configuration."""
        return asdict(self.config)


def _safe_metric(function: object, *args: object, **kwargs: object) -> float:
    try:
        value = float(function(*args, **kwargs))  # type: ignore[operator]
    except (ValueError, FloatingPointError, np.linalg.LinAlgError):
        return float("nan")
    return value if np.isfinite(value) else float("nan")


def _expanding_minmax(frame: pd.DataFrame) -> pd.DataFrame:
    # Current information may update the causal bound, but no future observation is used.
    lower = frame.expanding(min_periods=2).min()
    upper = frame.expanding(min_periods=2).max()
    span = upper - lower
    result = (frame - lower) / span.where(span > 0)
    return result.where(span > 0, 0.5).clip(0.0, 1.0)


def _development_minmax(frame: pd.DataFrame, development_end: str) -> pd.DataFrame:
    mask = frame.index <= pd.Timestamp(development_end)
    development = frame.loc[mask]
    if development.shape[0] < 2:
        raise ValueError("development period has fewer than two metric observations")
    lower = development.min()
    upper = development.max()
    span = (upper - lower).replace(0.0, np.nan)
    result = (frame - lower) / span
    return result.fillna(0.5).clip(0.0, 1.0)


class MarketMind:
    """Estimate the paper's full Market Intelligence Index.

    ``fit_transform`` accepts a wide panel of prices or returns. All raw features are
    computed from trailing windows only. Estimation dates are spaced by ``step`` and
    then carried forward to the intervening trading days.
    """

    MEMORY_FEATURES = ("hurst", "fractal_hurst", "acf_persistence")
    INFORMATION_FEATURES = ("entropy_order", "transfer_entropy", "mutual_information")
    CONNECTIVITY_FEATURES = ("mean_correlation", "clustering", "mst_coherence")

    def __init__(self, config: MarketMindConfig | None = None) -> None:
        self.config = config or MarketMindConfig()

    def _raw_metrics(
        self, returns: pd.DataFrame, network_returns: pd.DataFrame | None = None
    ) -> pd.DataFrame:
        config = self.config
        network_panel = returns if network_returns is None else network_returns
        records: list[dict[str, object]] = []
        for end in range(config.window, len(returns) + 1, config.step):
            sample = returns.iloc[end - config.window : end].dropna(axis=1, how="all")
            usable = [column for column in sample if sample[column].dropna().size >= config.window // 2]
            sample = sample[usable].dropna(how="any")
            if sample.shape[0] < config.window // 2 or sample.shape[1] < 2:
                continue

            hurst_values: list[float] = []
            fractal_hurst_values: list[float] = []
            persistence_values: list[float] = []
            entropy_values: list[float] = []
            for column in sample:
                series = sample[column].to_numpy()
                k_max = min(config.higuchi_k_max, max(2, (len(series) - 1) // 3))
                hurst_values.append(_safe_metric(dfa_hurst, series))
                # Higuchi is applied to the reconstructed log-price path so D and H=2-D
                # share the paper's self-affine interpretation.
                dimension = _safe_metric(higuchi_fractal_dimension, np.cumsum(series), k_max=k_max)
                fractal_hurst_values.append(hurst_from_fractal_dimension(dimension))
                decay = _safe_metric(
                    absolute_return_acf_decay,
                    series,
                    max_lag=min(config.acf_max_lag, max(2, len(series) // 4)),
                )
                persistence_values.append(float(np.exp(-decay)) if np.isfinite(decay) else 0.0)
                entropy_values.append(
                    _safe_metric(
                        shannon_entropy,
                        series,
                        bins=config.entropy_bins,
                        normalize=True,
                    )
                )

            mi_values = [
                _safe_metric(mutual_information, sample[left], sample[right], k=config.knn_k)
                for left, right in combinations(sample.columns, 2)
            ]
            te_values = [
                _safe_metric(transfer_entropy, sample[left], sample[right], k=config.knn_k)
                for left, right in permutations(sample.columns, 2)
            ]
            date = returns.index[end - 1]
            network_sample = network_panel.loc[:date].tail(config.window).dropna(axis=1, how="all")
            network_sample = network_sample.dropna(how="any")
            if network_sample.shape[0] < config.window // 2 or network_sample.shape[1] < 2:
                continue
            network = network_snapshot(network_sample, threshold=config.network_threshold)
            records.append(
                {
                    "date": date,
                    "hurst": np.nanmean(hurst_values),
                    "fractal_hurst": np.nanmean(fractal_hurst_values),
                    "acf_persistence": np.nanmean(persistence_values),
                    "entropy_order": 1.0 - np.nanmean(entropy_values),
                    "transfer_entropy": np.nanmean(te_values),
                    "mutual_information": np.nanmean(mi_values),
                    "mean_correlation": network.mean_correlation,
                    "clustering": network.clustering,
                    "mst_coherence": network.mst_coherence,
                }
            )
        if not records:
            raise ValueError("no valid rolling windows could be estimated")
        return pd.DataFrame.from_records(records).set_index("date").sort_index()

    def fit_transform(
        self,
        data: pd.DataFrame,
        *,
        network_data: pd.DataFrame | None = None,
        input_type: Literal["prices", "returns"] = "prices",
    ) -> MIIResult:
        """Compute raw metrics, normalized components, MII, and causal regimes.

        ``data`` is the primary market panel used for memory and information flow.
        ``network_data`` may provide a broader cross-section for connectivity (for
        example, the paper's sector ETFs); when omitted, the primary panel is reused.
        Both inputs follow the same ``input_type`` convention.
        """
        frame = validate_frame(data, minimum_columns=2).ffill()
        network_frame = (
            validate_frame(network_data, minimum_columns=2).ffill()
            if network_data is not None
            else frame
        )
        if input_type == "prices":
            if (frame <= 0).any().any() or (network_frame <= 0).any().any():
                raise ValueError("prices must be strictly positive")
            returns = np.log(frame).diff().dropna(how="all")
            network_returns = np.log(network_frame).diff().dropna(how="all")
        elif input_type == "returns":
            returns = frame
            network_returns = network_frame
        else:
            raise ValueError("input_type must be 'prices' or 'returns'")

        raw = self._raw_metrics(returns, network_returns)
        if self.config.normalization == "development":
            assert self.config.development_end is not None
            normalized = _development_minmax(raw, self.config.development_end)
        else:
            normalized = _expanding_minmax(raw)

        components_at_steps = pd.DataFrame(index=normalized.index)
        components_at_steps["memory"] = normalized[list(self.MEMORY_FEATURES)].mean(axis=1)
        components_at_steps["information"] = normalized[list(self.INFORMATION_FEATURES)].mean(axis=1)
        components_at_steps["connectivity"] = normalized[list(self.CONNECTIVITY_FEATURES)].mean(axis=1)
        mii_at_steps = (
            self.config.memory_weight * components_at_steps["memory"]
            + self.config.information_weight * components_at_steps["information"]
            + self.config.connectivity_weight * components_at_steps["connectivity"]
        ).rename("mii")

        target_index = returns.index[returns.index >= raw.index.min()]
        components = components_at_steps.reindex(target_index).ffill()
        mii = mii_at_steps.reindex(target_index).ffill().clip(0.0, 1.0)
        regimes = classify_regimes(
            mii,
            lookback=self.config.regime_lookback,
            min_history=min(self.config.regime_min_history, max(2, len(mii) // 3)),
            monthly=True,
        )
        return MIIResult(raw, normalized, components, mii, regimes, self.config)


def mii_light(prices: pd.Series, breadth: pd.Series, *, z_window: int = 252) -> pd.DataFrame:
    """Compute the simplified MII-Light practitioner proxy from Appendix B.

    Trend strength uses the slope of the EMA(20)/EMA(100) differential; volatility
    uses an ATR-like close-to-close proxy ranked over 63 days; breadth is a 5-day EMA.
    Trend z-scores are mapped through their empirical normal CDF so the composite
    remains on ``[0, 1]``.
    """
    from scipy.stats import norm

    price = pd.to_numeric(prices, errors="coerce").sort_index()
    breadth_series = pd.to_numeric(breadth, errors="coerce").reindex(price.index).ffill()
    ema20 = price.ewm(span=20, adjust=False).mean()
    ema100 = price.ewm(span=100, adjust=False).mean()
    differential = ema20 / ema100 - 1.0
    slope = differential.diff(5) / 5.0
    trend_z = (slope - slope.rolling(z_window).mean()) / slope.rolling(z_window).std(ddof=1)
    trend_score = pd.Series(norm.cdf(trend_z), index=price.index)
    atr_ratio = price.diff().abs().rolling(14).mean() / price
    volatility_percentile = atr_ratio.rolling(63).rank(pct=True)
    volatility_score = 1.0 - volatility_percentile
    breadth_score = breadth_series.ewm(span=5, adjust=False).mean().clip(0.0, 1.0)
    composite = 0.40 * trend_score + 0.30 * volatility_score + 0.30 * breadth_score
    return pd.DataFrame(
        {
            "trend_strength": trend_score,
            "volatility_regime": volatility_score,
            "breadth_coherence": breadth_score,
            "mii_light": composite.clip(0.0, 1.0),
        }
    )
