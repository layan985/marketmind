import json

import numpy as np
import pandas as pd
import pytest

from marketmind.data import DataConfig, frame_fingerprint, read_price_csv, validate_prices, write_dataset
from marketmind.mii import MarketMind, MarketMindConfig, mii_light
from marketmind.pipeline import run_mii_pipeline
from marketmind.synthetic import synthetic_market


def small_config() -> MarketMindConfig:
    return MarketMindConfig(
        window=64,
        step=32,
        entropy_bins=10,
        higuchi_k_max=8,
        acf_max_lag=8,
        regime_lookback=160,
        regime_min_history=50,
    )


def test_marketmind_end_to_end_and_no_future_contamination() -> None:
    prices = synthetic_market(periods=420, assets=4, seed=30)
    first = MarketMind(small_config()).fit_transform(prices)
    assert first.mii.dropna().between(0, 1).all()
    assert set(first.components) == {"memory", "information", "connectivity"}
    assert len(first.raw_metrics) >= 10
    assert first.metadata()["window"] == 64

    changed = prices.copy()
    changed.iloc[320:] *= np.linspace(1, 3, len(changed) - 320)[:, None]
    second = MarketMind(small_config()).fit_transform(changed)
    cutoff = prices.index[319]
    pd.testing.assert_frame_equal(
        first.raw_metrics.loc[:cutoff], second.raw_metrics.loc[:cutoff], check_exact=False, rtol=1e-12
    )


def test_development_normalization_and_mii_light() -> None:
    prices = synthetic_market(periods=360, assets=4, seed=31)
    development_end = str(prices.index[220].date())
    config = small_config()
    config = MarketMindConfig(**{**config.__dict__, "normalization": "development", "development_end": development_end})
    result = MarketMind(config).fit_transform(prices)
    assert result.normalized_metrics.min().min() >= 0
    assert result.normalized_metrics.max().max() <= 1
    breadth = (prices.gt(prices.rolling(50).mean())).mean(axis=1)
    light = mii_light(prices.iloc[:, 0], breadth, z_window=80)
    assert light["mii_light"].dropna().between(0, 1).all()


def test_dataset_round_trip_and_manifest(tmp_path) -> None:
    prices = synthetic_market(periods=120, assets=3, seed=32)
    config = DataConfig(
        provider="synthetic",
        tickers={column: column for column in prices},
        start="2018-01-01",
        end="2020-01-01",
    )
    data_path, manifest_path = write_dataset(prices, config, output_directory=tmp_path)
    reloaded = read_price_csv(data_path)
    assert list(reloaded.columns) == list(prices.columns)
    manifest = json.loads(manifest_path.read_text())
    assert manifest["rows"] == 120
    assert manifest["frame_fingerprint"] == frame_fingerprint(prices)
    assert len(manifest["sha256"]) == 64


def test_pipeline_writes_audit_files(tmp_path) -> None:
    prices = synthetic_market(periods=260, assets=4, seed=33)
    csv_path = tmp_path / "input.csv"
    prices.to_csv(csv_path)
    result = run_mii_pipeline(csv_path, tmp_path / "output", config=small_config())
    assert len(result.mii) > 0
    assert (tmp_path / "output" / "raw_metrics.csv").exists()
    assert (tmp_path / "output" / "run_metadata.json").exists()


def test_data_validation_errors() -> None:
    with pytest.raises(ValueError):
        validate_prices(pd.DataFrame({"a": [1, -1], "b": [2, 3]}))
    with pytest.raises(ValueError):
        MarketMind(MarketMindConfig(window=64, normalization="development"))
