"""Institutional benchmark and client-evidence bundle generation.

The benchmark evaluates a fixed signal family and explicit baselines on a supplied
price panel. Evidence labels are supplied by the caller and are never inferred from
performance. Historical benchmark evidence stays separate from the sealed prospective
MarketMind study.
"""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.metadata import version as distribution_version
from pathlib import Path
from typing import Any, cast

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
    """High-level state returned with a generated evidence bundle."""

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


def _scalar_float(value: object) -> float:
    """Extract one numeric scalar from pandas' deliberately broad scalar types."""
    if isinstance(value, pd.Series):
        if len(value) != 1:
            raise ValueError("expected one scalar value")
        value = value.iloc[0]
    return float(cast(Any, value))


def _frame_xs(summary: pd.DataFrame, key: str, *, level: str) -> pd.DataFrame:
    """Return a cross-section while making the DataFrame contract explicit to type checkers."""
    result = summary.xs(key, level=level)
    if not isinstance(result, pd.DataFrame):
        raise TypeError("expected a DataFrame cross-section")
    return result.copy()


def _summary_for_population(summary: pd.DataFrame, population: str) -> pd.DataFrame:
    overall = _frame_xs(summary, "all", level="regime")
    overall.insert(0, "population", population)
    return overall


def _inference_value(inference: pd.DataFrame, diagnostic: str) -> float:
    matches = inference.loc[inference.index == diagnostic, "value"]
    if not isinstance(matches, pd.Series) or len(matches) != 1:
        raise ValueError(f"expected exactly one inference row for {diagnostic}")
    return _scalar_float(matches.iloc[0])


def _qa_report(
    prices: pd.DataFrame,
    *,
    reference_asset: str,
    evidence_label: str,
    input_fingerprint: str,
    source_metadata: dict[str, Any],
) -> str:
    index = prices.index
    missing = {str(column): int(prices[column].isna().sum()) for column in prices.columns}
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
            f"**Duplicate timestamps:** {int(index.duplicated().sum())}",
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
            "2. Public-provider data can be revised; the input fingerprint identifies the exact analytical frame used.",
            "3. Close-to-close daily data does not model intraday fills, spreads, market impact, borrow or venue effects.",
            "4. The benchmark uses a fixed family of nine long-only technical signals rather than the full conceivable strategy universe.",
            "5. Transaction costs and slippage are proportional approximations and can differ materially from client execution economics.",
            "6. Reality-check and deflated-Sharpe diagnostics address selection risk only under their stated assumptions.",
            "7. Moving-block bootstrap intervals depend on the chosen block length and sample regime.",
            "8. MII regime labels are descriptive state estimates, not trade recommendations.",
            "9. Cross-asset panels can contain calendar, currency, stale-price and instrument-structure differences requiring review.",
            "10. `REAL PUBLIC DATA` does not imply official-source certification, external review, independent reproduction or production-client validation.",
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
    best_sharpe = _scalar_float(benchmark_summary.at[best_signal, "sharpe"])
    buy_hold_sharpe = _scalar_float(baseline_summary.at["buy_and_hold", "sharpe"])
    reality_pvalue = _inference_value(inference, "family_reality_check")
    rows: list[dict[str, object]] = [
        {
            "claim": "exact benchmark input frame",
            "number": input_fingerprint,
            "evidence_label": config.evidence_label,
            "source": "input_manifest.json",
            "code_record": "marketmind.benchmark.run_benchmark_bundle",
            "reproducible": "yes with identical input",
            "limitation": "upstream provider can revise history",
            "status": "observed",
        },
        {
            "claim": "highest historical signal Sharpe in the fixed nine-signal family",
            "number": best_sharpe,
            "evidence_label": config.evidence_label,
            "source": "benchmark_summary.csv",
            "code_record": best_signal,
            "reproducible": "yes with identical input and config",
            "limitation": "selected historical maximum; not a prospective performance claim",
            "status": "descriptive",
        },
        {
            "claim": "buy-and-hold historical Sharpe under the same daily return convention",
            "number": buy_hold_sharpe,
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
            "limitation": "depends on dependence and search-set assumptions",
            "status": "diagnostic",
        },
    ]
    return pd.DataFrame(rows)


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
    best_sharpe = _scalar_float(ranking.iloc[0]["sharpe"])
    buy_hold_sharpe = _scalar_float(baseline_summary.at["buy_and_hold", "sharpe"])
    reality_pvalue = _inference_value(inference, "family_reality_check")
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
            f"a net daily Sharpe of {best_sharpe:.3f}. The same-sample buy-and-hold baseline "
            f"Sharpe is {buy_hold_sharpe:.3f}. The family-level White-style reality-check p-value "
            f"is {reality_pvalue:.4f}.",
            "",
            "These are historical diagnostics. They are not promoted to a claim that MarketMind "
            "predicts returns, beats buy-and-hold prospectively, or has been independently validated. "
            "The prospective MarketMind holdout remains a separate sealed evidence stream.",
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
            "The bundle supports audit of assumptions, robustness and failure modes. Deployment still "
            "requires client-specific data licensing, execution, market-impact, governance and risk review.",
            "",
        ]
    )


