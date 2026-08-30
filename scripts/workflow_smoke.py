#!/usr/bin/env python3
"""Deterministic, offline smoke runner for every declared SciXZ workflow.

This runner validates workflow intake and creates an auditable handoff artifact.
It deliberately does not call an LLM, alter a manuscript, query a database, or
produce scientific findings.  Those operations remain dependent on supplied
data, authorized external services, and the relevant runtime Skill.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "registry" / "function_matrix.json"

try:
    from scripts.private_artifact_guard import ensure_private_output_path
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from private_artifact_guard import ensure_private_output_path


ROUTE_REQUIREMENTS = {
    "research-question": ("question", "population", "outcome"),
    "literature-review": ("review_type", "question", "databases", "eligibility"),
    "study-design": ("question", "design", "analysis_unit"),
    "protocol-ethics": ("protocol_title", "study_design", "data_governance"),
    "sample-size": ("outcome", "design", "target_effect", "power"),
    "data-preparation": ("dataset", "analysis_unit", "privacy_constraints"),
    "statistical-analysis": ("analysis_unit", "outcome", "estimand", "design"),
    "manuscript-writing": ("article_type", "outline", "evidence_ledger"),
    "manuscript-review": ("manuscript", "study_type"),
    "reviewer-response": ("editor_decision", "comments", "manuscript"),
    "revision-after-review": ("editor_decision", "comments", "manuscript"),
    "journal-lookup": ("journal",),
    "journal-selection": ("manuscript_fingerprint", "candidates", "external_artifacts"),
    "citation-management": ("citations", "citation_style"),
    "figure-presentation": ("figure_brief", "data_provenance"),
    "project-management": ("project", "deliverables"),
    "capability-absorption": ("source_manifest",),
    "geo-analysis": ("accession_or_topic", "species", "comparison"),
    "scrna-analysis": ("data_format", "sample_identities", "biological_replicates"),
    "multiomics": ("question", "modalities", "sample_matching"),
    "document-operation": ("document", "requested_operation"),
}

RUNTIME_BOUND_ROUTES = {
    "literature-review", "data-preparation", "statistical-analysis", "manuscript-review",
    "reviewer-response", "revision-after-review", "journal-lookup", "journal-selection",
    "citation-management", "figure-presentation", "geo-analysis", "scrna-analysis", "multiomics",
    "document-operation",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def route_names() -> List[str]:
    matrix = load_json(MATRIX_PATH)
    return [item["task"] for item in matrix["functions"]]


def missing_fields(payload: Dict[str, Any], required: Iterable[str]) -> List[str]:
    return [key for key in required if payload.get(key) in (None, "", [], {})]


def _load_preflight(skill: str, script: str):
    candidates = (ROOT / "bundled-skills" / skill / "scripts" / script, ROOT.parent / skill / "scripts" / script)
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location(f"scixz_{skill.replace('-', '_')}", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise RuntimeError(f"Unable to load {skill} preflight from bundled or sibling Skill layouts")


def _load_script(script: str):
    path = ROOT / "scripts" / script
    spec = importlib.util.spec_from_file_location(f"scixz_{Path(script).stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load SciXZ script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _comment_ledger(comments: List[Dict[str, Any]], revision: bool) -> Tuple[List[Dict[str, Any]], List[str]]:
    ledger: List[Dict[str, Any]] = []
    failures: List[str] = []
    for index, comment in enumerate(comments, 1):
        identifier = str(comment.get("id") or f"C-{index}")
        missing = missing_fields(comment, ("text", "severity", "stance"))
        if missing:
            failures.append(f"{identifier}: missing {', '.join(missing)}")
            continue
        action = str(comment.get("action") or "").strip()
        data_needed = bool(comment.get("requires_data"))
        status = "ready"
        if revision and data_needed and not comment.get("data_available"):
            status = "blocked_data"
        elif not action:
            status = "needs_action"
        ledger.append({
            "id": identifier,
            "severity": comment["severity"],
            "stance": comment["stance"],
            "action_status": status,
            "evidence_reference": comment.get("evidence_reference") or None,
            "location_status": "verified" if comment.get("final_location") else "placeholder",
        })
    return ledger, failures


def _route_checks(route: str, payload: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any], List[str], str]:
    required = ROUTE_REQUIREMENTS[route]
    missing = missing_fields(payload, required)
    checks: List[Dict[str, Any]] = [{"name": "required_inputs", "passed": not missing, "detail": missing or "all required inputs supplied"}]
    if missing:
        return "BLOCKED", checks, {}, [f"Missing required intake fields: {', '.join(missing)}."], "Provide the missing inputs before running this route."

    outputs: Dict[str, Any] = {"handoff_type": "validated-plan"}
    limitations: List[str] = []
    status = "COMPLETE"
    next_action = "Hand the validated package to the configured Skill/runtime for the requested operation."

    if route == "literature-review":
        corpus = payload.get("corpus", {})
        full_text = int(corpus.get("full_text_included", 0) or 0)
        abstract_only = int(corpus.get("abstract_only", 0) or 0)
        ready = full_text >= 3 and abstract_only == 0
        level = "review-grade evidence synthesis" if ready else "evidence map/scoping output"
        checks.append({"name": "corpus_readiness", "passed": ready, "detail": {"full_text_included": full_text, "abstract_only": abstract_only}})
        outputs.update({"output_level": level, "corpus_counts": corpus})
        if not ready:
            status = "DIAGNOSTIC"
            limitations.append("Full-text/appraisal coverage is insufficient for a submission-grade synthesis.")
            next_action = "Acquire and appraise eligible full texts, then reconcile screening counts."
    elif route == "data-preparation":
        dataset = payload["dataset"]
        raw_rows = dataset.get("raw_rows", []) if isinstance(dataset, dict) else []
        review_queue = [row for row in raw_rows if not row.get("confirmed", False)]
        checks.append({"name": "raw_values_preserved", "passed": bool(raw_rows), "detail": f"{len(raw_rows)} source rows"})
        outputs.update({"profile": {"declared_rows": dataset.get("rows"), "declared_columns": dataset.get("columns")}, "review_queue": review_queue})
        status = "DIAGNOSTIC"
        limitations.append("No transformation was applied; raw input must be retained until user-approved cleaning.")
        next_action = "Resolve the review queue and approve a versioned cleaning plan."
    elif route == "statistical-analysis":
        assumptions = payload.get("assumptions", [])
        checks.append({"name": "assumptions_declared", "passed": bool(assumptions), "detail": assumptions or "none supplied"})
        plan = payload.get("runtime_plan") or {
            "analysis_unit": payload["analysis_unit"], "outcome": payload["outcome"], "estimand": payload["estimand"], "design": payload["design"],
            "objective": payload.get("objective"), "primary_analysis": payload.get("analysis_plan"), "assumptions": assumptions,
            "missing_data_plan": payload.get("missing_data_plan"), "sensitivity_analyses": payload.get("sensitivity_analyses"),
        }
        preflight = _load_preflight("statistical-analysis", "validate_analysis_plan.py").validate(plan)
        checks.append({"name": "executable_plan_preflight", "passed": preflight["status"] == "READY_FOR_EXECUTION", "detail": preflight["checks"]})
        outputs.update({"estimand": payload["estimand"], "analysis_plan": payload.get("analysis_plan", "plan required before computation"), "preflight": preflight})
        status = "DIAGNOSTIC"
        limitations.append("This is a plan validation only; it contains no effect estimate or inferential result.")
        next_action = "Supply governed data and execute the declared plan with diagnostics and sensitivity analyses."
    elif route == "manuscript-review":
        evidence_locations = payload.get("evidence_locations", [])
        checks.append({"name": "evidence_locations", "passed": bool(evidence_locations), "detail": evidence_locations or "no verifiable locations"})
        outputs.update({
            "review_outline": {"major": payload.get("major_concerns", []), "minor": payload.get("minor_concerns", []), "evidence_locations": evidence_locations},
            "parallel_review_contract": {
                "shared_frozen_input": True,
                "shared_uploaded_pdf_fingerprint": True,
                "companion_evidence_supported": True,
                "branch_evidence_scopes_may_differ": True,
                "branches": {
                    "local_primary_review": "independent",
                    "paperreview_external_signal": "optional-explicit-authorization",
                },
                "fusion_barrier": "both requested branches completed with identical manuscript fingerprints",
                "fusion_owner": "fresh synthesis sub-agent that authored neither branch",
                "formal_output_contract": {
                    "primary_renderer": "scripts/render_editorial_review_docx.py",
                    "structure_profile": "templates/editorial_review_structure_bilingual.json",
                    "languages": ["zh", "en"],
                    "required_sections": [
                        "materials reviewed", "editorial decision", "reviewer panel",
                        "overall assessment and strengths", "P0/P1/P2/P3 findings",
                        "source attribution", "required actions", "acceptance criteria",
                        "adversarial stress test", "author questions", "dimension scores",
                        "revision roadmap",
                    ],
                    "strict_fusion_audit_location": "appendices",
                    "compact_renderer_role": "optional machine-audit attachment only",
                },
                "strict_fusion_checks": [
                    "every local issue id appears in the agreement/disagreement matrix exactly once",
                    "every canonical external PR-xx issue is dispositioned and mapped exactly once",
                    "companion evidence fingerprints and asymmetric branch visibility are disclosed",
                    "repeated provider outputs with identical review-content fingerprints count as one external signal",
                ],
            },
        })
        if payload.get("paperreview_artifact"):
            paperreview = _load_script("paperreview_adapter.py").validate_review_artifact(payload["paperreview_artifact"])
            checks.append({"name": "optional_paperreview_artifact", "passed": paperreview["status"] == "EXTERNAL_SIGNAL_READY_FOR_VERIFICATION", "detail": paperreview})
            outputs["optional_external_review"] = paperreview
            limitations.append("PaperReview.ai is an external advisory signal and cannot replace independent manuscript, reporting, or statistical review.")
        status = "DIAGNOSTIC"
        limitations.append("A formal review requires independent substantive assessment and, where relevant, source data.")
    elif route in {"reviewer-response", "revision-after-review"}:
        ledger, failures = _comment_ledger(payload["comments"], revision=route == "revision-after-review")
        checks.append({"name": "atomic_comment_ledger", "passed": not failures and bool(ledger), "detail": failures or f"{len(ledger)} comments mapped"})
        outputs["comment_ledger"] = ledger
        unresolved = [item["id"] for item in ledger if item["action_status"] != "ready"]
        if failures:
            return "BLOCKED", checks, outputs, ["Invalid comment ledger: " + "; ".join(failures)], "Classify every reviewer comment with severity, stance, and an action."
        status = "DIAGNOSTIC"
        if unresolved:
            limitations.append("Some revision tickets remain unresolved or blocked by unavailable data.")
        limitations.append("No response letter claims a change until final manuscript locations are verified.")
    elif route == "journal-selection":
        artifacts = payload["external_artifacts"]
        required_tools = ("jane", "ipubmed")
        failed = [tool for tool in required_tools if artifacts.get(tool, {}).get("status") != "succeeded"]
        checks.append({"name": "mandatory_external_evidence", "passed": not failed, "detail": failed or "JANE and iPubMed artifacts present"})
        outputs["candidate_count"] = len(payload["candidates"])
        if failed:
            return "BLOCKED", checks, outputs, [f"Final journal ranking requires auditable artifacts for: {', '.join(failed)}."], "Run the missing external evidence branches; do not treat venue scores as acceptance probability."
        status = "DIAGNOSTIC"
        limitations.append("Candidate evidence was validated offline; current scope, metrics, and author guidelines still require live verification.")
    elif route == "citation-management":
        citations = payload["citations"]
        order = [item.get("first_appearance") for item in citations]
        ordered = order == sorted(order) and len(set(order)) == len(order)
        checks.append({"name": "vancouver_first_appearance", "passed": ordered, "detail": order})
        outputs["first_appearance_map"] = [{"key": item.get("key"), "number": item.get("first_appearance")} for item in citations]
        if not ordered:
            return "BLOCKED", checks, outputs, ["Citation first-appearance order is not a unique increasing sequence."], "Resolve citation order before generating the numbered reference list."
        status = "DIAGNOSTIC"
        limitations.append("Metadata and claim support still require canonical-source verification.")
    elif route in {"geo-analysis", "scrna-analysis", "multiomics"}:
        provenance = payload.get("provenance_verified", False)
        checks.append({"name": "input_provenance", "passed": bool(provenance), "detail": "verified" if provenance else "not verified"})
        outputs["analysis_boundary"] = "planning only; no biological result, cell label, DEG, or mechanism is generated"
        if route == "multiomics":
            preflight = _load_preflight("multiomics-analysis", "validate_multiomics_plan.py").validate(payload.get("runtime_plan", {}))
            checks.append({"name": "executable_multiomics_preflight", "passed": preflight["status"] == "READY_FOR_EXECUTION", "detail": preflight["checks"]})
            outputs["preflight"] = preflight
        status = "DIAGNOSTIC"
        limitations.append("Domain analysis requires verified raw/processed data, metadata, and the specified runtime.")
        if not provenance:
            next_action = "Verify dataset provenance and metadata before any biological interpretation."
    elif route == "journal-lookup":
        outputs["lookup_request"] = payload["journal"]
        status = "DIAGNOSTIC"
        limitations.append("Live journal metrics are not queried by this offline smoke test.")
        next_action = "Run journal_lookup.py with a refreshed local index and verify current publisher data."
    elif route == "document-operation":
        status = "DIAGNOSTIC"
        limitations.append("No document was opened or changed by the smoke test.")
    elif route in RUNTIME_BOUND_ROUTES:
        status = "DIAGNOSTIC"
        limitations.append("The route requires a configured domain runtime for substantive execution.")

    return status, checks, outputs, limitations, next_action


def run_route(route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if route not in ROUTE_REQUIREMENTS:
        raise ValueError(f"Unknown SciXZ route: {route}")
    status, checks, outputs, limitations, next_action = _route_checks(route, payload)
    return {
        "route": route,
        "status": status,
        "inputs": {key: payload.get(key) for key in ROUTE_REQUIREMENTS[route]},
        "required_skills": next(item["primary"] for item in load_json(MATRIX_PATH)["functions"] if item["task"] == route),
        "checks": checks,
        "outputs": outputs,
        "limitations": limitations,
        "next_action": next_action,
    }


def load_fixtures(fixtures: Path) -> Dict[str, Dict[str, Any]]:
    fixture_file = fixtures / "routes.json"
    payload = load_json(fixture_file)
    if not isinstance(payload, dict):
        raise ValueError("routes.json must be an object mapping route names to fixture inputs")
    return payload


def run_all(fixtures: Dict[str, Dict[str, Any]], routes: Iterable[str] | None = None) -> Dict[str, Any]:
    names = list(routes or route_names())
    missing = [route for route in names if route not in fixtures]
    if missing:
        raise ValueError(f"Missing fixtures for routes: {', '.join(missing)}")
    artifacts = [run_route(route, fixtures[route]) for route in names]
    counts = {status: sum(artifact["status"] == status for artifact in artifacts) for status in ("COMPLETE", "DIAGNOSTIC", "BLOCKED")}
    all_checks = [check for artifact in artifacts for check in artifact["checks"]]
    passed_checks = sum(bool(check["passed"]) for check in all_checks)
    readiness = round(100 * passed_checks / len(all_checks), 1) if all_checks else 0.0
    return {
        "runner": "scixz-workflow-smoke-v1",
        "offline": True,
        "artifacts": artifacts,
        "summary": {
            "routes": len(artifacts),
            "statuses": counts,
            "checks": {"passed": passed_checks, "total": len(all_checks)},
            "readiness_score": readiness,
            "score_interpretation": "Readiness score is the share of deterministic intake/safety checks passed; it is not a scientific-quality, peer-review, publication, or acceptance score.",
        },
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic offline smoke checks for SciXZ workflows.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--route", choices=route_names())
    group.add_argument("--all", action="store_true")
    parser.add_argument("--fixtures", required=True, help="Directory containing routes.json")
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    fixtures = load_fixtures(Path(args.fixtures))
    report = run_all(fixtures, None if args.all else [args.route])
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            output = ensure_private_output_path(Path(args.output), ROOT)
        except ValueError as exc:
            parser.exit(2, f"workflow smoke blocked: {exc}\n")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["summary"]["statuses"]["BLOCKED"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
