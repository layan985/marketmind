"""Command-line interface for reproducible MarketMind runs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal

from marketmind._version import __version__
from marketmind.data import DataConfig, frame_fingerprint, run_data_pipeline, write_dataset
from marketmind.mii import MarketMind, MarketMindConfig
from marketmind.pipeline import run_mii_pipeline, save_mii_result
from marketmind.synthetic import synthetic_market


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="marketmind", description="MarketMind research toolkit")
    parser.add_argument("--version", action="version", version=f"marketmind {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    demo = commands.add_parser("demo", help="run the full pipeline on deterministic synthetic data")
    demo.add_argument("--output", default="artifacts/demo")
    demo.add_argument("--periods", type=int, default=1500)
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--window", type=int, default=252)
    demo.add_argument("--step", type=int, default=21)

    fetch = commands.add_parser("fetch", help="download and fingerprint public data")
    fetch.add_argument("--config", default="config/paper-public.yml")
    fetch.add_argument("--output", default="data/raw/paper-public")

    run = commands.add_parser("run", help="estimate MII from a wide price CSV")
    run.add_argument("prices")
    run.add_argument("--output", default="artifacts/run")
    run.add_argument("--window", type=int, default=252)
    run.add_argument("--step", type=int, default=21)
    run.add_argument("--development-end")
    run.add_argument(
        "--primary", help="comma-separated primary columns; defaults to paper four when present"
    )
    run.add_argument("--network", help="comma-separated network columns; defaults to all columns")

    audit = commands.add_parser(
        "audit", help="run the deterministic research-integrity audit and write its evidence pack"
    )
    audit.add_argument("--output", default="artifacts/research-audit")
    audit.add_argument("--periods", type=int, default=2_000)
    audit.add_argument("--assets", type=int, default=9)
    audit.add_argument("--seed", type=int, default=42)
    audit.add_argument("--window", type=int, default=252)
    audit.add_argument("--step", type=int, default=21)

    commands.add_parser("dashboard", help="launch the interactive Streamlit dashboard")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute the command-line interface."""
    args = _parser().parse_args(argv)
    if args.command == "fetch":
        data_path, manifest_path = run_data_pipeline(args.config, args.output)
        print(f"data: {data_path}\nmanifest: {manifest_path}")
        return 0
    if args.command == "dashboard":
        from marketmind.dashboard import launch

        return launch()
    if args.command == "audit":
        from marketmind.audit import run_research_audit

        audit_result = run_research_audit(
            args.output,
            periods=args.periods,
            assets=args.assets,
            seed=args.seed,
            window=args.window,
            step=args.step,
        )
        status = "passed" if audit_result.passed else "failed"
        print(
            f"research audit {status}: {sum(check.passed for check in audit_result.checks)}/"
            f"{len(audit_result.checks)} checks; evidence: "
            f"{audit_result.output_directory.resolve()}"
        )
        return 0 if audit_result.passed else 1
    if args.command == "run":
        normalization: Literal["expanding", "development"] = (
            "development" if args.development_end else "expanding"
        )
        run_config = MarketMindConfig(
            window=args.window,
            step=args.step,
            development_end=args.development_end,
            normalization=normalization,
        )
        primary = args.primary.split(",") if args.primary else None
        network = args.network.split(",") if args.network else None
        mii_result = run_mii_pipeline(
            args.prices,
            args.output,
            config=run_config,
            primary_columns=primary,
            network_columns=network,
        )
        print(f"wrote {len(mii_result.mii)} MII observations to {Path(args.output).resolve()}")
        return 0
    if args.command == "demo":
        prices = synthetic_market(periods=args.periods, seed=args.seed)
        data_directory = Path(args.output) / "data"
        data_config = DataConfig(
            provider="synthetic",
            tickers={column: column for column in prices.columns},
            start=str(prices.index.min().date()),
            end=str(prices.index.max().date()),
        )
        data_path, manifest_path = write_dataset(
            prices, data_config, output_directory=data_directory
        )
        estimator = MarketMind(MarketMindConfig(window=args.window, step=args.step))
        demo_result = estimator.fit_transform(prices)
        output = save_mii_result(
            demo_result,
            Path(args.output) / "results",
            input_hash=frame_fingerprint(prices),
            extra_metadata={
                "input_data": str(data_path.relative_to(Path(args.output))),
                "input_manifest": str(manifest_path.relative_to(Path(args.output))),
                "synthetic_seed": args.seed,
            },
        )
        print(f"wrote deterministic demo to {output.resolve()}")
        return 0
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
