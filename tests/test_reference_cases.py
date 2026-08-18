"""Reference cases for publication-grade scientific validation.

These tests intentionally use analytically simple or structurally controlled cases.
They complement ordinary unit tests by checking scientific behavior rather than only
API mechanics.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from marketmind.backtest import cost_adjusted_returns
from marketmind.fractal import dfa_hurst
from marketmind.information import mutual_information, shannon_entropy, transfer_entropy
from marketmind.networks import correlation_distance, minimum_spanning_tree, network_snapshot


def test_dfa_orders_differenced_white_integrated_processes() -> None:
    """DFA should distinguish anti-persistent, white, and integrated controls."""
    rng = np.random.default_rng(42)
    white = rng.normal(size=8192)
    anti_persistent = np.diff(white)
    integrated = np.cumsum(white)

    h_anti = dfa_hurst(anti_persistent, n_scales=16)
    h_white = dfa_hurst(white, n_scales=16)
    h_integrated = dfa_hurst(integrated, n_scales=16)

    assert h_anti < 0.20
    assert 0.40 < h_white < 0.65
    assert 1.30 < h_integrated < 1.70
    assert h_anti < h_white < h_integrated


def test_shannon_entropy_matches_two_equiprobable_states() -> None:
    values = np.array([0.0, 0.0, 1.0, 1.0] * 100)
    assert shannon_entropy(values, bins=2) == pytest.approx(1.0, abs=1e-12)
    assert shannon_entropy(values, bins=2, normalize=True) == pytest.approx(1.0, abs=1e-12)


def test_mutual_information_null_vs_controlled_dependence() -> None:
    rng = np.random.default_rng(43)
    x = rng.normal(size=2000)
    independent = rng.normal(size=2000)
    dependent = x + rng.normal(scale=0.10, size=2000)

    mi_null = mutual_information(x, independent, k=3)
    mi_dep = mutual_information(x, dependent, k=3)

    # Finite-sample KSG estimates need not be exactly zero under independence.
    assert mi_null < 0.15
    assert mi_dep > 1.0
    assert mi_dep > mi_null + 0.8


def test_transfer_entropy_recovers_simulated_direction() -> None:
    rng = np.random.default_rng(44)
    source = rng.normal(size=2000)
    target = np.zeros(2000)
    for t in range(1, target.size):
        target[t] = 0.90 * source[t - 1] + 0.10 * target[t - 1] + rng.normal(scale=0.20)

    forward = transfer_entropy(source, target, k=3)
    reverse = transfer_entropy(target, source, k=3)
    assert forward > reverse + 0.20


def test_correlation_distance_has_known_values() -> None:
    rho = np.array([[1.0, 0.5, -1.0], [0.5, 1.0, 0.0], [-1.0, 0.0, 1.0]])
    distance = correlation_distance(rho)

    assert distance[0, 0] == 0.0
    assert distance[0, 1] == pytest.approx(1.0)
    assert distance[0, 2] == pytest.approx(2.0)
    assert distance[1, 2] == pytest.approx(np.sqrt(2.0))


def test_mst_selects_the_two_shortest_connecting_edges() -> None:
    rho = pd.DataFrame(
        [[1.0, 0.90, 0.10], [0.90, 1.0, 0.80], [0.10, 0.80, 1.0]],
        index=["A", "B", "C"],
        columns=["A", "B", "C"],
    )
    tree = minimum_spanning_tree(rho)
    edges = {frozenset(edge) for edge in tree.edges()}

    assert tree.number_of_nodes() == 3
    assert tree.number_of_edges() == 2
    assert edges == {frozenset(("A", "B")), frozenset(("B", "C"))}


def test_network_summaries_are_invariant_to_column_permutation() -> None:
    rng = np.random.default_rng(45)
    common = rng.normal(size=1000)
    frame = pd.DataFrame(
        {
            "A": common + rng.normal(scale=0.2, size=1000),
            "B": 0.7 * common + rng.normal(scale=0.4, size=1000),
            "C": -0.5 * common + rng.normal(scale=0.5, size=1000),
        }
    )
    first = network_snapshot(frame, threshold=0.20)
    second = network_snapshot(frame[["C", "A", "B"]], threshold=0.20)

    assert first.mean_correlation == pytest.approx(second.mean_correlation)
    assert first.clustering == pytest.approx(second.clustering)
    assert first.mst_coherence == pytest.approx(second.mst_coherence)


def test_execution_lag_blocks_same_session_signal_use() -> None:
    index = pd.RangeIndex(4)
    returns = pd.Series([0.10, 0.20, -0.10, 0.05], index=index)
    signal = pd.Series([1.0, 0.0, 1.0, 0.0], index=index)

    audit = cost_adjusted_returns(returns, signal, cost_bps=0.0, execution_lag=1)

    assert audit["position"].tolist() == [0.0, 1.0, 0.0, 1.0]
    assert audit["gross"].tolist() == pytest.approx([0.0, 0.20, 0.0, 0.05])


def test_transaction_cost_is_charged_on_turnover() -> None:
    index = pd.RangeIndex(3)
    returns = pd.Series([0.0, 0.0, 0.0], index=index)
    signal = pd.Series([1.0, 0.0, 0.0], index=index)

    audit = cost_adjusted_returns(returns, signal, cost_bps=10.0, execution_lag=1)

    # 10 bps on entry and 10 bps on exit.
    assert audit["turnover"].tolist() == [0.0, 1.0, 1.0]
    assert audit["net"].tolist() == pytest.approx([0.0, -0.001, -0.001])
