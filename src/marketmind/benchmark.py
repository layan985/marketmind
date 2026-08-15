"""Institutional benchmark and client-evidence bundle generation.

This module evaluates MarketMind-related technical signals on a supplied real or
controlled price panel while preserving an explicit evidence boundary. It does not
fetch data itself and it never labels a result as externally validated.
"""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import version as distribution_version
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from marketmind._version import __version__
from marketmind.backtest import WalkForwardEvaluator
from marketmind.data import frame_fingerprint, validate_prices
from marketmind.indicators import all_signals
from marketmind.mii import MarketMind, MarketMindConfig
from marketmind.robustness import (
    block_bootstrap_interval,
    deflated_sharpe_probability,
    naive_baselines,
    transaction_cost_sweep,
    white_reality_check,
)

CANONICAL_EVIDENCE_LABELS = {
    "OFFICIAL SOURCE",
    "REAL PUBLIC DATA",
    "PROVIDER TEST",
    "SYNTHETIC",
    "RANDOMIZED SYNTHETIC",
    "PRODUCTION CLIENT DATA",
    "EXTERNAL REVIEW",
    "INDEPENDENT REPRODUCTION",
    "PENDING VALIDATION",
}


@dataclass(frozen=True)
class BenchmarkConfig:
    """Frozen evaluation contract for one benchmark bundle."""

    reference_asset: str
    evidence_label: str = "REAL PUBLIC DATA"
    cost_bps: float = 5.0
    slippage_bps: float = 0.0
    execution_lag: int = 1
    annualization: int = 252
    block_size: int = 20
    n_bootstrap: int = 1_000
    random_state: int = 20260815
    cost_grid_bps: tuple[float, ...] = (0.0, 5.0, 10.0, 25.0)

    def __post_init__(self) -> None:
        if self.evidence_label not in CANONICAL_EVIDENCE_LABELS:
            raise ValueError("evidence_label must use the canonical MarketMind vocabulary")
        if self.cost_bps < 0 or self.slippage_bps < 0:
            raise ValueError("cost and slippage assumptions must be non-negative")
        if self.execution_lag < 1:
            raise ValueError("execution_lag must be at least one session")
        if self.annualization < 1:
            raise ValueError("annualization must be positive")
        if self.block_size < 1:
            raise ValueError("block_size must be positive")
        if self.n_bootstrap < 100:
            raise ValueError("n_bootstrap must be at least 100")
        if not self.cost_grid_bps or any(value < 0 for value in self.cost_grid_bps):
            raise ValueError("cost_grid_bps must contain non-negative values")


