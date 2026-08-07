import numpy as np
import pandas as pd
import pytest

from marketmind.networks import (
    correlation_distance,
    correlation_network,
    minimum_spanning_tree,
    network_snapshot,
    rolling_network_metrics,
)
from marketmind.regimes import classify_regimes


def returns_frame(rows: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(10)
    common = rng.normal(size=rows)
    return pd.DataFrame(
        {
            "a": common + rng.normal(scale=0.1, size=rows),
            "b": common + rng.normal(scale=0.1, size=rows),
            "c": -common + rng.normal(scale=0.2, size=rows),
        },
        index=pd.bdate_range("2020-01-01", periods=rows),
    )


def test_correlation_distance_and_mst() -> None:
    corr = pd.DataFrame(
        [[1.0, 0.5, 0.0], [0.5, 1.0, -0.5], [0.0, -0.5, 1.0]],
        columns=list("abc"),
        index=list("abc"),
    )
    distance = correlation_distance(corr)
    assert distance[0, 1] == pytest.approx(1.0)
    assert np.all(np.diag(distance) == 0)
    tree = minimum_spanning_tree(corr)
    assert tree.number_of_edges() == 2
    with pytest.raises(ValueError):
        correlation_distance(np.ones((2, 3)))


def test_network_snapshot_and_rolling_metrics() -> None:
    frame = returns_frame()
    graph = correlation_network(frame, threshold=0.5)
    assert graph.number_of_nodes() == 3
    snapshot = network_snapshot(frame)
    assert 0 <= snapshot.mean_correlation <= 1
    assert 0 <= snapshot.clustering <= 1
    assert 0 <= snapshot.mst_coherence <= 1
    metrics = rolling_network_metrics(frame, window=80, step=40)
    assert list(metrics.columns) == ["mean_correlation", "clustering", "mst_coherence"]
    assert len(metrics) >= 5


def test_regime_classification_is_past_only() -> None:
    index = pd.bdate_range("2018-01-01", periods=500)
    original = pd.Series(np.sin(np.arange(500) / 20) / 4 + 0.5, index=index)
    altered = original.copy()
    altered.iloc[350:] = 100.0
    first = classify_regimes(original, lookback=200, min_history=60)
    second = classify_regimes(altered, lookback=200, min_history=60)
    pd.testing.assert_frame_equal(first.iloc[:350], second.iloc[:350])
    assert set(first["regime"].dropna().astype(str)) == {"low", "medium", "high"}


def test_regime_validation() -> None:
    with pytest.raises(ValueError):
        classify_regimes(pd.Series([1.0, 2.0]), lookback=1, min_history=2)

