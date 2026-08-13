"""Deterministic research-integrity audit for MarketMind."""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from importlib.metadata import version as distribution_version
from pathlib import Path

import numpy as np
import pandas as pd

from marketmind._version import __version__
from marketmind.data import frame_fingerprint
from marketmind.indicators import INDICATOR_CATEGORIES
from marketmind.information import transfer_entropy
from marketmind.mii import MarketMind, MarketMindConfig
from marketmind.pipeline import save_mii_result
from marketmind.regimes import classify_regimes
from marketmind.study import confirmatory_market_returns, strategy_exposures
from marketmind.synthetic import synthetic_market, synthetic_market_scenario


@dataclass(frozen=True)
class AuditCheck:
    """One falsifiable controlled check and its observed result."""

    identifier: str
    title: str
    passed: bool
    statistic: object
    criterion: str
    scope: str


@dataclass(frozen=True)
class ResearchAudit:
    """Complete controlled audit result."""

    checks: tuple[AuditCheck, ...]
    output_directory: Path

    @property
    def passed(self) -> bool:
        """Return whether every controlled check passed."""
        return all(check.passed for check in self.checks)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_artifact_manifest(directory: Path) -> bool:
    payload = json.loads((directory / "artifact_manifest.json").read_text(encoding="utf-8"))
    for name, record in payload["artifacts"].items():
        path = directory / name
        if not path.exists():
            return False
        if path.stat().st_size != record["bytes"] or _sha256(path) != record["sha256"]:
            return False
    return True


def _markdown_report(checks: list[AuditCheck], settings: dict[str, object]) -> str:
    passed = sum(check.passed for check in checks)
    lines = [
        "# MarketMind controlled research audit",
        "",
        f"**Result: {passed}/{len(checks)} controlled checks passed.**",
        "",
        "This audit tests implementation invariants and recovery of disclosed synthetic structure. "
        "It is not evidence of trading profitability and is not a substitute for the sealed "
        "2026–2027 prospective holdout.",
        "",
        "| Check | Result | Observed statistic | Acceptance rule |",
        "| --- | --- | --- | --- |",
    ]
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        statistic = json.dumps(check.statistic, sort_keys=True).replace("|", "\\|")
        lines.append(f"| {check.title} | **{status}** | `{statistic}` | {check.criterion} |")
    lines.extend(
        [
            "",
            "## Audit configuration",
            "",
            "```json",
            json.dumps(settings, indent=2, sort_keys=True),
            "```",
            "",
            "## Interpretation boundary",
            "",
            "Passing means the tested code path obeyed the stated invariant in this deterministic "
            "environment. It does not prove that the MII predicts returns. Favorable, null, and "
            "adverse prospective outcomes remain sealed until the registered endpoint.",
            "",
        ]
    )
    return "\n".join(lines)