def _signal_inference(
    evaluated_returns: pd.DataFrame,
    benchmark_summary: pd.DataFrame,
    *,
    config: BenchmarkConfig,
) -> pd.DataFrame:
    reality = white_reality_check(
        evaluated_returns,
        block_size=min(config.block_size, len(evaluated_returns)),
        n_bootstrap=config.n_bootstrap,
        random_state=config.random_state,
    )
    rows: list[dict[str, object]] = [
        {
            "diagnostic": "family_reality_check",
            "signal": "fixed_nine_signal_family",
            "value": reality.pvalue,
            "lower": np.nan,
            "upper": np.nan,
            "assumption": f"moving blocks; block_size={min(config.block_size, len(evaluated_returns))}",
        }
    ]
    trial_count = len(evaluated_returns.columns)
    for raw_name in evaluated_returns.columns:
        name = str(raw_name)
        series = pd.to_numeric(evaluated_returns[raw_name], errors="coerce").dropna()
        observed_sharpe = _scalar_float(benchmark_summary.at[name, "sharpe"])
        finite = series[np.isfinite(series)]
        if len(finite) >= config.block_size and float(finite.std(ddof=1)) > 0:
            lower, upper = block_bootstrap_interval(
                finite,
                statistic="sharpe",
                block_size=min(config.block_size, len(finite)),
                n_bootstrap=config.n_bootstrap,
                confidence=0.95,
                random_state=config.random_state,
            )
            deflated = deflated_sharpe_probability(
                finite,
                n_trials=trial_count,
                annualization=config.annualization,
            )
        else:
            lower, upper, deflated = float("nan"), float("nan"), float("nan")
        rows.extend(
            [
                {
                    "diagnostic": "sharpe_block_interval",
                    "signal": name,
                    "value": observed_sharpe,
                    "lower": lower,
                    "upper": upper,
                    "assumption": f"95% moving-block interval; block_size={config.block_size}",
                },
                {
                    "diagnostic": "deflated_sharpe_probability",
                    "signal": name,
                    "value": deflated,
                    "lower": np.nan,
                    "upper": np.nan,
                    "assumption": f"n_trials={trial_count} fixed signal family",
                },
            ]
        )
    return pd.DataFrame(rows).set_index("diagnostic")


def run_benchmark_bundle(
    prices: pd.DataFrame,
    output_directory: str | Path,
    *,
    config: BenchmarkConfig,
    source_metadata: dict[str, Any] | None = None,
    mii_config: MarketMindConfig | None = None,
) -> BenchmarkBundle:
    """Generate an auditable benchmark and evidence bundle from a supplied price panel."""
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
    reference_prices = clean[config.reference_asset]
    returns = reference_prices.pct_change(fill_method=None).dropna()
    signals = all_signals(reference_prices).reindex(returns.index)
    evaluator = WalkForwardEvaluator(
        cost_bps=config.cost_bps,
        slippage_bps=config.slippage_bps,
        execution_lag=config.execution_lag,
        annualization=config.annualization,
    )

    mii_result = MarketMind(mii_config or MarketMindConfig()).fit_transform(clean)
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
    pd.concat([signal_costs, baseline_costs], ignore_index=True).to_csv(
        output / "cost_sweep.csv", index=False
    )

    inference = _signal_inference(
        evaluated.net_returns,
        benchmark_summary,
        config=config,
    )
    inference.to_csv(output / "inference.csv")

    mii_result.to_frame().to_csv(output / "mii_regimes.csv")
    evaluated.net_returns.to_csv(output / "signal_net_returns.csv")
    baseline_evaluated.net_returns.to_csv(output / "baseline_net_returns.csv")

    input_manifest: dict[str, object] = {
        "schema_version": 1,
        "evidence_label": config.evidence_label,
        "reference_asset": config.reference_asset,
        "rows": len(clean),
        "columns": [str(column) for column in clean.columns],
        "first_observation": str(clean.index.min()),
        "last_observation": str(clean.index.max()),
        "frame_fingerprint": input_fingerprint,
        "missing_observations": {
            str(column): int(clean[column].isna().sum()) for column in clean.columns
        },
        "source_metadata": source,
    }
    (output / "input_manifest.json").write_text(
        json.dumps(input_manifest, indent=2, sort_keys=True, default=str), encoding="utf-8"
    )

    run_metadata: dict[str, object] = {
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
    _claim_register(
        benchmark_summary=benchmark_summary,
        baseline_summary=baseline_summary,
        inference=inference,
        config=config,
        input_fingerprint=input_fingerprint,
    ).to_csv(output / "CLAIM_REGISTER.csv", index=False)

    manifest_files = sorted(path for path in output.iterdir() if path.is_file())
    artifact_manifest: dict[str, object] = {
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
