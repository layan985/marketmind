"""Repository-level tests for MarketMind's public evidence and client-assurance contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_LABELS = {
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

LEGACY_OR_AMBIGUOUS_BADGES = {
    "EXTERNALLY VERIFIED",
    "FOUNDER PRODUCED",
    "INTERNAL VALIDATION",
    "VERIFIED",
    "VALIDATED",
}


def test_proof_ledger_declares_every_canonical_evidence_label() -> None:
    ledger = (ROOT / "PROOF_LEDGER.md").read_text(encoding="utf-8")
    for label in CANONICAL_LABELS:
        assert f"`{label}`" in ledger, f"missing canonical evidence label: {label}"


def test_proof_ledger_does_not_introduce_ambiguous_badges() -> None:
    ledger = (ROOT / "PROOF_LEDGER.md").read_text(encoding="utf-8")
    for badge in LEGACY_OR_AMBIGUOUS_BADGES:
        assert f"`{badge}`" not in ledger, f"ambiguous evidence badge detected: {badge}"


def test_buyer_room_exposes_assurance_and_risk_controls() -> None:
    buyer_room = (ROOT / "BUYER_ROOM_INDEX.md").read_text(encoding="utf-8")
    required_links = {
        "CLIENT_ASSURANCE_PROTOCOL.md",
        "CLIENT_DELIVERY_CHECKLIST.md",
        "MODEL_RISK_REGISTER.md",
        "PROOF_LEDGER.md",
        "REPRODUCIBILITY.md",
        "REPLICATION_CHALLENGE.md",
    }
    for link in required_links:
        assert link in buyer_room, f"buyer room is missing {link}"


def test_assurance_protocol_preserves_evidence_escalation_boundary() -> None:
    protocol = (ROOT / "CLIENT_ASSURANCE_PROTOCOL.md").read_text(encoding="utf-8")
    ordered_levels = [
        "implementation invariant",
        "controlled known-structure synthetic recovery",
        "real public-data execution",
        "external methodological/code review",
        "independent reproduction",
        "production-client evidence",
        "prospective confirmatory result",
    ]
    positions = [protocol.index(level) for level in ordered_levels]
    assert positions == sorted(positions)
    assert "Passing one level does not silently grant the next." in protocol


def test_client_checklist_contains_blocking_integrity_controls() -> None:
    checklist = (ROOT / "CLIENT_DELIVERY_CHECKLIST.md").read_text(encoding="utf-8")
    required_controls = {
        "Input dataset fingerprint",
        "Feature future-invariance test",
        "Multiple-testing correction",
        "Synthetic evidence is not described as real-market validation",
        "Manifest integrity has been verified",
        "Critical risks are resolved",
    }
    for control in required_controls:
        assert control in checklist, f"client checklist is missing blocking control: {control}"