def run_research_audit(
    output_directory: str | Path,
    *,
    periods: int = 2_000,
    assets: int = 9,
    seed: int = 42,
    window: int = 252,
    step: int = 21,
) -> ResearchAudit:
    """Run and persist the deterministic reviewer-facing audit suite."""
    if periods < window + 300:
        raise ValueError("periods must leave at least 300 observations after the estimation window")
    if assets < 4:
        raise ValueError("assets must be at least four")
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    checks: list[AuditCheck] = []

    scenario = synthetic_market_scenario(periods=periods, assets=assets, seed=seed)
    replay = synthetic_market(periods=periods, assets=assets, seed=seed)
    first_fingerprint = frame_fingerprint(scenario.prices)
    replay_fingerprint = frame_fingerprint(replay)
    checks.append(
        AuditCheck(
            identifier="deterministic_replay",
            title="Seeded synthetic replay",
            passed=first_fingerprint == replay_fingerprint,
            statistic={"sha256": first_fingerprint},
            criterion="identical frame fingerprints",
            scope="Reproducibility of the controlled input generator.",
        )
    )

    config = MarketMindConfig(window=window, step=step)
    result = MarketMind(config).fit_transform(
        scenario.prices.iloc[:, :4], network_data=scenario.prices
    )
    trailing_truth = (
        scenario.latent["coherence"].rolling(window).mean().reindex(result.raw_metrics.index)
    )
    tracking = result.raw_metrics[["mean_correlation", "clustering", "mst_coherence"]].copy()
    tracking.insert(0, "trailing_latent_coherence", trailing_truth)
    tracking.to_csv(output / "latent_connectivity_tracking.csv")
    correlation_names = ["mean_correlation", "clustering", "mst_coherence"]
    correlations = pd.Series(
        {
            name: tracking["trailing_latent_coherence"].corr(tracking[name])
            for name in correlation_names
        },
        dtype=float,
    )
    min_tracking = float(np.min(correlations.to_numpy(dtype=float)))
    checks.append(
        AuditCheck(
            identifier="latent_connectivity_tracking",
            title="Known-structure recovery",
            passed=bool(min_tracking >= 0.75),
            statistic={name: round(float(correlations.loc[name]), 6) for name in correlation_names},
            criterion="every connectivity measure correlates at least 0.75 with trailing latent coherence",
            scope="Construct validity on disclosed synthetic structure; not a return forecast.",
        )
    )

    causal_prices = synthetic_market(periods=520, assets=4, seed=seed + 1)
    causal_config = MarketMindConfig(
        window=64,
        step=16,
        entropy_bins=10,
        higuchi_k_max=8,
        acf_max_lag=8,
        regime_lookback=160,
        regime_min_history=50,
    )
    baseline = MarketMind(causal_config).fit_transform(causal_prices)
    cutoff_position = 379
    changed = causal_prices.copy()
    changed.iloc[cutoff_position + 1 :] *= np.linspace(
        1.0, 5.0, len(changed) - cutoff_position - 1
    )[:, None]
    perturbed = MarketMind(causal_config).fit_transform(changed)
    cutoff = causal_prices.index[cutoff_position]
    before = baseline.raw_metrics.loc[:cutoff]
    after = perturbed.raw_metrics.loc[:cutoff].reindex_like(before)
    max_difference = float(np.nanmax(np.abs(before.to_numpy() - after.to_numpy())))
    checks.append(
        AuditCheck(
            identifier="feature_future_invariance",
            title="Feature look-ahead audit",
            passed=bool(max_difference <= 1e-12),
            statistic={"max_abs_difference": max_difference},
            criterion="future perturbation changes no earlier raw metric beyond 1e-12",
            scope="Trailing feature windows and network snapshots.",
        )
    )

    regime_index = pd.bdate_range("2020-01-01", periods=500)
    original_mii = pd.Series(np.sin(np.arange(500) / 17.0) / 4.0 + 0.5, index=regime_index)
    altered_mii = original_mii.copy()
    altered_mii.iloc[350:] = 10.0
    original_regimes = classify_regimes(original_mii, lookback=200, min_history=60)
    altered_regimes = classify_regimes(altered_mii, lookback=200, min_history=60)
    identical_regime_history = original_regimes.iloc[:350].equals(altered_regimes.iloc[:350])
    checks.append(
        AuditCheck(
            identifier="regime_future_invariance",
            title="Threshold look-ahead audit",
            passed=identical_regime_history,
            statistic={"unchanged_rows": 350},
            criterion="future MII perturbation changes zero prior thresholds or labels",
            scope="Rolling, monthly refreshed regime classification.",
        )
    )

    rng = np.random.default_rng(seed + 2)
    source = rng.normal(size=1_200)
    target = np.zeros(1_200)
    for position in range(1, len(target)):
        target[position] = (
            0.85 * source[position - 1] + 0.15 * target[position - 1] + rng.normal(scale=0.25)
        )
    forward = transfer_entropy(source, target, k=3)
    reverse = transfer_entropy(target, source, k=3)
    direction_margin = float(forward - reverse)
    checks.append(
        AuditCheck(
            identifier="information_direction",
            title="Directional information recovery",
            passed=bool(direction_margin >= 0.15),
            statistic={
                "source_to_target": round(float(forward), 6),
                "target_to_source": round(float(reverse), 6),
                "margin": round(direction_margin, 6),
            },
            criterion="known causal direction exceeds reverse transfer entropy by at least 0.15 nats",
            scope="KSG conditional-mutual-information transfer entropy.",
        )
    )

    contract_index = pd.bdate_range("2024-01-02", periods=260)
    contract_signals = pd.DataFrame(index=contract_index)
    family_values = {
        "trend": (1.0, 1.0, 1.0),
        "breakout": (1.0, 0.0, 0.0),
        "mean_reversion": (0.0, 0.0, 0.0),
    }
    family_offsets = {family: 0 for family in family_values}
    for name, family in INDICATOR_CATEGORIES.items():
        offset = family_offsets[family]
        contract_signals[name] = family_values[family][offset]
        family_offsets[family] += 1
    contract_regimes = pd.Series(
        np.resize(["high", "medium", "low"], len(contract_index)), index=contract_index
    )
    exposures = strategy_exposures(contract_signals, contract_regimes)
    expected = contract_regimes.map({"high": 1.0, "medium": 1.0 / 3.0, "low": 0.0})
    selection_error = float((exposures["regime_aware"] - expected).abs().max())
    contract_returns = pd.Series(rng.normal(0.0, 0.01, len(contract_index)), index=contract_index)
    executed = confirmatory_market_returns(
        contract_returns, contract_signals, contract_regimes, cost_bps=5.0
    )
    first_position = float(executed.positions["regime_aware"].iloc[0])
    checks.append(
        AuditCheck(
            identifier="confirmatory_contract",
            title="Preregistered strategy contract",
            passed=bool(selection_error <= 1e-12 and first_position == 0.0),
            statistic={
                "max_family_selection_error": selection_error,
                "same_session_position": first_position,
            },
            criterion="exact High/Medium/Low family mapping and no same-session execution",
            scope="Executable H1/H2/H3 exposure construction.",
        )
    )

    controlled_run = output / "controlled_run"
    save_mii_result(
        result,
        controlled_run,
        input_hash=first_fingerprint,
        extra_metadata={"controlled_synthetic_seed": seed},
    )
    manifest_valid = _verify_artifact_manifest(controlled_run)
    checks.append(
        AuditCheck(
            identifier="artifact_integrity",
            title="Result-bundle integrity",
            passed=manifest_valid,
            statistic={"verified_files": 4},
            criterion="every declared byte count and SHA-256 digest matches",
            scope="Raw metrics, normalized metrics, MII regimes, and run metadata.",
        )
    )

    settings: dict[str, object] = {
        "package": "marketmind",
        "version": __version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": distribution_version("scipy"),
        "seed": seed,
        "periods": periods,
        "assets": assets,
        "window": window,
        "step": step,
        "scope": "controlled implementation audit; prospective outcomes remain sealed",
    }
    payload = {
        "schema_version": 1,
        "passed": all(check.passed for check in checks),
        "summary": {"passed": sum(check.passed for check in checks), "total": len(checks)},
        "settings": settings,
        "checks": [asdict(check) for check in checks],
    }
    (output / "audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (output / "AUDIT.md").write_text(_markdown_report(checks, settings), encoding="utf-8")
    root_artifacts: dict[str, dict[str, object]] = {}
    for name in ("AUDIT.md", "audit.json", "latent_connectivity_tracking.csv"):
        path = output / name
        root_artifacts[name] = {"bytes": path.stat().st_size, "sha256": _sha256(path)}
    (output / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "artifacts": root_artifacts}, indent=2),
        encoding="utf-8",
    )
    return ResearchAudit(checks=tuple(checks), output_directory=output)
