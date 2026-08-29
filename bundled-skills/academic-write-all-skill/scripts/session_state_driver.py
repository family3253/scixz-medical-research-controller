from __future__ import annotations

import argparse
from pathlib import Path

from review_project_schema import PROJECT_DEFAULT_PATHS


STAGE_ORDER = [
    "retrieval",
    "screening",
    "evidence_extraction",
    "decision_loop",
    "writing",
    "final_gate",
]

STAGE_REQUIREMENTS = {
    "retrieval": [
        "00_topic_definition/topic_definition.md",
        "01_search_strategy/search_strategy.md",
        PROJECT_DEFAULT_PATHS["candidate_csv"],
        "session_manifest.md",
    ],
    "screening": [
        PROJECT_DEFAULT_PATHS["candidate_csv"],
        PROJECT_DEFAULT_PATHS["abstract_screen_csv"],
        PROJECT_DEFAULT_PATHS["fulltext_screen_csv"],
    ],
    "evidence_extraction": [
        PROJECT_DEFAULT_PATHS["fulltext_screen_csv"],
        PROJECT_DEFAULT_PATHS["fulltext_review_csv"],
        PROJECT_DEFAULT_PATHS["evidence_csv"],
        "06_claim_mapping_and_outline/claim_mapping.md",
    ],
    "writing": [
        PROJECT_DEFAULT_PATHS["evidence_csv"],
        "06_claim_mapping_and_outline/claim_mapping.md",
        "06_claim_mapping_and_outline/outline.md",
        "proceed_case.md",
        "refine_case.md",
        "pivot_case.md",
        "decision_record.md",
    ],
    "decision_loop": [
        PROJECT_DEFAULT_PATHS["evidence_csv"],
        "06_claim_mapping_and_outline/claim_mapping.md",
        "08_revision_and_final_checks/gate_report.md",
        "decision_packet.md",
    ],
    "final_gate": [
        "08_revision_and_final_checks/gate_report.md",
        "deliverables_manifest.md",
        "sentinel_watch_report.md",
        "citation_authenticity_report.md",
    ],
}

STAGE_OWNERS = {
    "retrieval": "awas-retrieval-orchestrator",
    "screening": "awas-screening-analyst",
    "evidence_extraction": "awas-evidence-extractor",
    "decision_loop": "awas-decision-synthesizer",
    "writing": "awas-writing-coordinator",
    "final_gate": "awas-sentinel-watchdog",
}


