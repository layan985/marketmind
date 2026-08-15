from pathlib import Path

import numpy as np
import pandas as pd

from marketmind.benchmark import BenchmarkConfig, run_benchmark_bundle


def _fixture_prices() -> pd.DataFrame:
    rng = np.random.default_rng(20260815)
    index = pd.bdate_range("2018-01-02", periods=900)
    common = rng.normal(0.0002, 0.008, len(index))
    columns: dict[str, np.ndarray] = {}
    for offset, name in enumerate(["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT"]):
        idiosyncratic = rng.normal(0.0, 0.004 + offset * 0.0002, len(index))
        returns = common * (0.9 - offset * 0.05) + idiosyncratic
        columns[name] = 100.0 * np.exp(np.cumsum(returns))
    return pd.DataFrame(columns, index=index)


def test_benchmark_bundle_writes_auditable_delivery(tmp_path: Path) -> None:
    bundle = run_benchmark_bundle(
        _fixture_prices(),
        tmp_path,
        config=BenchmarkConfig(
            reference_asset="SPY",
            evidence_label="SYNTHETIC",
            n_bootstrap=100,
            block_size=10,
            cost_grid_bps=(0.0, 5.0, 25.0),
        ),
        source_metadata={"provider": "controlled-fixture", "retrieved_at_utc": None},
    )
    expected = {
        "benchmark_summary.csv",
        "baseline_summary.csv",
        "cost_sweep.csv",
        "inference.csv",
        "mii_regimes.csv",
        "signal_net_returns.csv",
        "baseline_net_returns.csv",
        "input_manifest.json",
        "run_metadata.json",
        "QA_REPORT.md",
        "LIMITATIONS.md",
        "DECISION_MEMO.md",
        "CLAIM_REGISTER.csv",
        "artifact_manifest.json",
    }
    assert expected <= {path.name for path in tmp_path.iterdir()}
    assert bundle.evidence_label == "SYNTHETIC"
    assert len(bundle.benchmark_summary) == 9
    assert "buy_and_hold" in bundle.baseline_summary.index
    assert bundle.input_fingerprint


def test_benchmark_rejects_noncanonical_evidence_label() -> None:
    try:
        BenchmarkConfig(reference_asset="SPY", evidence_label="BACKTESTED")
    except ValueError as error:
        assert "canonical" in str(error)
    else:
        raise AssertionError("noncanonical evidence label should fail")
