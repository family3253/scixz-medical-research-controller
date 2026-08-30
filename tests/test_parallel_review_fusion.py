import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "build_parallel_review_fusion_bundle.py"
SPEC = importlib.util.spec_from_file_location("scixz_parallel_review_fusion", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _primary(fingerprint="sha256:test"):
    return {
        "schema": "scixz-local-primary-review-v1",
        "status": "COMPLETED",
        "branch_id": "local-primary-review",
        "manuscript": {"file_name": "paper.pdf", "fingerprint": fingerprint},
        "review": {"decision": "Major revision", "major_concerns": [{"id": "M1"}]},
    }


def _external(fingerprint="sha256:test"):
    return {
        "schema": "scixz-paperreview-synthesis-bundle-v1",
        "status": "READY_FOR_SCIXZ_FINAL_REVIEW",
        "manuscript": {"file_name": "paper.pdf", "fingerprint": fingerprint},
        "external_signal": {"tool": "paperreview-ai", "issue_ledger": {"issue_count": 1, "issues": [{"id": "PR-01", "text": "Concern"}]}},
    }


def test_fusion_requires_two_completed_branches_and_creates_fresh_agent_barrier():
    bundle = MODULE.build_bundle(_primary(), _external())

    assert bundle["schema"] == "scixz-parallel-review-fusion-bundle-v2"
    assert bundle["status"] == "READY_FOR_FRESH_SYNTHESIS_AGENT"
    assert bundle["barrier"]["synthesis_may_start"] is True
    contract = bundle["fresh_synthesis_agent_contract"]
    assert "did not author" in contract["separation"]
    assert any("agreement/disagreement" in step for step in contract["required_steps"])
    assert any("majority" in rule for rule in contract["prohibited"])
    assert bundle["barrier"]["external_issue_ids_requiring_disposition"] == ["PR-01"]
    assert bundle["barrier"]["local_issue_ids_requiring_matrix_mapping"] == ["M1"]


def test_fusion_blocks_mismatched_frozen_manuscripts():
    with pytest.raises(ValueError, match="same frozen manuscript"):
        MODULE.build_bundle(_primary("sha256:one"), _external("sha256:two"))


def test_fusion_blocks_incomplete_or_empty_primary_review():
    incomplete = _primary()
    incomplete["status"] = "PENDING"
    with pytest.raises(ValueError, match="not completed"):
        MODULE.build_bundle(incomplete, _external())

    empty = _primary()
    empty["review"] = {}
    with pytest.raises(ValueError, match="substantive review"):
        MODULE.build_bundle(empty, _external())


def test_fusion_blocks_missing_or_duplicate_external_issue_ids():
    missing = _external()
    missing["external_signal"]["issue_ledger"]["issues"] = []
    with pytest.raises(ValueError, match="canonical external issue ledger"):
        MODULE.build_bundle(_primary(), missing)

    duplicate = _external()
    duplicate["external_signal"]["issue_ledger"] = {"issue_count": 2, "issues": [{"id": "PR-01"}, {"id": "PR-01"}]}
    with pytest.raises(ValueError, match="duplicate"):
        MODULE.build_bundle(_primary(), duplicate)


def test_fusion_records_asymmetric_companion_evidence_scope():
    companion = {"file_name": "tables.docx", "path": "C:/private/tables.docx", "fingerprint": "sha256:tables", "available_to": ["local-primary-review", "fresh-synthesis-agent"], "not_available_to": ["paperreview-ai"]}

    bundle = MODULE.build_bundle(_primary(), _external(), [companion])

    assert bundle["evidence_manifest"]["branch_scopes_identical"] is False
    assert bundle["final_review_contract"]["requires_evidence_scope_disclosure"] is True
    assert bundle["final_review_contract"]["companion_evidence_fingerprints"] == ["sha256:tables"]
