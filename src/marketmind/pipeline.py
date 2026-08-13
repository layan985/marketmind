"""End-to-end research pipeline with audit-friendly outputs."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from marketmind._version import __version__
from marketmind.data import frame_fingerprint, read_price_csv
from marketmind.mii import MarketMind, MarketMindConfig, MIIResult


def save_mii_result(
    result: MIIResult,
    directory: str | Path,
    *,
    input_hash: str | None = None,
    extra_metadata: dict[str, object] | None = None,
) -> Path:
    """Persist a hash-verifiable MII result bundle.

    ``artifact_manifest.json`` binds every numerical output to the exact metadata
    written by this run. The manifest deliberately excludes itself from its file list.
    """
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    result.raw_metrics.to_csv(output / "raw_metrics.csv")
    result.normalized_metrics.to_csv(output / "normalized_metrics.csv")
    result.to_frame().to_csv(output / "mii_regimes.csv")
    metadata: dict[str, object] = {
        "package": "marketmind",
        "version": __version__,
        "config": result.metadata(),
    }
    if input_hash is not None:
        metadata["input_sha256"] = input_hash
    if extra_metadata:
        metadata.update(extra_metadata)
    (output / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    artifacts: dict[str, dict[str, object]] = {}
    for name in (
        "raw_metrics.csv",
        "normalized_metrics.csv",
        "mii_regimes.csv",
        "run_metadata.json",
    ):
        path = output / name
        artifacts[name] = {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest = {
        "schema_version": 1,
        "package": "marketmind",
        "version": __version__,
        "artifacts": artifacts,
    }
    (output / "artifact_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output


def run_mii_pipeline(
    prices_path: str | Path,
    output_directory: str | Path,
    *,
    config: MarketMindConfig | None = None,
    primary_columns: Sequence[str] | None = None,
    network_columns: Sequence[str] | None = None,
) -> MIIResult:
    """Read a canonical price CSV, estimate MII, and persist the full audit trail."""
    prices = read_price_csv(prices_path)
    default_primary = ["SPX", "NDX", "SX5E", "ES"]
    selected_primary = (
        list(primary_columns)
        if primary_columns is not None
        else (
            default_primary
            if set(default_primary).issubset(prices.columns)
            else list(prices.columns)
        )
    )
    selected_network = (
        list(network_columns) if network_columns is not None else list(prices.columns)
    )
    missing = (set(selected_primary) | set(selected_network)) - set(prices.columns)
    if missing:
        raise ValueError(f"requested columns are missing from the price file: {sorted(missing)}")
    result = MarketMind(config).fit_transform(
        prices[selected_primary], network_data=prices[selected_network]
    )
    save_mii_result(
        result,
        output_directory,
        input_hash=frame_fingerprint(prices),
        extra_metadata={
            "primary_columns": selected_primary,
            "network_columns": selected_network,
        },
    )
    return result