def parse_manifest(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        body = line[1:].strip()
        if ":" not in body:
            continue
        key, value = body.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def format_manifest(manifest: dict[str, str]) -> str:
    upstream = {
        "candidate_pool": manifest.get(
            "candidate_pool", "02_candidate_pool_and_screening/candidate_pool.csv"
        ),
        "title_abstract_screening": manifest.get(
            "title_abstract_screening",
            "02_candidate_pool_and_screening/title_abstract_screening.csv",
        ),
        "fulltext_screening": manifest.get(
            "fulltext_screening",
            "03_fulltext_acquisition_and_review/fulltext_screening.csv",
        ),
        "evidence_extraction": manifest.get(
            "evidence_extraction", "04_evidence_extraction/evidence_extraction.csv"
        ),
        "figure_plan": manifest.get(
            "figure_plan", "05_writing_and_figure_planning/figure_plan.md"
        ),
        "visual_evidence_pack": manifest.get(
            "visual_evidence_pack",
            "05_writing_and_figure_planning/visual_evidence_pack.md",
        ),
    }
    downstream = {
        "outline": manifest.get("outline", "06_claim_mapping_and_outline/outline.md"),
        "draft_sections": manifest.get("draft_sections", ""),
        "claim_mapping": manifest.get(
            "claim_mapping", "06_claim_mapping_and_outline/claim_mapping.md"
        ),
        "decision_record": manifest.get("decision_record", "decision_record.md"),
        "gate_report": manifest.get(
            "gate_report", "08_revision_and_final_checks/gate_report.md"
        ),
    }
    memory_artifacts = {
        "sentinel_watch_report": manifest.get(
            "sentinel_watch_report", "sentinel_watch_report.md"
        ),
        "lessons_memory": manifest.get("lessons_memory", "lessons_memory.md"),
    }
    verification_artifacts = {
        "citation_authenticity_report": manifest.get(
            "citation_authenticity_report", "citation_authenticity_report.md"
        ),
    }
    lines = [
        "# Session Manifest",
        "",
        f"- session_id: {manifest.get('session_id', '')}",
        f"- project_goal: {manifest.get('project_goal', '')}",
        f"- review_type: {manifest.get('review_type', '')}",
        f"- source_plan: {manifest.get('source_plan', '')}",
        f"- current_stage: {manifest.get('current_stage', 'retrieval')}",
        "- upstream_artifacts:",
        f"  - candidate_pool: {upstream['candidate_pool']}",
        f"  - title_abstract_screening: {upstream['title_abstract_screening']}",
        f"  - fulltext_screening: {upstream['fulltext_screening']}",
        f"  - evidence_extraction: {upstream['evidence_extraction']}",
        f"  - figure_plan: {upstream['figure_plan']}",
        f"  - visual_evidence_pack: {upstream['visual_evidence_pack']}",
        "- downstream_targets:",
        f"  - outline: {downstream['outline']}",
        f"  - draft_sections: {downstream['draft_sections']}",
        f"  - claim_mapping: {downstream['claim_mapping']}",
        f"  - decision_record: {downstream['decision_record']}",
        f"  - gate_report: {downstream['gate_report']}",
        "- memory_artifacts:",
        f"  - sentinel_watch_report: {memory_artifacts['sentinel_watch_report']}",
        f"  - lessons_memory: {memory_artifacts['lessons_memory']}",
        "- verification_artifacts:",
        f"  - citation_authenticity_report: {verification_artifacts['citation_authenticity_report']}",
        f"- notes: {manifest.get('notes', '')}",
        "",
    ]
    return "\n".join(lines)


def update_manifest(path: Path, updates: dict[str, str]) -> None:
    manifest = parse_manifest(path)
    manifest.update(updates)
    path.write_text(format_manifest(manifest), encoding="utf-8")


def stage_missing_files(root: Path, stage: str) -> list[str]:
    missing = []
    for relative in STAGE_REQUIREMENTS.get(stage, []):
        target = root / relative
        if not target.exists():
            missing.append(relative)
    return missing


def detect_current_stage(manifest: dict[str, str]) -> str:
    stage = manifest.get("current_stage", "").strip()
    return stage if stage in STAGE_ORDER else "retrieval"


def next_stage(current: str) -> str | None:
    if current not in STAGE_ORDER:
        return "retrieval"
    idx = STAGE_ORDER.index(current)
    return STAGE_ORDER[idx + 1] if idx + 1 < len(STAGE_ORDER) else None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Drive staged AWAS multi-agent workflow from session manifest."
    )
    parser.add_argument("project_dir")
    parser.add_argument(
        "--advance",
        action="store_true",
        help="Advance to next stage if current stage requirements are satisfied",
    )
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    manifest_path = root / "session_manifest.md"
    if not manifest_path.exists():
        raise SystemExit(f"Missing session manifest: {manifest_path}")

    manifest = parse_manifest(manifest_path)
    current = detect_current_stage(manifest)
    missing = stage_missing_files(root, current)

    print(f"CURRENT_STAGE: {current}")
    print(f"CURRENT_OWNER: {STAGE_OWNERS[current]}")
    if missing:
        print("STATUS: blocked")
        print("MISSING_FILES:")
        for item in missing:
            print(f"- {item}")
        return

    print("STATUS: ready")
    if not args.advance:
        print(
            "NEXT_ACTION: use --advance to move forward once you accept the current stage"
        )
        return

    next_value = next_stage(current)
    if next_value is None:
        print("NEXT_STAGE: complete")
        update_manifest(manifest_path, {"current_stage": "complete"})
        return

    update_manifest(manifest_path, {"current_stage": next_value})
    print(f"NEXT_STAGE: {next_value}")
    print(f"NEXT_OWNER: {STAGE_OWNERS[next_value]}")


if __name__ == "__main__":
    main()
