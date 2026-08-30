"""Deterministic contract evaluation for the local SciXZ Skill.

This is a static/contract score, not a claim that an LLM has executed every prompt
successfully. It checks the artifacts that make those behaviors possible and keeps
the rubric reproducible without network access or third-party dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path):
    return json.loads(load_text(path))


def check_all(items):
    return all(items)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    results = []

    def category(name, weight, checks, detail):
        passed = sum(bool(item) for item in checks)
        score = round(weight * passed / len(checks), 2) if checks else 0
        results.append(
            {
                "category": name,
                "weight": weight,
                "passed": passed,
                "total": len(checks),
                "score": score,
                "status": "PASS" if passed == len(checks) else "PARTIAL",
                "detail": detail,
            }
        )

    skill_path = ROOT / "SKILL.md"
    skill = load_text(skill_path)
    frontmatter = skill.split("---", 2)
    category(
        "discoverability and entrypoint",
        10,
        [
            len(frontmatter) >= 3,
            bool(re.search(r"^name:\s*scixz\s*$", frontmatter[1], re.M)),
            bool(re.search(r"^description:\s*.+", frontmatter[1], re.M)),
            "/scixz" in frontmatter[1] and "manuscript" in frontmatter[1],
            "references/manuscript_section_depth.md" in skill,
        ],
        "frontmatter, trigger boundary, and section-depth reference link",
    )

    workflow_files = sorted((ROOT / "workflows").glob("*.md"))
    required_sections = [
        "## Entry and scope",
        "## Inputs",
        "## Route",
        "## Outputs",
        "## Verification",
        "## Failure/fallback",
    ]
    workflow_checks = [
        bool(workflow_files),
        all(all(section in load_text(path) for section in required_sections) for path in workflow_files),
    ]
    matrix = load_json(ROOT / "registry" / "function_matrix.json")
    matrix_checks = [
        all(item.get("status") == "complete" for item in matrix["functions"]),
        all((ROOT / item["workflow"]).exists() for item in matrix["functions"]),
        matrix.get("smoke_test", {}).get("runner") == "scripts/workflow_smoke.py",
        (ROOT / matrix.get("smoke_test", {}).get("runner", "missing")).is_file(),
        (ROOT / matrix.get("smoke_test", {}).get("fixtures", "missing")).is_file(),
    ]
    category(
        "workflow completeness",
        15,
        workflow_checks + matrix_checks,
        f"{len(workflow_files)} workflow files; {len(matrix['functions'])} matrix functions",
    )

    bindings_path = ROOT / "registry" / "scixz_bindings.json"
    catalog_path = ROOT / "registry" / "local_skill_catalog.json"
    if bindings_path.exists() and catalog_path.exists():
        bindings = load_json(bindings_path)["bindings"]
        catalog_doc = load_json(catalog_path)
        catalog_names = {item["name"] for item in catalog_doc["skills"]}
        binding_checks = [
            bool(bindings),
            all(item.get("skill_status") == "installed" for item in bindings),
            all(item.get("binding_state") == "ready" for item in bindings),
            all(Path(item["skill_md"]).exists() for item in bindings),
            all(item["name"] in catalog_names for item in bindings),
            any(item["name"] == "paperconan" and item.get("runtime_status") == "ready" for item in bindings),
            any(item["name"] == "verification" for item in bindings),
            any(item["name"] == "statistical-analysis" for item in bindings),
        ]
        binding_detail = f"{len(bindings)} local allowlisted bindings; catalog count {catalog_doc['logical_skill_count']}"
    else:
        bundled = ROOT / "bundled-skills"
        portable_owners = ("sci-select", "find-journal", "academic-paper", "verify-refs")
        binding_checks = [
            bundled.is_dir(),
            all((bundled / name / "SKILL.md").is_file() for name in portable_owners),
            (ROOT / "scripts" / "journal_selection.py").is_file(),
            (ROOT / "scripts" / "journal_lookup.py").is_file(),
            (ROOT / "scripts" / "verify_corpus_integration.py").is_file(),
        ]
        binding_detail = "portable bundle owners found; local runtime bindings were intentionally not packaged"
    category(
        "skill and runtime availability",
        10,
        binding_checks,
        binding_detail,
    )

    engine = load_text(ROOT / "controller" / "skill_decision_engine.md")
    permission = load_text(ROOT / "controller" / "permission_matrix.md")
    state = load_text(ROOT / "controller" / "state_machine.md")
    protocol = load_text(ROOT / "collaboration" / "protocol.md")
    governance_checks = [
        "skill_missing" in engine and "runtime_missing" in engine,
        "skill_installed=true, runtime_ready=false" in engine,
        "dedupe_key" in permission and "max_hops" in permission,
        "APPROVED_FOR_EXECUTION" in state and "PUBLISHED" in state and "REVISION_REQUIRED" in state,
        "critic" in protocol.lower() and "consensus" in protocol.lower() and "verifier" in protocol.lower(),
    ]
    category(
        "governance and recovery",
        15,
        governance_checks,
        "controller gate, availability distinction, permission matrix, collaboration barriers",
    )

    depth = load_text(ROOT / "references" / "manuscript_section_depth.md")
    writing = load_text(ROOT / "workflows" / "manuscript_writing.md")
    journal_workflow = load_text(ROOT / "workflows" / "journal_selection.md")
    citations = load_text(ROOT / "workflows" / "citation_management.md")
    revision = load_text(ROOT / "workflows" / "revision_after_review.md")
    controller_evals = load_json(ROOT / "evals" / "controller_evals.json")
    writing_evals = load_json(ROOT / "evals" / "manuscript_writing_evals.json")
    depth_checks = [
        "Introduction" in depth and "Discussion" in depth and "Methods" in depth and "Results" in depth,
        "citation_ledger" in depth and "reuse_reason" in depth,
        "finding -> comparison -> explanation -> boundary" in depth,
        "Do not fabricate references" in depth,
        "references/manuscript_section_depth.md" in writing,
        "introduction/discussion" in writing.lower() and "overlap" in citations.lower(),
        "section-depth-and-citation-allocation" in {item["id"] for item in controller_evals["tests"]},
        len(writing_evals["tests"]) >= 5,
        "citation-overlap report" in revision,
    ]
    category(
        "section depth and citation allocation",
        15,
        depth_checks,
        f"{len(writing_evals['tests'])} manuscript-writing adversarial cases",
    )

    external_manifest_path = ROOT / "registry" / "external_tools.json"
    external_manifest = load_json(external_manifest_path)
    external_tools = {item["id"]: item for item in external_manifest["tools"]}
    external_ref = load_text(ROOT / "references" / "external_research_tools.md")
    mandatory_groups = {item["route"]: item for item in external_manifest["mandatory_route_groups"]}
    external_checks = [
        set(external_tools) == {"jane", "ipubmed"},
        all(item.get("mandatory") is True for item in external_tools.values()),
        all(set(item.get("mandatory_routes", [])) >= {"journal-selection", "citation-management"} for item in external_tools.values()),
        set(mandatory_groups["journal-selection"]["required_tools"]) == {"jane", "ipubmed"},
        set(mandatory_groups["citation-management"]["required_tools"]) == {"jane", "ipubmed"},
        set(mandatory_groups["submission-preflight.citation-branch"]["required_tools"]) == {"jane", "ipubmed"},
        external_tools["jane"]["mode"] == "public-url-api" and external_tools["jane"].get("api_documentation"),
        external_tools["ipubmed"]["mode"] == "browser-assisted-shiny" and external_tools["ipubmed"].get("api_documentation") is None,
        all(item.get("routes") and item.get("capabilities") and item.get("input_policy") for item in external_tools.values()),
        "external-signal" in external_ref and "verification" in external_ref.lower(),
        "required external tickets" in journal_workflow.lower() and "jane" in journal_workflow.lower() and "ipubmed" in journal_workflow.lower(),
        "mandatory" in citations.lower() and "jane" in citations.lower() and "ipubmed" in citations.lower() and "verify-refs" in citations,
        "ipubmed" in revision.lower() or "external" in revision.lower(),
        "External websites are not Skills" in engine and "cannot publish" in engine,
        len(load_json(ROOT / "evals" / "external_tool_evals.json")["tests"]) >= 5,
        (ROOT / "scripts" / "journal_selection.py").is_file(),
        "journal_selection.py" in journal_workflow and "decomposed score" in journal_workflow,
    ]
    category(
        "external research-tool adapters",
        20,
        external_checks,
        "JANE/iPubMed evidence gates plus the executable journal-selection report",
    )

    # Existing suites are counted as coverage evidence, not executed behavior.
    suite_files = sorted((ROOT / "evals").glob("*.json"))
    suite_checks = [
        len(suite_files) >= 6,
        all(isinstance(load_json(path), (dict, list)) for path in suite_files),
        len(load_json(ROOT / "evals" / "controller_evals.json")["tests"]) >= 5,
        len(load_json(ROOT / "evals" / "multi_agent_evals.json")["tests"]) >= 4,
        len(load_json(ROOT / "evals" / "submission_preflight_evals.json")["tests"]) >= 5,
    ]
    category(
        "evaluation coverage",
        10,
        suite_checks,
        f"{len(suite_files)} JSON evaluation suites; prompt execution remains an LLM-level follow-up",
    )

    smoke_checks = [
        (ROOT / "scripts" / "workflow_smoke.py").is_file(),
        (ROOT / "tests" / "test_workflow_smoke.py").is_file(),
        (ROOT / "tests" / "fixtures" / "workflow_smoke" / "routes.json").is_file(),
        set(load_json(ROOT / "tests" / "fixtures" / "workflow_smoke" / "routes.json")) >= {item["task"] for item in matrix["functions"]},
        all((ROOT / "bundled-skills" / skill / "SKILL.md").is_file() for item in matrix["functions"] for skill in item["primary"]),
        (ROOT / "scripts" / "paperreview_adapter.py").is_file() and any(item.get("id") == "paperreview-ai" and item.get("mandatory") is False for item in load_json(ROOT / "registry" / "external_review_adapters.json")["tools"]),
        "workflow_smoke.py" in load_text(ROOT / "README.md") and "workflow_smoke.py" in load_text(ROOT / "README.zh-CN.md"),
    ]
    category(
        "runnable workflow smoke coverage",
        5,
        smoke_checks,
        "all matrix routes have deterministic fixtures and typed offline artifacts",
    )

    total = round(sum(item["score"] for item in results), 2)
    payload = {"skill": "scixz", "score": total, "scale": 100, "results": results}
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("SciXZ skill-creator static/contract evaluation")
        for item in results:
            print(
                f"[{item['status']}] {item['category']}: "
                f"{item['score']}/{item['weight']} "
                f"({item['passed']}/{item['total']}) — {item['detail']}"
            )
        print(f"SCORE: {total}/100")
        print("LIMITATION: this score validates local contracts and coverage; it is not a substitute for independent LLM forward execution.")
    return 0 if total == 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())