@dataclass(frozen=True)
class BenchmarkBundle:
    """Paths and high-level state for a generated evidence bundle."""

    output_directory: Path
    benchmark_summary: pd.DataFrame
    baseline_summary: pd.DataFrame
    inference: pd.DataFrame
    input_fingerprint: str
    evidence_label: str


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_json(value: object) -> object:
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _manifest_record(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _summary_for_population(summary: pd.DataFrame, population: str) -> pd.DataFrame:
    overall = summary.xs("all", level="regime").copy()
    overall.insert(0, "population", population)
    return overall


def _qa_report(
    prices: pd.DataFrame,
    *,
    reference_asset: str,
    evidence_label: str,
    input_fingerprint: str,
    source_metadata: dict[str, Any],
) -> str:
    index = prices.index
    duplicate_rows = int(index.duplicated().sum())
    missing = {column: int(prices[column].isna().sum()) for column in prices}
    return "\n".join(
        [
            "# MarketMind benchmark QA report",
            "",
            f"**Evidence label:** `{evidence_label}`",
            f"**Reference asset:** `{reference_asset}`",
            f"**Rows:** {len(prices)}",
            f"**Assets:** {prices.shape[1]}",
            f"**First observation:** {index.min()}",
            f"**Last observation:** {index.max()}",
            f"**Duplicate timestamps:** {duplicate_rows}",
            f"**Input frame fingerprint:** `{input_fingerprint}`",
            "",
            "## Missing observations after bounded validation",
            "",
            "```json",
            json.dumps(missing, indent=2, sort_keys=True),
            "```",
            "",
            "## Source metadata",
            "",
            "```json",
            json.dumps(source_metadata, indent=2, sort_keys=True, default=str),
            "```",
            "",
            "## QA boundary",
            "",
            "This report records structural integrity of the supplied analytical panel. It does "
            "not independently verify the upstream vendor's raw observations, licensing, corporate "
            "actions, point-in-time constituents or revision policy. Those remain engagement-level "
            "data-governance responsibilities.",
            "",
        ]
    )


def _limitations() -> str:
    return "\n".join(
        [
            "# Limitations register",
            "",
            "1. Historical performance is not a prospective result and is not evidence of future profitability.",
            "2. Public-provider data can be revised, adjusted or unavailable on rerun; the input fingerprint identifies the exact analytical frame used.",
            "3. Close-to-close daily data does not model intraday execution, bid-ask spread dynamics, market impact, borrow constraints or venue-specific fills.",
            "4. The benchmark uses a fixed family of long-only technical signals; it does not represent the full strategy-design universe a researcher might search.",
            "5. Transaction costs are proportional approximations. Client execution economics may be materially different.",
            "6. The White-style reality check and deflated-Sharpe diagnostic address selection risk only under their stated assumptions; they do not eliminate data-mining risk.",
            "7. Moving-block bootstrap intervals depend on the chosen block length and sample regime.",
            "8. MII regime labels are descriptive state estimates. They are not, by themselves, trade recommendations.",
            "9. Cross-asset panels can contain calendar, currency, stale-price and instrument-structure differences that require engagement-specific review.",
            "10. `REAL PUBLIC DATA` means the analytical input was obtained from a publicly accessible source. It does not mean official-source certification, external review, independent reproduction or production-client validation.",
            "",
        ]
    )


def _claim_register(
    *,
    benchmark_summary: pd.DataFrame,
    baseline_summary: pd.DataFrame,
    inference: pd.DataFrame,
    config: BenchmarkConfig,
    input_fingerprint: str,
) -> pd.DataFrame:
    best_signal = str(benchmark_summary["sharpe"].idxmax())
    best_row = benchmark_summary.loc[best_signal]
    buy_hold = baseline_summary.loc["buy_and_hold"]
    reality_pvalue = float(inference.loc["family_reality_check", "value"])
    rows = [
        {
            "claim": "exact benchmark input frame",
            "number": input_fingerprint,
            "evidence_label": config.evidence_label,
            "source": "input_manifest.json",
            "code_record": "marketmind.benchmark.run_benchmark_bundle",
            "reproducible": "yes with identical input",
            "limitation": "upstream public provider can revise history",
            "status": "observed",
        },
        {
            "claim": "highest historical signal Sharpe in the fixed nine-signal family",
            "number": float(best_row["sharpe"]),
            "evidence_label": config.evidence_label,
            "source": "benchmark_summary.csv",
            "code_record": best_signal,
            "reproducible": "yes with identical input and config",
            "limitation": "selected historical maximum; not a prospective performance claim",
            "status": "descriptive",
        },
        {
            "claim": "buy-and-hold historical Sharpe under the same daily return convention",
            "number": float(buy_hold["sharpe"]),
            "evidence_label": config.evidence_label,
            "source": "baseline_summary.csv",
            "code_record": "buy_and_hold",
            "reproducible": "yes with identical input and config",
            "limitation": "historical reference only",
            "status": "descriptive",
        },
        {
            "claim": "family-level White-style reality-check p-value",
            "number": reality_pvalue,
            "evidence_label": config.evidence_label,
            "source": "inference.csv",
            "code_record": "marketmind.robustness.white_reality_check",
            "reproducible": "yes with identical input, config and seed",
            "limitation": "bootstrap conclusion depends on dependence and search-set assumptions",
            "status": "diagnostic",
        },
    ]
    return pd.DataFrame.from_records(rows)


def _decision_memo(
    *,
    config: BenchmarkConfig,
    prices: pd.DataFrame,
    benchmark_summary: pd.DataFrame,
    baseline_summary: pd.DataFrame,
    inference: pd.DataFrame,
) -> str:
    ranking = benchmark_summary.sort_values("sharpe", ascending=False)
    best_name = str(ranking.index[0])
    best = ranking.iloc[0]
    buy_hold = baseline_summary.loc["buy_and_hold"]
    reality_pvalue = float(inference.loc["family_reality_check", "value"])
    return "\n".join(
        [
            "# MarketMind institutional benchmark memo",
            "",
            f"**Evidence:** `{config.evidence_label}`  ",
            f"**Reference asset:** `{config.reference_asset}`  ",
            f"**Sample:** {prices.index.min()} to {prices.index.max()}  ",
            f"**Execution:** {config.execution_lag}-session lag; {config.cost_bps:g} bps cost + {config.slippage_bps:g} bps slippage per unit turnover",
            "",
            "## Decision summary",
            "",
            f"The strongest historical member of the fixed nine-signal family is `{best_name}` with "
            f"a net daily Sharpe of {float(best['sharpe']):.3f}. The same-sample buy-and-hold "
            f"baseline Sharpe is {float(buy_hold['sharpe']):.3f}. The family-level White-style "
            f"reality-check p-value is {reality_pvalue:.4f}.",
            "",
            "These are historical diagnostics. They are deliberately not promoted to a claim that "
            "MarketMind predicts returns, beats buy-and-hold prospectively, or has been independently "
            "validated. The prospective MarketMind holdout remains a separate sealed evidence stream.",
            "",
            "## What the client can audit",
            "",
            "- exact input fingerprint and source metadata;",
            "- all nine fixed signal results, including adverse and null outcomes;",
            "- naive baselines under the same execution engine;",
            "- transaction-cost sweeps;",
            "- block-bootstrap Sharpe intervals;",
            "- deflated-Sharpe diagnostics and a family-level reality check;",
            "- MII/regime outputs generated from the same price panel;",
            "- machine-readable claim register and artifact hashes.",
            "",
            "## Delivery interpretation",
            "",
            "A client should use this bundle to inspect robustness, assumptions and failure modes. "
            "Any deployment decision still requires client-specific data licensing, execution, market "
            "impact, governance and risk review.",
            "",
        ]
    )


def run_benchmark_bundle(
    prices: pd.DataFrame,
    output_directory: str | Path,
    *,
    config: BenchmarkConfig,
    source_metadata: dict[str, Any] | None = None,
    mii_config: MarketMindConfig | None = None,
) -> BenchmarkBundle:
    """Generate an auditable benchmark and evidence bundle from a supplied price panel.

    The caller is responsible for truthfully choosing ``evidence_label``. The function
    records the label but does not infer that public, production, external-review or
    independent-reproduction status from the data itself.
    """
    clean = validate_prices(prices)
    if config.reference_asset not in clean.columns:
        raise ValueError(f"reference asset '{config.reference_asset}' is not present")
    if len(clean) < 260:
        raise ValueError("benchmark requires at least 260 price observations")

    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    source = dict(source_metadata or {})
    source.setdefault("evidence_label", config.evidence_label)
    source.setdefault("retrieved_at_utc", None)
    source.setdefault("provider", "caller-supplied")

    input_fingerprint = frame_fingerprint(clean)
    returns = clean[config.reference_asset].pct_change(fill_method=None).dropna()
    signals = all_signals(clean[config.reference_asset]).reindex(returns.index)
    evaluator = WalkForwardEvaluator(
        cost_bps=config.cost_bps,
        slippage_bps=config.slippage_bps,
        execution_lag=config.execution_lag,
        annualization=config.annualization,
    )

    mii_settings = mii_config or MarketMindConfig()
    mii_result = MarketMind(mii_settings).fit_transform(clean)
    regimes = mii_result.regimes["regime"].reindex(returns.index)

    evaluated = evaluator.evaluate(returns, signals, regimes=regimes)
    benchmark_summary = _summary_for_population(evaluated.summary, "fixed_signal")
    benchmark_summary.to_csv(output / "benchmark_summary.csv")

    baseline_signals = naive_baselines(
        returns,
        signals["sma_50_200"],
        random_state=config.random_state,
    )
    baseline_evaluated = evaluator.evaluate(returns, baseline_signals, regimes=regimes)
    baseline_summary = _summary_for_population(baseline_evaluated.summary, "baseline")
    baseline_summary.to_csv(output / "baseline_summary.csv")

    signal_costs = transaction_cost_sweep(returns, signals, config.cost_grid_bps).reset_index()
    signal_costs.insert(0, "population", "fixed_signal")
    baseline_costs = transaction_cost_sweep(
        returns, baseline_signals, config.cost_grid_bps
    ).reset_index()
    baseline_costs.insert(0, "population", "baseline")
    cost_sweep = pd.concat([signal_costs, baseline_costs], ignore_index=True)
    cost_sweep.to_csv(output / "cost_sweep.csv", index=False)

    reality = white_reality_check(
        evaluated.net_returns,
        block_size=min(config.block_size, len(returns)),
        n_bootstrap=config.n_bootstrap,
        random_state=config.random_state,
    )
    inference_rows: list[dict[str, object]] = [
        {
            "diagnostic": "family_reality_check",
            "signal": "fixed_nine_signal_family",
            "value": reality.pvalue,
            "lower": np.nan,
            "upper": np.nan,
            "assumption": f"moving blocks; block_size={min(config.block_size, len(returns))}",
        }
    ]
    for name in evaluated.net_returns:
        series = evaluated.net_returns[name]
        lower, upper = block_bootstrap_interval(
            series,
            statistic="sharpe",
            block_size=min(config.block_size, int(series.notna().sum())),
            n_bootstrap=config.n_bootstrap,
            confidence=0.95,
            random_state=config.random_state,
        )
        inference_rows.append(
            {
                "diagnostic": "sharpe_block_interval",
                "signal": name,
                "value": float(benchmark_summary.loc[name, "sharpe"]),
                "lower": lower,
                "upper": upper,
                "assumption": f"95% moving-block interval; block_size={config.block_size}",
            }
        )
        inference_rows.append(
            {
                "diagnostic": "deflated_sharpe_probability",
                "signal": name,
                "value": deflated_sharpe_probability(
                    series,
                    n_trials=len(signals.columns),
                    annualization=config.annualization,
                ),
                "lower": np.nan,
                "upper": np.nan,
                "assumption": f"n_trials={len(signals.columns)} fixed signal family",
            }
        )
    inference = pd.DataFrame.from_records(inference_rows).set_index("diagnostic")
    inference.to_csv(output / "inference.csv")

    mii_result.to_frame().to_csv(output / "mii_regimes.csv")
    evaluated.net_returns.to_csv(output / "signal_net_returns.csv")
    baseline_evaluated.net_returns.to_csv(output / "baseline_net_returns.csv")

    input_manifest = {
        "schema_version": 1,
        "evidence_label": config.evidence_label,
        "reference_asset": config.reference_asset,
        "rows": len(clean),
        "columns": list(clean.columns),
        "first_observation": str(clean.index.min()),
        "last_observation": str(clean.index.max()),
        "frame_fingerprint": input_fingerprint,
        "missing_observations": {column: int(clean[column].isna().sum()) for column in clean},
        "source_metadata": source,
    }
    (output / "input_manifest.json").write_text(
        json.dumps(input_manifest, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )

    run_metadata = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "package": "marketmind",
        "version": __version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": distribution_version("scipy"),
        "benchmark_config": asdict(config),
        "mii_config": mii_result.metadata(),
        "input_fingerprint": input_fingerprint,
        "scope": "historical benchmark evidence; separate from sealed prospective validation",
    }
    (output / "run_metadata.json").write_text(
        json.dumps(run_metadata, indent=2, sort_keys=True, default=_safe_json), encoding="utf-8"
    )

    (output / "QA_REPORT.md").write_text(
        _qa_report(
            clean,
            reference_asset=config.reference_asset,
            evidence_label=config.evidence_label,
            input_fingerprint=input_fingerprint,
            source_metadata=source,
        ),
        encoding="utf-8",
    )
    (output / "LIMITATIONS.md").write_text(_limitations(), encoding="utf-8")
    (output / "DECISION_MEMO.md").write_text(
        _decision_memo(
            config=config,
            prices=clean,
            benchmark_summary=benchmark_summary,
            baseline_summary=baseline_summary,
            inference=inference,
        ),
        encoding="utf-8",
    )
    claims = _claim_register(
        benchmark_summary=benchmark_summary,
        baseline_summary=baseline_summary,
        inference=inference,
        config=config,
        input_fingerprint=input_fingerprint,
    )
    claims.to_csv(output / "CLAIM_REGISTER.csv", index=False)

    manifest_files = sorted(path for path in output.iterdir() if path.is_file())
    artifact_manifest = {
        "schema_version": 1,
        "input_fingerprint": input_fingerprint,
        "artifacts": {path.name: _manifest_record(path) for path in manifest_files},
    }
    (output / "artifact_manifest.json").write_text(
        json.dumps(artifact_manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    return BenchmarkBundle(
        output_directory=output,
        benchmark_summary=benchmark_summary,
        baseline_summary=baseline_summary,
        inference=inference,
        input_fingerprint=input_fingerprint,
        evidence_label=config.evidence_label,
    )
