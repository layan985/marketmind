"""Dynamic correlation-network and minimum-spanning-tree measures."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

from marketmind._validation import validate_frame


@dataclass(frozen=True)
class DynamicNetwork:
    """A dated network snapshot and its paper-aligned summary measures."""

    date: object
    correlation: pd.DataFrame
    graph: WeightedGraph
    mst: WeightedGraph
    mean_correlation: float
    clustering: float
    mst_coherence: float


def correlation_distance(correlation: ArrayLike) -> NDArray[np.float64]:
    """Convert correlation to Mantegna distance ``sqrt(2 * (1-rho))``."""
    rho = np.asarray(correlation, dtype=float)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("correlation must be a square matrix")
    distance = np.sqrt(2.0 * (1.0 - np.clip(rho, -1.0, 1.0)))
    np.fill_diagonal(distance, 0.0)
    return distance


@dataclass
class WeightedGraph:
    """Small dependency-free weighted graph suited to rolling market panels."""

    _nodes: list[object] = field(default_factory=list)
    _edges: dict[frozenset[object], dict[str, float]] = field(default_factory=dict)

    def add_nodes_from(self, nodes: list[object]) -> None:
        for node in nodes:
            if node not in self._nodes:
                self._nodes.append(node)

    def add_edge(self, left: object, right: object, **attributes: float) -> None:
        self.add_nodes_from([left, right])
        self._edges[frozenset((left, right))] = dict(attributes)

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return len(self._edges)

    def nodes(self) -> tuple[object, ...]:
        return tuple(self._nodes)

    def edges(self, data: bool = False) -> list[object]:
        result: list[object] = []
        for key, attributes in self._edges.items():
            left, right = tuple(key)
            result.append((left, right, attributes) if data else (left, right))
        return result

    def neighbors(self, node: object) -> list[object]:
        neighbors: list[object] = []
        for key in self._edges:
            if node in key:
                neighbors.extend(candidate for candidate in key if candidate != node)
        return neighbors

    def edge_data(self, left: object, right: object) -> dict[str, float] | None:
        return self._edges.get(frozenset((left, right)))


def _weighted_clustering(graph: WeightedGraph) -> float:
    if graph.number_of_edges() == 0:
        return 0.0
    max_weight = max(attributes.get("weight", 0.0) for _, _, attributes in graph.edges(data=True))
    if max_weight <= 0:
        return 0.0
    coefficients: list[float] = []
    for node in graph.nodes():
        neighbors = graph.neighbors(node)
        degree = len(neighbors)
        if degree < 2:
            coefficients.append(0.0)
            continue
        triangles = 0.0
        for left, right in combinations(neighbors, 2):
            left_edge = graph.edge_data(node, left)
            right_edge = graph.edge_data(node, right)
            closing_edge = graph.edge_data(left, right)
            if left_edge and right_edge and closing_edge:
                product = (
                    left_edge.get("weight", 0.0)
                    * right_edge.get("weight", 0.0)
                    * closing_edge.get("weight", 0.0)
                ) / max_weight**3
                triangles += product ** (1.0 / 3.0)
        coefficients.append(2.0 * triangles / (degree * (degree - 1)))
    return float(np.mean(coefficients))


def correlation_network(
    returns: pd.DataFrame, *, threshold: float = 0.30, absolute: bool = True
) -> WeightedGraph:
    """Build a thresholded weighted correlation network."""
    frame = validate_frame(returns, minimum_columns=2).dropna(how="any")
    if frame.shape[0] < 3:
        raise ValueError("at least three complete rows are required")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must lie in [0, 1]")
    corr = frame.corr()
    graph = WeightedGraph()
    graph.add_nodes_from(list(corr.columns))
    for i, left in enumerate(corr.columns):
        for right in corr.columns[i + 1 :]:
            raw = float(corr.loc[left, right])
            strength = abs(raw) if absolute else raw
            if strength >= threshold:
                graph.add_edge(left, right, weight=max(0.0, strength), correlation=raw)
    return graph


def minimum_spanning_tree(correlation: pd.DataFrame | ArrayLike) -> WeightedGraph:
    """Construct an MST on the complete correlation-distance graph."""
    if isinstance(correlation, pd.DataFrame):
        labels = list(correlation.columns)
        if list(correlation.index) != labels:
            raise ValueError("correlation DataFrame index and columns must match")
        rho = correlation.to_numpy(dtype=float)
    else:
        rho = np.asarray(correlation, dtype=float)
        labels = list(range(rho.shape[0])) if rho.ndim == 2 else []
    distances = correlation_distance(rho)
    tree = WeightedGraph()
    tree.add_nodes_from(labels)
    selected = {0}
    while len(selected) < len(labels):
        best: tuple[float, int, int] | None = None
        for left in selected:
            for right in range(len(labels)):
                if right in selected:
                    continue
                candidate = (float(distances[left, right]), left, right)
                if best is None or candidate[0] < best[0]:
                    best = candidate
        if best is None:
            raise ValueError("correlation graph is disconnected")
        distance, left, right = best
        tree.add_edge(
            labels[left],
            labels[right],
            distance=distance,
            weight=distance,
            correlation=float(rho[left, right]),
        )
        selected.add(right)
    return tree


def network_snapshot(
    returns: pd.DataFrame, *, threshold: float = 0.30, absolute: bool = True
) -> DynamicNetwork:
    """Compute correlation, threshold network, MST, and connectivity summaries."""
    frame = validate_frame(returns, minimum_columns=2).dropna(how="any")
    if frame.shape[0] < 3:
        raise ValueError("at least three complete rows are required")
    corr = frame.corr()
    graph = correlation_network(frame, threshold=threshold, absolute=absolute)
    mst = minimum_spanning_tree(corr)
    upper = corr.to_numpy()[np.triu_indices(corr.shape[0], k=1)]
    mean_correlation = float(np.mean(np.abs(upper)))
    clustering = _weighted_clustering(graph)
    distances = [data["distance"] for _, _, data in mst.edges(data=True)]
    max_distance = 2.0
    mst_coherence = float(1.0 - np.mean(distances) / max_distance) if distances else 0.0
    return DynamicNetwork(
        date=frame.index[-1],
        correlation=corr,
        graph=graph,
        mst=mst,
        mean_correlation=mean_correlation,
        clustering=clustering,
        mst_coherence=float(np.clip(mst_coherence, 0.0, 1.0)),
    )


def rolling_network_metrics(
    returns: pd.DataFrame,
    *,
    window: int = 252,
    step: int = 21,
    threshold: float = 0.30,
) -> pd.DataFrame:
    """Compute dynamic network metrics with trailing-only windows."""
    frame = validate_frame(returns, minimum_columns=2)
    if window < 20 or step < 1:
        raise ValueError("window must be at least 20 and step must be positive")
    records: list[dict[str, object]] = []
    for end in range(window, len(frame) + 1, step):
        sample = frame.iloc[end - window : end].dropna(how="any")
        if len(sample) < max(20, window // 2):
            continue
        snapshot = network_snapshot(sample, threshold=threshold)
        records.append(
            {
                "date": frame.index[end - 1],
                "mean_correlation": snapshot.mean_correlation,
                "clustering": snapshot.clustering,
                "mst_coherence": snapshot.mst_coherence,
            }
        )
    if not records:
        return pd.DataFrame(columns=["mean_correlation", "clustering", "mst_coherence"])
    return pd.DataFrame.from_records(records).set_index("date")
