import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "workflow_smoke.py"
SPEC = importlib.util.spec_from_file_location("scixz_workflow_smoke", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FIXTURES = ROOT / "tests" / "fixtures" / "workflow_smoke"


def _report():
    return MODULE.run_all(MODULE.load_fixtures(FIXTURES))


def _artifact(route):
    return next(item for item in _report()["artifacts"] if item["route"] == route)


def test_every_declared_route_has_a_runnable_smoke_fixture_and_contract_artifact():
    report = _report()

    assert [item["route"] for item in report["artifacts"]] == MODULE.route_names()
    assert report["summary"]["routes"] == 21
    assert report["summary"]["statuses"]["BLOCKED"] == 0
    assert report["summary"]["checks"]["total"] > 21
    assert 0 < report["summary"]["readiness_score"] < 100
    for artifact in report["artifacts"]:
        assert set(artifact) == {"route", "status", "inputs", "required_skills", "checks", "outputs", "limitations", "next_action"}
        assert artifact["status"] in {"COMPLETE", "DIAGNOSTIC"}
        assert artifact["checks"]
        assert all((ROOT / "bundled-skills" / skill / "SKILL.md").is_file() for skill in artifact["required_skills"])


def test_peer_review_and_revision_keep_evidence_locations_and_unresolved_tickets_explicit():
    review = _artifact("manuscript-review")
    revision = _artifact("revision-after-review")

    assert review["status"] == "DIAGNOSTIC"
    assert review["outputs"]["review_outline"]["evidence_locations"]
    assert review["outputs"]["optional_external_review"]["status"] == "EXTERNAL_SIGNAL_READY_FOR_VERIFICATION"
    assert any("external advisory signal" in item for item in review["limitations"])
    assert any(item["action_status"] == "blocked_data" for item in revision["outputs"]["comment_ledger"])
    assert any("No response letter claims" in item for item in revision["limitations"])


def test_literature_and_data_routes_downgrade_or_preserve_uncertainty():
    literature = _artifact("literature-review")
    data_prep = _artifact("data-preparation")

    assert literature["outputs"]["output_level"] == "evidence map/scoping output"
    assert literature["status"] == "DIAGNOSTIC"
    assert data_prep["outputs"]["review_queue"][0]["value"] == "?"
    assert data_prep["status"] == "DIAGNOSTIC"


def test_statistics_and_omics_are_plan_only_without_results():
    stats = _artifact("statistical-analysis")

    assert stats["outputs"]["estimand"] == "risk difference at 30 days"
    assert stats["outputs"]["preflight"]["status"] == "READY_FOR_EXECUTION"
    for route in ("geo-analysis", "scrna-analysis", "multiomics"):
        artifact = _artifact(route)
        assert artifact["status"] == "DIAGNOSTIC"
        assert "no biological result" in artifact["outputs"]["analysis_boundary"]
    assert _artifact("multiomics")["outputs"]["preflight"]["status"] == "READY_FOR_EXECUTION"


def test_missing_or_invalid_inputs_block_instead_of_claiming_completion():
    blocked = MODULE.run_route("statistical-analysis", {"analysis_unit": "participant", "outcome": "binary"})
    bad_citations = MODULE.run_route("citation-management", {"citation_style": "Vancouver", "citations": [{"key": "a", "first_appearance": 2}, {"key": "b", "first_appearance": 1}]})

    assert blocked["status"] == "BLOCKED"
    assert bad_citations["status"] == "BLOCKED"


def test_cli_writes_machine_readable_full_report(tmp_path):
    output = tmp_path / "workflow-smoke.json"

    assert MODULE.main(["--all", "--fixtures", str(FIXTURES), "--output", str(output)]) == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["routes"] == len(MODULE.route_names())
    assert report["summary"]["score_interpretation"].startswith("Readiness score")
