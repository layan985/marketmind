import hashlib
import json

import pytest

from marketmind.audit import run_research_audit


def test_research_audit_writes_self_verifying_evidence_pack(tmp_path) -> None:
    result = run_research_audit(
        tmp_path / "audit",
        periods=640,
        assets=4,
        seed=94,
        window=64,
        step=16,
    )
    assert result.passed
    assert len(result.checks) == 7
    assert (tmp_path / "audit" / "AUDIT.md").exists()
    payload = json.loads((tmp_path / "audit" / "audit.json").read_text())
    assert payload["summary"] == {"passed": 7, "total": 7}
    manifest = json.loads((tmp_path / "audit" / "manifest.json").read_text())
    for name, record in manifest["artifacts"].items():
        path = tmp_path / "audit" / name
        assert path.stat().st_size == record["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]


def test_research_audit_validates_scope() -> None:
    with pytest.raises(ValueError):
        run_research_audit("unused", periods=300, window=252)
    with pytest.raises(ValueError):
        run_research_audit("unused", periods=700, assets=3, window=252)
