"""Run the frozen MarketMind public benchmark and persist its evidence bundle."""

from __future__ import annotations

import argparse
from dataclasses import fields
from pathlib import Path

import yaml

from marketmind.benchmark import BenchmarkConfig, run_benchmark_bundle
from marketmind.data import DataConfig, download_yfinance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config/institutional-public-benchmark.yml",
        help="Frozen benchmark YAML configuration.",
    )
    parser.add_argument("--output", default="public-benchmark-bundle")
    args = parser.parse_args()

    path = Path(args.config)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    benchmark_payload = dict(payload.pop("benchmark"))
    claim_boundary = payload.pop("claim_boundary", [])
    purpose = payload.pop("purpose", "institutional_public_benchmark")
    status = payload.pop("status", "historical_public_data_only")
    reference_asset = payload.pop("reference_asset")

    data_fields = {field.name for field in fields(DataConfig)}
    data_payload = {key: value for key, value in payload.items() if key in data_fields}
    data_config = DataConfig(**data_payload)
    prices = download_yfinance(data_config)

    benchmark_config = BenchmarkConfig(
        reference_asset=reference_asset,
        cost_grid_bps=tuple(benchmark_payload.pop("cost_grid_bps")),
        **benchmark_payload,
    )
    source_metadata = {
        "provider": data_config.provider,
        "provider_symbols": data_config.tickers,
        "requested_start": data_config.start,
        "requested_end": data_config.end,
        "price_field": data_config.price_field,
        "purpose": purpose,
        "status": status,
        "claim_boundary": claim_boundary,
    }
    bundle = run_benchmark_bundle(
        prices,
        args.output,
        config=benchmark_config,
        source_metadata=source_metadata,
    )
    print(f"bundle={bundle.output_directory}")
    print(f"input_fingerprint={bundle.input_fingerprint}")
    print(f"evidence_label={bundle.evidence_label}")


if __name__ == "__main__":
    main()
