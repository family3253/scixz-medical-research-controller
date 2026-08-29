from __future__ import annotations

import argparse
import csv
from pathlib import Path

from review_project_schema import (
    ABSTRACT_SCREEN_HEADERS,
    CANDIDATE_HEADERS,
    EVIDENCE_HEADERS,
    FULLTEXT_ACQUISITION_HEADERS,
    FULLTEXT_REVIEW_HEADERS,
    FULLTEXT_SCREEN_HEADERS,
    PROJECT_DEFAULT_PATHS,
)


STAGE_DIRS = [
    "00_topic_definition",
    "01_search_strategy",
    "02_candidate_pool_and_screening",
    "03_fulltext_acquisition_and_review",
    "04_evidence_extraction",
    "05_writing_and_figure_planning",
    "06_claim_mapping_and_outline",
    "07_draft",
    "08_revision_and_final_checks",
]


def write_csv(path: Path, headers: list[str], force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize a traceable review-writing project scaffold."
    )
    parser.add_argument("output_dir")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path(args.output_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for dirname in STAGE_DIRS:
        (root / dirname).mkdir(parents=True, exist_ok=True)

    write_text(
        root / "00_topic_definition" / "topic_definition.md",
        "# Topic Definition\n\n- Working title:\n- Research question:\n- Target output:\n- Review type:\n- Field/subfield:\n- Why this topic matters:\n- What would count as enough evidence:\n",
        args.force,
    )
    write_text(
        root / "01_search_strategy" / "search_strategy.md",
        "# Search Strategy\n\n- Topic:\n- Target output:\n- Concept groups:\n- Query variants:\n- Database/source plan:\n- Provider and access-mode plan:\n- Institution filters / thesis scope if relevant:\n- Filters:\n- Expected limitations and access risks:\n",
        args.force,
    )
    write_text(
        root / "05_writing_and_figure_planning" / "figure_plan.md",
        "# Figure / Table Plan\n\n| ID | Type | Purpose | Source artifact | Notes |\n|---|---|---|---|---|\n",
        args.force,
    )
    write_text(
        root / "05_writing_and_figure_planning" / "visual_evidence_pack.md",
        "# Visual Evidence Pack\n\n- Screening counts:\n- Topic clusters:\n- Candidate comparative tables:\n- Figure opportunities:\n- Evidence gaps:\n",
        args.force,
    )
    write_text(
        root / "06_claim_mapping_and_outline" / "claim_mapping.md",
        "# Claim Mapping\n\n| Claim | Supporting citations | Evidence strength | Counterevidence | Destination section |\n|---|---|---|---|---|\n",
        args.force,
    )
    write_text(
        root / "06_claim_mapping_and_outline" / "outline.md",
        "# Writing Outline\n\n## Proposed structure\n\n## Section jobs\n\n## Missing evidence by section\n",
        args.force,
    )
    write_text(
        root / "decision_packet.md",
        "# Debate Packet\n\n## Decision Context\n\n## Evidence Snapshot\n\n## Claims in Play\n\n## Debate Question\n\nShould the project PROCEED, REFINE, or PIVOT before writing?\n",
        args.force,
    )
    write_text(
        root / "proceed_case.md",
        "# Proceed Case\n\n- recommendation: PROCEED\n- strongest_support:\n  -\n- allowed_claim_scope:\n  -\n- residual_risks:\n  -\n",
        args.force,
    )
    write_text(
        root / "refine_case.md",
        "# Refine Case\n\n- recommendation: REFINE\n- blocking_weaknesses:\n  -\n- minimum_upgrades_needed:\n  -\n- why_not_pivot:\n  -\n",
        args.force,
    )
    write_text(
        root / "pivot_case.md",
        "# Pivot Case\n\n- recommendation: PIVOT\n- strongest_counterargument:\n  -\n- critical_issues:\n  -\n- alternative_direction:\n  -\n",
        args.force,
    )
    write_text(
        root / "decision_record.md",
        "# Decision Record\n\n- final_decision:\n- confidence:\n- rationale:\n- consensus_points:\n  -\n- disagreement_points:\n  -\n- required_next_actions:\n  -\n- blocks_handoff:\n",
        args.force,
    )
    write_text(
        root / "sentinel_watch_report.md",
        "# Sentinel Watch Report\n\n- status:\n- blocking_inconsistencies:\n  -\n- warnings:\n  -\n- required_fixes:\n  -\n- handoff_allowed:\n",
        args.force,
    )
    write_text(
        root / "citation_authenticity_report.md",
        "# Citation Authenticity Report\n\n## Summary\n\n- total_citations:\n- proceed_count:\n- refine_count:\n- pivot_count:\n\n## Four-Layer Verification Table\n\n| Citation ID | Identity | Source Status | Claim Support | Manuscript Binding | Decision | Notes |\n|---|---|---|---|---|---|---|\n\n## Blocking Risks\n\n-\n\n## Required Fixes\n\n-\n",
        args.force,
    )
    write_text(
        root / "lessons_memory.md",
        "# Lessons Memory\n\n## Entry\n\n- logged_at:\n- stage:\n- severity:\n- pattern_key:\n- lesson:\n- suggested_fix:\n- recurrence_count:\n- first_seen:\n- last_seen:\n- decay_window_days: 30\n",
        args.force,
    )
    write_text(
        root / "session_manifest.md",
        "# Session Manifest\n\n- session_id:\n- project_goal:\n- review_type:\n- source_plan:\n- current_stage: retrieval\n- upstream_artifacts:\n  - candidate_pool: 02_candidate_pool_and_screening/candidate_pool.csv\n  - title_abstract_screening: 02_candidate_pool_and_screening/title_abstract_screening.csv\n  - fulltext_screening: 03_fulltext_acquisition_and_review/fulltext_screening.csv\n  - evidence_extraction: 04_evidence_extraction/evidence_extraction.csv\n  - figure_plan: 05_writing_and_figure_planning/figure_plan.md\n  - visual_evidence_pack: 05_writing_and_figure_planning/visual_evidence_pack.md\n- downstream_targets:\n  - outline: 06_claim_mapping_and_outline/outline.md\n  - draft_sections:\n  - claim_mapping: 06_claim_mapping_and_outline/claim_mapping.md\n  - decision_record: decision_record.md\n  - gate_report: 08_revision_and_final_checks/gate_report.md\n- memory_artifacts:\n  - sentinel_watch_report: sentinel_watch_report.md\n  - lessons_memory: lessons_memory.md\n- verification_artifacts:\n  - citation_authenticity_report: citation_authenticity_report.md\n- notes:\n",
        args.force,
    )

    write_csv(
        root / PROJECT_DEFAULT_PATHS["candidate_csv"], CANDIDATE_HEADERS, args.force
    )
    write_csv(
        root / PROJECT_DEFAULT_PATHS["abstract_screen_csv"],
        ABSTRACT_SCREEN_HEADERS,
        args.force,
    )
    write_csv(
        root / PROJECT_DEFAULT_PATHS["fulltext_acquisition_csv"],
        FULLTEXT_ACQUISITION_HEADERS,
        args.force,
    )
    write_csv(
        root / PROJECT_DEFAULT_PATHS["fulltext_screen_csv"],
        FULLTEXT_SCREEN_HEADERS,
        args.force,
    )
    write_csv(
        root / PROJECT_DEFAULT_PATHS["fulltext_review_csv"],
        FULLTEXT_REVIEW_HEADERS,
        args.force,
    )
    write_csv(
        root / PROJECT_DEFAULT_PATHS["evidence_csv"], EVIDENCE_HEADERS, args.force
    )

    write_text(
        root / "08_revision_and_final_checks" / "gate_report.md",
        "# Gate Report\n\nRun `generate_gate_report.py` after populating the project tables.\n",
        args.force,
    )

    print(f"[ok] initialized review project: {root}")


if __name__ == "__main__":
    main()
